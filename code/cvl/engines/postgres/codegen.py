__author__ = 'kostas'

import re
import imp
import os

from cvl.framework.query import WILDCARD
from cvl.engines.postgres.sql import *


class CodeGenerator(object):
    """docstring for Transaction"""

    def __init__(self, **options):
        super(CodeGenerator, self).__init__()
        self.options = options
        self.code = []

    def set_query(self, query):
        self.query = query
        self.constraints = self._load_constraints()

    def _load_constraints(self):
        constraints = []
        constraints_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'constraints')

        for constraint in self.query.subject_to:
            name = constraint[0]
            params = list(constraint[1:])
            module_name = 'cvl.engines.postgres.constraints.%s' % name
            module_file = '%s/%s.py' % (constraints_dir, name)
            #pdb.set_trace()
            mod = imp.load_source(module_name, module_file)
            constraints.append((name, mod.FIND_CONFLICTS))
        return constraints

    def Info(self, *info):
        for comment in info:
            self.code.append(COMMENT.format(comment=comment))
            self.code.append("\n")

    def Initialize(self):
        self.code.append(BEGIN_TX)

        self.Info('Dropping old version of output table')
        self.code.append(DROP_OUTPUT_TABLE.format(self.query))

        self.Info('Creating new output table and index')
        self.code.append(CREATE_OUTPUT_TABLE_AND_INDEX.format(self.query))

        self.Info('Adding CVL framework')
        self.code.append(ADD_FRAMEWORK)

    def Finalize(self):
        self.Comment('Removing CVL framework')
        self.code.append(REMOVE_FRAMEWORK)
        self.code.append(COMMIT_TX)

    def MergePartitions(self):
        self.Comment('Merging partitions')
        code = []
        merged = []
        formatter = self.query.__dict__.copy()

        for merge in filter(lambda x: x[0] is not WILDCARD, self.query.merge_partitions):
            formatter['before_merge'] = ', '.join(map(lambda x: "'{0:s}'".format(x), merge[0]))
            formatter['after_merge'] = merge[1]
            code.append(MERGE_PARTITIONS.format(**formatter))
            merged.append(merge[1])

        for merge in filter(lambda x: x[0] is WILDCARD, self.query.merge_partitions):
            formatter['merged'] = ', '.join(map(lambda x: "'{0:s}'".format(x), merged))
            formatter['after_merge'] = merge[1]

            code.append(MERGE_PARTITIONS_REST.format(**formatter))

        self.code.extend(code)

    def CopyLevel(self, from_z, to_z):
        self.Comment('Copy data from level %d to level %d' % (from_z, to_z))
        self.code.append(COPY_LEVEL.format(**self.formatter))

    def InitializeLevel(self, z, copy_from=None):
        self.Comment('Initialization for level %d' % z)
        formatter = self.query.__dict__.copy()
        if copy_from is not None:
            formatter['copy_from'] = copy_from
            formatter['z'] = z
            self.Comment('Copy data from level %d to level %d' % (copy_from, z))
            self.code.append(COPY_LEVEL.format(**formatter))
        self.code.append(INITIALIZE_LEVEL.format(self.query))

    def ForceLevel(self, z):
        # FORCE LEVEL
        for force_delete in filter(lambda x: x[1] == z + 1, self.query.force_level):
            self.Comment('Force delete records')
            self.formatter['delete_partition'] = "'%s'" % force_delete[0]
            self.code.append(FORCE_LEVEL.format(**self.formatter))

    def FindConflicts(self, z):
        self.formatter['ignored_partitions'] = ', '.join(map(lambda x: ("'%s'" % x[0]), self.query.force_level))
        # find conflicts
        for constraint in self.constraints:
            self.Comment('Find conflicts')
            self.code.extend(constraint.set_up(z))
            self.formatter['constraint_select'] = constraint.find_conflicts(z)
            if self.formatter['ignored_partitions'] == '':
                self.code.extend(FIND_CONFLICTS.format(**self.formatter))
            else:
                self.code.extend(FIND_CONFLICTS_IGNORE.format(**self.formatter))
            self.code.extend(constraint.clean_up(z))

    def FindDeletions(self, z):
        self.formatter['solution'] = ''.join(self._solver.get_solution(self.query))
        # resolve conflicts
        self.Comment('Find hitting set')
        self.code.append(FIND_DELETIONS.format(**self.formatter))

    def ApplyDeletions(self, z):
        self.Comment('Delete hitting set')
        self.code.append(APPLY_DELETIONS.format(**self.formatter))

    def DropExportTables(self, ):
        self.Comment('Dropping old export tables')
        self.code.append(DROP_EXPORT_TABLES.format(**self.formatter))

    def CreateExportTables(self):
        self.Comment('Creating export tables')
        self.code.append(CREATE_EXPORT_TABLES.format(**self.formatter))

    def ExportLevel(self, z):
        self.Comment('Exporting conflicts')
        self.code.append(EXPORT_LEVEL.format(**self.formatter))

    def LevelTransforms(self, z):
        if 'allornothing' in self.query.transform_by:
            self.Comment('Apply all-or-nothing')
            self.code.append(ALLORNOTHING.format(**self.formatter))
        if 'simplify' in self.query.transform_by:
            self.Comment('Simplifying level')
            self.code.append(SIMPLIFY.format(**self.formatter))

    def CleanLevel(self, z):
        self.Comment('Clean-up for level %d' % z)
        self.code.append(CLEAN_LEVEL.format(**self.formatter))

    def SimplifyAll(self):
        self.Comment('Simplifying output')
        if 'simplify_once' in self.query.transform_by:
            self.code.append(SIMPLIFY_ALL.format(**self.formatter))

    def TryThis(self):
        self.Comment('Something you can try')
        self.code.append(TRYTHIS.format(**self.formatter))

    def get_code(self):
        return "\n".join(self.code)