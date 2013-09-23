# Visibility specific CVL algorithm

The following algorithms compute solutions to the thinning problem with visibility-constraint for some *K*. All the algorithms respect the zoom-consistency constraint automatically, because we're only setting the minimum zoom-level for each record (they implicitely appear on all higher zoom-levels).

# Analysis

Observations about the possible rank of records on different zoom-levels.

* Top-level (level 0) certainly contains the *K* highest-ranked records, and in fact only those.
* Level 1 certainly contains the records with rank *K+1* to rank *2K*.
* Level 1 may contain records with rank *2K + 1* though to rank *4K*
* Level 1 will never contain records with rank lower than *4K*.
* Level 2 will never contain records with rank *2K* or higher
* ...

Generalizations:

* Zoom-level *z* only contains records from the *4^z* highest ranked records. This is a pretty useless observation for higher values of *z*, as the number grows large fast.
* Zoom-level *z* cannot contain records that are among the *zK* highest ranked records, e.g. for zoom-level 0 among the zero highest ranked records, and for zoom-level 1 among the *K* highest ranked records. This is also a pretty useless observation, because this lower-bound rises very slowly.
* If a bit-vector is used to record whether a record (ordered by rank decreasing) has been selected or not, we can do the following: The records selected for zoom-level *z*, must be among the *4^z* first unselected records in the bit-vector. Still pretty useless however.

# Naïve solution

## Python pseudo-code

D = set of all records

```python
def main(D):
  assign_zs(D, world_box, 0)

def compare_rank(item1, item2):
  # return -1, 0 or 1
  pass

def split_box(box):
  # magically split box into four quadrants
  return box[0], box[1], box[2], box[3]

def assign_zs(D, box, z):
  # BEGIN: naïve part: 
  # repeatedly intersect against all records
  in_cell = filter(lambda r: r.intersects(box), D)
  repeatedly sort same records 
  inorder = sorted(in_cell, cmp=compare_rank, reverse=True)
  # END: naïve part
  top = inorder[:K]
  rst = inorder[K:]
  for r in top:
    if r.z is None:
      r.z = z
  if rst:
    box0,box1,box2,box3 = split_box(box)
    assign_zs(D, box0, z+1)
    assign_zs(D, box1, z+1)
    assign_zs(D, box2, z+1)
    assign_zs(D, box3, z+1)
```

While correct, it is (presumumed to be) inefficient because of the many repeated sorts and big repeated intersection tests.

# Maybe better solution

Key ideas: Only sort records once. Don't compute intersection over all records again and again, only records that could possibly be relevant in this round (i.e. not records that are guaranteed to have their minimum zoom-level set in a later round).

Using a.o.t. a bit-vector to represent already selected entries

* [Python bitarray](https://pypi.python.org/pypi/bitarray) (done: `pip install bitarray` on MBP). Example is `from bitarray import bitarray; a = bitarray([0]*20000000)` which runs in less than a second
* [Python bitstring](https://code.google.com/p/python-bitstring/) (done: `pip install bitstring` on MBP)
* [PostgreSQL bit](http://www.postgresql.org/docs/9.2/static/datatype-bit.html). Example is `SELECT B'0'::bit(10);` which returns bit-vector of 10 elements initialized to zero. [Bit-wise operators in PostgreSQL](http://www.postgresql.org/docs/9.2/static/functions-bitstring.html) include shifting, AND, OR, XOR etc. I have found some ideas for [finding longest prefix](http://dba.stackexchange.com/questions/43415/algorithm-for-finding-the-longest-prefix).

## Postgres bit stuff

Use bit-vector to keep tally of records with minimum zoom-level defined. This is used to compute a the highest (smaller numerical value) record that could have its zoom-level defined. 

```sql
CREATE TABLE test (a BIT(10));

-- Initialize as zeros
INSERT INTO test VALUES (0::bit(10));
-- 0000000000

-- Set 5th bit...(4+1)
UPDATE test SET a = a | (B'1'::bit(10) >> 4); -- set 4+1 = 5th bit 
-- 0000100000                            ---

-- Set 8th bit...(7+1)
UPDATE test SET a = a | (B'1'::bit(10) >> 7);
-- 0000100100                            ---
DROP TABLE test;
```

## Python pseudo-code

D = set of all records
V = bit-vector of selected records (in order of rank)

```python
def main(D,K):
  global D = D
  global K = K
  global inorder = sorted(D, cmp=compare_rank, reverse=True)
  assign_zs(lb=1,ub=K, )

def compare_rank(item1, item2):
  # return -1, 0 or 1
  pass

def split_box(box):
  # magically split box into four quadrants
  return box[0], box[1], box[2], box[3]

def assign_zs(box, z):
  # naïve part: intersection against full D
  in_cell = filter(lambda r: r.intersects(box), D)
  # naïve part: repeated sorting of same elements 
  byrank = sorted(in_cell, cmp=compare_rank, reverse=True)
  top = byrank[:K]
  rst = byrank[K:]
  for r in top:
    if r.z is None:
      r.z = z
  if rst:
    box0,box1,box2,box3 = split_box(box)
    assign_zs(box0, z+1)
    assign_zs(box1, z+1)
    assign_zs(box2, z+1)
    assign_zs(box3, z+1)
```

