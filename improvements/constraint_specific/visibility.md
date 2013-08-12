# Visibility specific CVL algorithm

# Naïve solution

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

# Maybe better solution

Using a.o.t. a bit-vector to represent already selected entries

* [Python bitarray](https://pypi.python.org/pypi/bitarray) (done: `pip install bitarray` on MBP). Example is `from bitarray import bitarray; a = bitarray([0]*20000000)` which runs in less than a second
* [Python bitstring](https://code.google.com/p/python-bitstring/) (done: `pip install bitstring` on MBP)
* [PostgreSQL bit](http://www.postgresql.org/docs/9.2/static/datatype-bit.html). Example is `SELECT B'0'::bit(10);` which returns bit-vector of 10 elements initialized to zero. [Bit-wise operators in PostgreSQL](http://www.postgresql.org/docs/9.2/static/functions-bitstring.html) include shifting, AND, OR, XOR etc. I have found some ideas for [finding longest prefix](http://dba.stackexchange.com/questions/43415/algorithm-for-finding-the-longest-prefix).

## Postgres bit stuff

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

## Visibility algorithm

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

