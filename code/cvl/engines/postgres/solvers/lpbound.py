__author__ = 'kostas'
from cvl.engines.postgres.solvers.lp import INSTALL as LP_INSTALL

INSTALL = LP_INSTALL

SOLVE = \
    """
    SELECT cvl_id FROM CVL_LPSolver('_conflicts', true)
    """

UNINSTALL = \
    """
    DROP FUNCTION CVL_LPSolver(text, boolean);
    """