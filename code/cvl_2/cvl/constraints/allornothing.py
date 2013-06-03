SET_UP = \
""""""

FIND_CONFLICTS = \
"""
SELECT 
  {fid} AS conflict_id, 
  {fid} AS record_id, 
  _rank, 
  _partition,
  1 AS min_hits 
FROM 
  {output}
WHERE
  _tile_level = {current_z}
AND
  type IN
(
  SELECT l._partition FROM 
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      {output}
    WHERE 
      _tile_level= {current_z}
    GROUP BY _partition
  ) l 
  JOIN
  (
    SELECT 
      _partition, 
      count(*) AS count
    FROM 
      {output} 
    WHERE
      _tile_level = {current_z} + 1
    GROUP BY 
      _partition
  ) r
  ON 
    l._partition = r._partition
  WHERE r.count - l.count > 0);
"""

CLEAN_UP = \
""""""

