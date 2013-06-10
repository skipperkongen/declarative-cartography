# 1: connect to database (input parameters point to tables)
# 2: read data from conflict tables (one for each zoom)
# 3: build LP from conflict data
# 4: solve LP
# 5: write solution (records to delete for each zoom level) to file as *(z, id)* pairs