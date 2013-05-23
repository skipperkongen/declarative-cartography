# Constraint evaluation

Evaluating a constraint over a spatial table must produce as output an [instance of hitting set](../algorithms/hitting_set.md). 

For each zoom-level, constraints are evaluated separately for each partition (see [PARTITION BY clause of CVL](../../wiki/cvl.md)).