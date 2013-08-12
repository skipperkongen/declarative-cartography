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

CONSTRAINTS = {
    'A': [('cellbound', 16)],
    'B': [('proximity', 10)],
    'AB': [('cellbound', 16), ('proximity', 10)]
}

DATASETS = {
    'airports': {
        'input': '(select * from pnt_7k_airports where x_order <= {0:d}) t',
        'rank_by': 'num_routes',
        'size': 7411},
    'tourism': {
        'input': '(select * from pnt_500k_tourism where x_order <= {0:d}) t',
        'rank_by': 'random()',
        'size': 523096},
    'usrivers': {
        'input': "(select * from lin_30k_uswaterway where x_order <= {0:d} and waterway='river') t",
        'rank_by': 'st_length(wkb_geometry)/1000',
        'size': 32231},
    'usriversandstreams': {
        'input': '(select * from lin_30k_uswaterway where x_order <= {0:d}) t',
        'rank_by': 'st_length(wkb_geometry)/1000',
        'size': 32231},
    'dai': {
        'input': '(select * from pol_30k_dai where x_order <= {0:d}) t',
        'rank_by': 'st_area(wkb_geometry)/1000000',
        'size': 30181},
    'fractal': {
        'input': '(select * from pnt_30m_synthetic where x_order <= {0:d}) t',
        'rank_by': 'random()',
        'size': 30000000}
}
