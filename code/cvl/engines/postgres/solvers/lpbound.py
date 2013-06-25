__author__ = 'kostas'
from lp import INSTALL as LP_INSTALL

INSTALL = LP_INSTALL

SOLVE = \
    """
    SELECT * FROM CVL_LPSolver('_conflicts', true);
    """

UNINSTALL = \
    """
    DROP FUNCTION CVL_LPSolver(text, boolean);
    """