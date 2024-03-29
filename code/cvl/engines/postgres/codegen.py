__author__ = 'kostas'

import imp
import os
import pdb

from cvl.engines.postgres.runtime import *
from cvl.engines.postgres.sql import *
from cvl.util.anonobject import Object


class CodeGenerator(object):
    """docstring for Transaction"""

    def __init__(self, query, solver_name, log_file='cvl.log', job_name='noname_job', analytics=True):
        super(CodeGenerator, self).__init__()
        self.query = query
        self.solver_name = solver_name
        self.solver = self._load_module('solvers', solver_name)
        self.constraints = []
        self.analytics = analytics
        for constraint in self.query.subject_to:
            module = self._load_module('constraints', constraint.name)
            self.constraints.append(Object(
                name=constraint.name,
                params=constraint.params,
                SET_UP=module.SET_UP,
                RESOLVE_IF_DELETE=module.RESOLVE_IF_DELETE,
                FIND_CONFLICTS=module.FIND_CONFLICTS,
                CLEAN_UP=module.CLEAN_UP)
            )
        self.log_path = log_file
        self.job_name = '[{0:s}]'.format(job_name)
        self.code = []

    def Initialize(self):
        formatter = self._get_formatter()
        formatter['path'] = self.log_path
        self.Info("-"*42,
                  "Code generated by CVL compiler",
                  "-"*42,
                  "Input:        {input}".format(**formatter),
                  "Output:       {output}".format(**formatter),
                  "Zoom-levels:  {zoomlevels}".format(**formatter),
                  "Rank by:      {rank_by}".format(**formatter),
                  "Solver:       {solver}".format(solver=self.solver_name),
                  "Subject to:   {subject_to}".format(**formatter),
                  "-"*42)

        self.code.append(BEGIN_TX)

        self.Log('BEGIN_TRANSACTION')

        self.Info('Dropping old version of output table')
        self.code.append(DROP_OUTPUT_TABLE.format(**formatter))

        self.Info('Creating new output table and index')

        self.code.append(CREATE_OUTPUT_TABLE_AND_INDEX.format(**formatter))

        self.code.append(ANALYZE.format(**formatter))

        self.Info('Adding CVL runtime')
        self.code.append(ADD_RUNTIME)
        self.code.append(OPTIMIZE_RUNTIME)

        self.Info('Installing solver')
        self.code.append(self.solver.INSTALL)

        self.Log('initialized')

        self.Log('solver "{0:s}"'.format(self.solver_name))
        constraints = ", ".join(map(lambda x: "{0:s}{1:s}".format(x.name, str(x.params)), self.query.subject_to))
        self.Log('constraints "{0:s}"'.format(constraints))
        formatter = self._get_formatter(log_path=self.log_path,job_name=self.job_name)
        self.code.append(DO_LOG_INPUTSTATS.format(**formatter))

    def Finalize(self):
        formatter = self._get_formatter()
        self.Info('Log num_recs and agg_rank for all zoom-levels')

        self.Info('Uninstalling solver')
        self.code.append(self.solver.UNINSTALL)

        self.Info('Removing CVL runtime')
        self.code.append(REMOVE_RUNTIME)

        self.code.append(COMMIT_TX)
        self.Log('COMMIT')

    def InitializeLevel(self, z):
        formatter = self._get_formatter(z=z)
        self.Info('Initialization for level {0:d}'.format(z))
        self.code.append(CREATE_TEMPORARY.format(**formatter))
        self.Log('initialized_level {0:d}'.format(z))

    def FindConflicts(self, z):
        formatter = self._get_formatter(z=z,level_view='_level_view')
        self.Info('Find conflicts')
        for constraint in self.constraints:
            #pdb.set_trace()
            for i, param in enumerate(constraint.params, start=1):
                formatter['parameter_{0:d}'.format(i)] = param
            self.code.append(constraint.SET_UP.format(**formatter))
            formatter['resolve_if_delete'] = constraint.RESOLVE_IF_DELETE.format(**formatter)
            formatter['constraint_select'] = constraint.FIND_CONFLICTS.format(**formatter)
            self.code.append(FIND_CONFLICTS.format(**formatter))
            self.code.append(constraint.CLEAN_UP.format(**formatter))
        self.Log('found_conflicts {0:d}'.format(z))

    def ResolveConflicts(self, z):
        formatter = self._get_formatter(z=z)
        formatter['solution'] = self.solver.SOLVE.format(**formatter)
        self.Info('Find records to delete and insert in temp table')
        self.code.append(SOLVE.format(**formatter))
        self.Info('Delete records')
        self.code.append(DO_DELETIONS.format(**formatter))
        self.Log('resolved_conflicts {0:d}'.format(z))

    def FinalizeLevel(self, z):
        formatter = self._get_formatter(z=z)
        if self.analytics:
            self.LogLevelStats(z)
        self.Info('Clean-up for level %d' % z)
        self.code.append(DROP_TEMPORARY.format(**formatter))
        self.Log('finalized_level {0:d}'.format(z))

    def Log(self, message):
        formatter = self._get_formatter(log_path=self.log_path, message="{0:s} {1:s}".format(self.job_name, message))
        self.code.append(DO_LOG.format(**formatter))

    def LogLevelStats(self, z):
        """
        Log the following information: LP-bound solution, size of constraints, constraints per record, rank-lost, recs-lost,
        :param z: zoom-level
        """
        formatter = self._get_formatter(log_path=self.log_path, job_name=self.job_name, z=z)
        self.code.append(DO_LOG_LEVELSTATS.format(**formatter))

    def Info(self, *info):
        for comment in info:
            self.code.append(COMMENT.format(comment=comment))

    def get_code(self):
        return "\n".join(self.code)

    def _get_formatter(self, **kwargs):
        formatter = self.query.__dict__.copy()
        for key, value in kwargs.items():
            formatter[key] = value
        return formatter

    def _load_module(self, module, submodule):
        root = os.path.dirname(os.path.realpath(__file__))
        module_file = os.path.join(root, module, '{0:s}.py'.format(submodule))
        module_name = 'cvl.engines.postgres.{module}.{submodule}'.format(module=module, submodule=submodule)
        return imp.load_source(module_name, module_file)

    def _load_constraints(self):
        constraints = []
        for constraint in self.query.subject_to:
            module = self._load_module('constraints', constraint.name)
            constraints.append(Object(
                name=constraint.name,
                params=constraint.params,
                SET_UP=module.SET_UP,
                FIND_CONFLICTS=module.FIND_CONFLICTS,
                CLEAN_UP=module.CLEAN_UP)
            )
        return constraints