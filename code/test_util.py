__author__ = 'kostas'

QUERY_DICT = {
    'zoomlevels': 18,
    'fid': 'ogc_fid',
    'geometry': 'wkb_geometry'
}

SOLVERS = [
    'heuristic',
    'lp'
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
        'name': 'usrivers',
        'input': '(select * from lin_4k_riversmerged where x_order <= {0:d}) t',
        'rank_by': 'st_length(wkb_geometry)/1000',
        'size': 4786},
    {
        'name': 'dai',
        'input': '(select * from pol_30k_dai where x_order <= {0:d}) t',
        'rank_by': 'st_area(wkb_geometry)/1000000',
        'size': 30181},
    {
        'name': 'xlarge_linestring',
        'input': '(select * from lin_3m_usriversplus where x_order <= {0:d}) t',
        'rank_by': 'st_length(wkb_geometry)/1000',
        'size': 3055237},
    {
        'name': 'xlarge_points',
        'input': '(select * from pnt_30m_synthetic where x_order <= {0:d}) t',
        'rank_by': 'random()',
        'size': 30000000}
]