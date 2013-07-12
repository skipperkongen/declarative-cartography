__author__ = 'kostas'

QUERY_DICT = {
    'zoomlevels': 18,
    'fid': 'ogc_fid',
    'geometry': 'wkb_geometry'
}

SOLVERS = [
    'lp',
    'heuristic'
]

CONSTRAINTS = [
    [('cellbound', 16)],
    [('proximity', 10)],
    [('cellbound', 16),('proximity', 10)]
]

DATASETS = [
    {
        'name': 'tourism',
        'input': '(select * from pnt_500k_tourism where x_order <= {0:d}) t',
        'rank_by': 'random()',
        'size': 523096},
    {
        'name': 'usrivers',
        'input': '(select * from lin_100k_usrivers where x_order <= {0:d}) t',
        'rank_by': 'st_length(wkb_geometry)/1000',
        'size': 102486},
    {
        'name': 'dai',
        'input': '(select * from pol_30k_dai where x_order <= {0:d}) t',
        'rank_by': 'st_area(wkb_geometry)/1000000',
        'size': 30181},
    {
        'name': 'airports',
        'input': '(select * from pnt_7k_airports where x_order <= {0:d}) t',
        'rank_by': 'num_routes',
        'size': 7411},
    {
        'name': 'usriversplus',
        'input': '(select * from lin_3m_usriversplus where x_order <= {0:d}) t',
        'rank_by': '',
        'size': 3055237}
]