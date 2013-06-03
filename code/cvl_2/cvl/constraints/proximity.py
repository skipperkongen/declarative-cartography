SET_UP = \
""""""

FIND_CONFLICTS = \
"""
SELECT 
	ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id, 
	unnest(array[l.{fid}, r.{fid}]) AS record_id, 
	unnest(array[l._rank, r._rank]) as _rank, 
	unnest(array[._partition, r._partition]) as _partition
	1 as min_hits
FROM 
	{table} l 
JOIN
	{table} r
ON 
	l.{fid} < r.{fid}
AND	l._partition = r._partition
AND	l._tile_level = {current_z}
AND	r._tile_level = {current_z}
AND	ST_DWithin(l.{geometry}, r.{geometry}, ST_ResZ({current_z}, 256) * {_pixels});
"""

CLEAN_UP = \
""""""

