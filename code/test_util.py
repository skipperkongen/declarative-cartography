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
        'name': 'airports',
        'input': '(select * from pnt_7k_airports where x_order <= {0:d}) t',
        'rank_by': 'num_routes',
        'size': 7411},
    {
        'name': 'tourism',
        'input': '(select * from pnt_500k_tourism where x_order <= {0:d}) t',
        'rank_by': 'random()',
        'size': 523096},
    {
        'name': 'synthetic',
        'input': '(select * from pnt_30m_synthetic where x_order <= {0:d}) t',
        'rank_by': 'random()',
        'size': 523096},
    {
        'name': 'waterways',
        'input': '(select * from lin_???k_waterways where x_order <= {0:d}) t',
        'rank_by': 'st_length(wkb_geometry)/1000',
        'size': 1024000},
    {
        'name': 'dai',
        'input': '(select * from pol_30m_dai where x_order <= {0:d}) t',
        'rank_by': 'st_area(wkb_geometry)/1000000',
        'size': 30181}
]