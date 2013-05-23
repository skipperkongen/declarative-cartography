# CVL

The structure of a CVL query, utilizing all possible clauses

```
GENERALIZE 			{input} -> {output} 

AT  				{Z} ZOOM LEVELS

RANK BY 			{float-valued expression}

PARTITION BY 		{expression}

SUBJECT TO 
	PROXIMITY 		{d} 
AND CELLBOUND 		{K} 
AND ALLORNOTHING 

TRANSFORM BY
	SIMPLIFY 
```

About clauses

* GENERALIZE clause:
    * {input} is either a *table name*, *view name* or *arbitrary select statement*
    * {output} is the name of a table to write result to
* AT clause:
    * {Z} is a positive integer
* RANK BY clause:
    * {float-valued expression} is something that evaluates to a float. It is either a constant, a *function call* or a *column name* of float value.
* PARTITION BY clause:
    * {expression} is really an arbitrary expression. It is either a *constant*, a *function call* or a *column name* of arbitrary value (anything that can be grouped by).
* SUBJECT TO clause:
    * Three possible constraints
    * {d} is a positive float
    * {K} is a positive integer
    * {true/false} are boolean options
* TRANSFORM BY:
    * Only tow subclauses possible: SIMPLIFY true or SIMPLIFY false

# About constraints

In this project we consider three constraints: Proximity, Cell-Bound and AllOrNothing. The constraint set is extensible. All it takes to implement a new constraint is a select statements that creates sets of K records (for some K = 1, 2, 3, 4...) that represent a "conflict" in the map. A conflict can be resolved by deleting one record from each conflict set.

The three constraints considered:

* AllOrNothing: K=1
* Proximity: K=2
* CellBound: K=x, x>1