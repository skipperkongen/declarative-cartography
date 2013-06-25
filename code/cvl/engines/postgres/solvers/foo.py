from cvxopt import matrix, spmatrix, sparse, solvers
import pdb


def f(lowerbound=False):
        conflicts = [
            {'conflict_id': 1, 'min_hits': 1, 'record_ids': [42, 54], 'record_ranks': [1.1, 1.2]},
        ]

        # make list of variables
        variables = set()
        RID = 0
        RANK = 1
        for cflt in conflicts:
            variables = variables.union(zip(cflt['record_ids'], cflt['record_ranks']))
        variables = list(variables)

        # create index of variables
        vindex = {}
        for i, var in enumerate(variables):
            vindex[var[RID]] = i

        # b: non-neg, less-than-one, min_hits
        _b = matrix([0.0] * len(variables) + [1.0] * len(variables) + [-c['min_hits'] for c in conflicts])
        # c: ranks
        _c = matrix([var[RANK] for var in variables])

        # A:
        non_neg = spmatrix(-1.0, range(len(variables)), range(len(variables)))
        less_than_one = spmatrix(1.0, range(len(variables)), range(len(variables)))
        I = []
        J = []
        for i, cflt in enumerate(conflicts):
            for v in cflt['record_ids']:
                I.append(i)
                J.append(vindex[v])
        csets = spmatrix(-1.0, I, J)

        _A = sparse([non_neg, less_than_one, csets])

        solvers.options['show_progress'] = False
        sol = solvers.lp(_c, _A, _b)

        EPSILON = 0.00001
        if lowerbound:
            snap = lambda x: (1.0 if x > (1.0 - EPSILON) else 0.0)
        else:
            snap = lambda x: (1.0 if x > EPSILON else 0.0)

        print "c: \n", _c
        print "A: \n", _A
        print "b: \n", _b
        print sol['status']
        if sol['status'] == 'optimal':
            print 'ok'
            for i, val in enumerate(sol['x']):
                print i, ': ', snap(val)

                if snap(val) == 1.0:
                    yield variables[i][RID]

for val in f():
    print val