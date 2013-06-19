__author__ = 'kostas'

import re
import imp
import os

from cvl.framework.query import WILDCARD
from cvl.engines.postgres.sql import *
from cvl.util.anonobject import Object


class CodeGenerator(object):
    """docstring for Transaction"""

    def __init__(self, **options):
        super(CodeGenerator, self).__init__()
        self.options = options
        self.code = []

    def set_query(self, query):
        self.query = query
        self.constraints = self._load_constraints()

    def _get_formatter(self, **kwargs):
        formatter = self.query.__dict__.copy()
        for key, value in kwargs:
            formatter[key] = value
        return formatter

    def _load_constraints(self):
        constraints = []
        constraints_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'constraints')

        for constraint in self.query.subject_to:
            module_name = 'cvl.engines.postgres.constraints.%s' % constraint.names
            module_file = '%s/%s.py' % (constraints_dir, constraint.name)
            #pdb.set_trace()
            mod = imp.load_source(module_name, module_file)
            constraints.append(Object(
                name=constraint.name,
                params=constraint.params,
                SET_UP=mod.SET_UP,
                FIND_CONFLICTS=mod.FIND_CONFLICTS,
                CLEAN_UP=mod.CLEAN_UP)
            )
        return constraints

    def Info(self, *info):
        for comment in info:
            self.code.append(COMMENT.format(comment=comment))
            self.code.append("\n")

    def Initialize(self):
        formatter = self._get_formatter()
        self.code.append(BEGIN_TX)

        self.Info('Dropping old version of output table')
        self.code.append(DROP_OUTPUT_TABLE.format(**formatter))

        self.Info('Creating new output table and index')
        self.code.append(CREATE_OUTPUT_TABLE_AND_INDEX.format(**formatter))

        self.Info('Adding CVL framework')
        self.code.append(ADD_FRAMEWORK)

    def Finalize(self):
        self.Info('Removing CVL framework')
        self.code.append(REMOVE_FRAMEWORK)
        self.code.append(COMMIT_TX)

    def MergePartitions(self):
        formatter = self._get_formatter()
        code = []
        merged = []
        self.Info('Merging partitions')
        for merge in filter(lambda clause: clause.before is not WILDCARD, self.query.merge_partitions):
            formatter['before_merge'] = ', '.join(map(lambda m: "'{0:s}'".format(m), merge.before))
            formatter['after_merge'] = merge.after
            code.append(MERGE_PARTITIONS.format(**formatter))
            merged.append(merge[1])

        for merge in filter(lambda clause: clause.before is WILDCARD, self.query.merge_partitions):
            formatter['merged'] = ', '.join(map(lambda m: "'{0:s}'".format(m), merged))
            formatter['after_merge'] = merge.after
            code.append(MERGE_PARTITIONS_REST.format(**formatter))

        self.code.extend(code)

    def InitializeLevel(self, z, copy_from=None):
        formatter = self._get_formatter(z=z)
        self.Info('Initialization for level {0:d}'.format(z))
        if copy_from is not None:
            formatter['copy_from'] = copy_from
            self.Info('Copy data from level {0:d} to level {1:d}'.format(**formatter))
            self.code.append(COPY_LEVEL.format(**formatter))
        self.code.append(CREATE_TEMP_TABLES_FOR_LEVEL.format(**formatter))

    def ForceLevel(self, z):
        formatter = self._get_formatter(z=z)
        for force in filter(lambda clause: clause.min_level == z + 1, self.query.force_level):
            self.Info('Force delete records')
            self.formatter['delete_partition'] = "'%s'" % force.partition
            self.code.append(FORCE_LEVEL.format(**formatter))

    def FindConflicts(self, z):
        ignored_partitions=', '.join(map(lambda x: ("'{0:s}'".format(x[0])), self.query.force_level))
        formatter = self._get_formatter(
            z=z,
            ignored_partitions=ignored_partitions)
        self.Info('Find conflicts')
        has_ignored = ignored_partitions != ''
        for constraint in self.constraints:
            self.code.append(constraint.SETUP.format(**formatter))
            for i, param in enumerate(constraint.params):
                formatter['parameter_{0:d}'.format(i)] = param
            formatter['constraint_select'] = constraint.FIND_CONFLICTS.format(**formatter)
            if has_ignored:
                self.code.extend(FIND_CONFLICTS.format(**formatter))
            else:
                self.code.extend(FIND_CONFLICTS_IGNORE.format(**formatter))
            self.code.append(constraint.CLEAN_UP.format(**formatter))

    def ResolveConflicts(self, z):
        formatter = self._get_formatter(z=z)
        formatter['solution'] = ''.join(self._solver.get_solution(self.query))
        # resolve conflicts
        self.Info('Insert records to delete in temp table')
        self.code.append(COLLECT_DELETIONS.format(**formatter))
        self.Info('Delete records')
        self.code.append(DO_DELETIONS.format(**formatter))

    def TransformLevel(self, z):
        formatter = self._get_formatter(z=z)
        if 'allornothing' in self.query.transform_by:
            self.Info('Apply all-or-nothing')
            self.code.append(ALLORNOTHING.format(**formatter))
        if 'simplify' in self.query.transform_by:
            self.Info('Simplifying level')
            self.code.append(SIMPLIFY.format(**formatter))

    def FinalizeLevel(self, z):
        formatter = self._get_formatter(z=z)
        self.Info('Clean-up for level %d' % z)
        self.code.append(DROP_TEMP_TABLES_FOR_LEVEL.format(**formatter))

    def SimplifyAll(self):
        formatter = self._get_formatter()
        self.Info('Simplifying output')
        if 'simplify_once' in self.query.transform_by:
            self.code.append(SIMPLIFY_ALL.format(**formatter))

    def TryThis(self):
        formatter = self._get_formatter()
        self.Comment('Something you can try')
        self.code.append(TRYTHIS.format(**formatter))

    def get_code(self):
        return "\n".join(self.code)