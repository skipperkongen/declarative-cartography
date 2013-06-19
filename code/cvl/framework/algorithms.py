__author__ = 'kostas'
"""
The logic side of CVL. Algorithms here are stated in terms of logic rather than in terms of implementation artifacts.
These are recipes of *what* to do, not *how* to do it.
"""


class BottomUp(object):
    def get_code(self, zoomlevels, code_generator):

        # INITIALIZATION PHASE
        code_generator.Initialize()  # output table, index on output table
        code_generator.MergePartitions()  # combine partitions

        # GENERALIZATION PHASE
        for z in reversed(range(zoomlevels)):
            code_generator.Info('Creating zoom-level %d' % z)
            code_generator.InitializeLevel(z, copy_from=z + 1)
            # FORCE LEVEL
            code_generator.ForceLevel(z)
            # SUBJECT TO
            code_generator.FindConflicts(z)  # find conflicts
            code_generator.ResolveConflicts(z)  # find records to delete
            # TRANSFORM: allornothing, simplify_level
            code_generator.TransformLevel(z)
            code_generator.FinalizeLevel(z)

        # FINALIZE PHASE
        code_generator.Finalize()
        return code_generator.get_code()
