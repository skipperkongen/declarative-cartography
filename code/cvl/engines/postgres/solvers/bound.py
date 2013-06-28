__author__ = 'kostas'
from cvl.engines.postgres.solvers.lp import INSTALL as LP_INSTALL
from cvl.engines.postgres.solvers.lp import UNINSTALL as LP_UNINSTALL

INSTALL = LP_INSTALL

SOLVE = \
    """
    SELECT cvl_id FROM CVL_LPSolver('_conflicts', true)
    """

UNINSTALL = LP_UNINSTALL