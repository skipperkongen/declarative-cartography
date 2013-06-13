SET_UP = \
"""
-- proximity constraints
"""

FIND_CONFLICTS = \
"""
SELECT 
	ROW_NUMBER() OVER (ORDER BY 1) AS conflict_id, 
	Unnest(array[l.{fid}, r.{fid}]) AS {fid}, 
	Unnest(array[l._rank, r._rank]) AS _rank, 
	Unnest(array[l._partition, r._partition]) AS _partition,
	1 as min_hits
FROM 
	{output} l 
JOIN
	{output} r
ON 
	l.{fid} < r.{fid}
AND	l._zoom = {current_z}
AND	r._zoom = {current_z}
-- AND l._partition = r._partition
AND	ST_DWithin(l.{geometry}, r.{geometry}, ST_ResZ({current_z}, 256) * {parameter_1})
"""

CLEAN_UP = \
""""""

