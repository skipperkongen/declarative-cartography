from constraints import cellbound, proximity, allornothing 
import solvers
import templates
from constraints import Constraint
from query import Query,WILDCARD

import imp
import re
import sys, os
import pdb

class CvlToSqlCompiler(object):
	"""Compiler that turns CVL into a single transaction in SQL"""
	def __init__( self, **options ):
		super( CvlToSqlCompiler, self ).__init__()
		self.options = options
	
	def _load_constraints( self, query ):
		constraints = []
		constraints_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'constraints')
		
		for constraint in query.subject_to:
			name = constraint[0]
			params = list(constraint[1:])
			module_name = 'constraints.%s' % name
			module_file = '%s/%s.py' % (constraints_dir, name)
			#pdb.set_trace()
			mod = imp.load_source( module_name, module_file )
			constraints.append(
				Constraint(name, query, mod.SET_UP, mod.FIND_CONFLICTS, mod.CLEAN_UP, *params)
			)
		return constraints
	
	def compile( self, query, templates=templates.pgtemplates, optimizer=solvers.pgsolvers.HittingSetHeuristic ):
		# initialize empty SQL transaction tx
		constraints = self._load_constraints( query )
		tx = TransactionBuilder( query, templates, optimizer, *constraints )
		# preample
		tx.BeginTx()
		tx.AddInfo()
		tx.AddFramework()
		tx.InitializeOutput() 
		tx.MergePartitions() # MERGE PARTITIONS
		if self.options.get('export', ''):
			tx.CreateExportTable( self.options['export'] ) # export hitting set for later analysis
		# main loop: bottom up
		for z in reversed(range( query.zoomlevels )):
			tx.BigComment( 'Creating zoom-level %d' % z )
			tx.CopyLevel( z + 1, z )
			tx.InitializeLevel( z ) # create _conflict table
			# FORCE LEVEL
			tx.ForceLevel( z ) 
			# SUBJECT TO
			tx.FindConflicts( z ) # find conflicts
			tx.FindHittingSet( z ) #  create hitting set
			if self.options.get('export', ''):
				tx.Export( z ) # export hitting set for later analysis
			tx.DeleteHittingSet( z ) 
			# TRANSFORM: allornothing, simplify_level
			tx.LevelTransforms( z ) 
			tx.CleanLevel( z )
		# finalize
		tx.SimplifyAll() # TRANSFORM: simplify_once
		tx.RemoveFramework()
		tx.CommitTx()
		tx.TryThis()
		return tx.get_sql()
							
class TransactionBuilder(object):
	"""docstring for Transaction"""
	def __init__( self, query, templates, optimizer, *constraints ):
		super(TransactionBuilder, self).__init__()
		self._query = query
		self._formatter = query.__dict__
		self._templates = templates
		self._optimizer = optimizer()
		self._constraints = constraints
		self.tx = []

	def BeginTx( self ):
		self.tx.append( self._templates.BEGIN_TX.format( **self._formatter ) )

	def CommitTx( self ):
		self.tx.append( self._templates.COMMIT_TX.format( **self._formatter ) )
	
	def AddInfo( self ):
		self.tx.append( self._templates.ADD_INFO.format( **self._formatter ) )
	
	def AddFramework( self ):
		self.Comment( 'Adding CVL generalization framework' )
		self.tx.append( self._templates.ADD_FRAMEWORK.format( **self._formatter ))
	
	def RemoveFramework( self ):
		self.Comment( 'Removing CVL generalization framework' )
		self.tx.append( self._templates.REMOVE_FRAMEWORK.format( **self._formatter ))

	def InitializeOutput( self ):
		self.Comment( 'Initializing output' )
		self.tx.append( self._templates.INITIALIZE_OUTPUT.format( **self._formatter ))
			
	def MergePartitions( self ):
		self.Comment( 'Merging partitions' )
		_tx = []
		merged = []
		has_merge_wildcard = False
		add_quotes = re.compile(r'(.*)')
		for merge in filter(lambda x: x[0] is not WILDCARD, self._query.merge_partitions):
			self._formatter['before_merge'] = ', '.join(map(lambda x: add_quotes.sub(r"'\1'", x), merge[0]))
			self._formatter['after_merge'] = merge[1]
			
			_tx.append( self._templates.MERGE_PARTITIONS.format( **self._formatter ))

			merged.append( merge[1] )
		for merge in filter(lambda x: x[0] is WILDCARD, self._query.merge_partitions):
			self._formatter['merged'] = ', '.join(map(lambda x: add_quotes.sub(r"'\1'", x), merged))
			self._formatter['after_merge'] = merge[1]

			_tx.append( self._templates.MERGE_PARTITIONS_REST.format( **self._formatter ))
		
		self.tx.extend(_tx)
	
	def CopyLevel( self, from_z, to_z ):
		self.Comment( 'Copy data from level %d to level %d' % (from_z, to_z) )
		self._formatter['from_z'] = from_z
		self._formatter['to_z'] = to_z
		self.tx.append( self._templates.COPY_LEVEL.format( **self._formatter ) )
	
	def InitializeLevel( self, z ):
		self.Comment( 'Initialization for level %d' % z )
		self._formatter['current_z'] = z
		
		self.tx.append( self._templates.INITIALIZE_LEVEL.format( **self._formatter ) )

	def ForceLevel(self, z ):
		# FORCE LEVEL
		for force_delete in filter(lambda x: x[1] == z+1, self._query.force_level):
			self.Comment( 'Force delete records' )
			self._formatter['delete_partition'] = "'%s'" % force_delete[0]
			self.tx.append( self._templates.FORCE_LEVEL.format( **self._formatter ) )
		
	def FindConflicts( self, z ):
		self._formatter['ignored_partitions'] = ', '.join(map(lambda x: ("'%s'" % x[0]), self._query.force_level))
		# find conflicts
		for constraint in self._constraints:
			self.Comment( 'Find conflicts' )
			self.tx.extend( constraint.set_up( z ) )
			self._formatter['constraint_select'] = constraint.find_conflicts( z )
			if self._formatter['ignored_partitions'] == '':
				self.tx.extend( self._templates.FIND_CONFLICTS.format( **self._formatter ) )
			else:
				self.tx.extend( self._templates.FIND_CONFLICTS_IGNORE.format( **self._formatter ) )
			self.tx.extend( constraint.clean_up( z ) )
	
	def FindHittingSet( self, z ):
		self._formatter['hittings_set_solution'] = ''.join(self._optimizer.get_solver( self._query ))
		# resolve conflicts
		self.Comment( 'Find hitting set' )
		self.tx.append( self._templates.FIND_HITTING_SET.format( **self._formatter ) )
	
	def DeleteHittingSet( self, z ):
		self.Comment( 'Delete hitting set' )
		self.tx.append( self._templates.DELETE_HITTING_SET.format( **self._formatter ) )
	
	def CreateExportTable( self, export_table ):
		self.Comment( 'Creating export table')
		self._formatter['export_table'] = export_table
		self.tx.append( self._templates.CREATE_EXPORT_TABLE.format ( **self._formatter ))
	
	def Export( self, z ):
		self.Comment( 'Exporting conflicts' )
		self.tx.append( self._templates.EXPORT.format( **self._formatter ))
	
	def LevelTransforms( self, z ):
		if 'allornothing' in self._query.transform_by:
			self.Comment( 'Apply all-or-nothing' )
			self.tx.append( self._templates.ALLORNOTHING.format( **self._formatter ) )
		if 'simplify' in self._query.transform_by:
			self.Comment( 'Simplifying level' )
			self.tx.append( self._templates.SIMPLIFY.format( **self._formatter ) )
			
	def CleanLevel( self, z ):
		self.Comment( 'Clean-up for level %d' % z )
		self.tx.append( self._templates.CLEAN_LEVEL.format( **self._formatter ) )

	def SimplifyAll( self ):
		self.Comment( 'Simplifying output' )
		if 'simplify_once' in self._query.transform_by:
			self.tx.append( self._templates.SIMPLIFY_ALL.format( **self._formatter ) )
	
	def TryThis( self ):
		self.Comment( 'Something you can try')
		self.tx.append( self._templates.TRYTHIS.format( **self._formatter) )
	
	def Comment( self, comment ):
		self.tx.append( self._templates.COMMENT.format(comment=comment) )
	
	def BigComment( self, comment ):
		self.tx.append( self._templates.BIG_COMMENT.format(comment=comment) )
	
	def get_sql( self ):
		return "".join( self.tx )
		
if __name__ == '__main__':
	print 'try example1.py in the root directory'
		
		


		
		