# See usage on http://skipperkongen.dk/2013/06/11/calling-lp-solver-from-postgres/
from cvxopt import matrix, solvers
 
solvers.options['show_progress'] = False
 
A = matrix([ [-1.0, -1.0, 0.0, 1.0], [1.0, -1.0, -1.0, -2.0] ])
b = matrix([ 1.0, -2.0, 0.0, 4.0 ])
c = matrix([ 2.0, 1.0 ])
sol=solvers.lp(c,A,b)
 
# Print string of comma-separated floats
print ",".join([str(x) for x in sol['x']])

