#!/usr/bin/env python

from cvl.cvlmain import CvlMain
from cvl.constraints import cellbound, proximity, allornothing, density2 
from cvl.algo.hittingset import HittingSetHeuristic

if __name__ == '__main__':
	query = {
		'datasource': 'cph_highway_copy',
		'table': 'cph_highway_output',
		'id': 'ogc_fid',
		'geometry': 'wkb_geometry',
		'other': 'type, name, oneway, lanes,_cluster_id',
		'zoomlevels': 15,
		'rank_by': 'ST_Length(wkb_geometry)',
	 	'partition_by' : '_cluster_id',
		'_maxdensity': 0.15,
		'simplify': True
	}
	cm = CvlMain(HittingSetHeuristic(**query), [density2.DensityConstraint(**query), allornothing.AllOrNothingConstraint(**query)], **query)
	print cm.generate_sql() # Query returned successfully with no result in 68070 ms on MacBook Pro