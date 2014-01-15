

# Addressing the points raised in reviews

## TODO:

- PKK: Make introduction holy again
- R3, WP: not possible to change geometry
- R3, WP: not clear how the framework is available to the community

## Ignored

- R2, WP: criticism of tile-based visibility constraint: boundary effects
- R2, DT: Not sure why the "AT X ZOOM LEVELS" clause is useful. Can you provide a motivating example? Current examples don't make the case. E.g., why "18" in Figure 4?
- R2, DT: The paragraph, "The resulting map is shown in Figure 3..." this is exactly the opposite of what I thought would happen. If the zoom level is very general, won't it be made up of many tiles that are fixed in their number of pixels? Wouldn't each such tile have 16 airports, instead of 16 for the whole world?
- R2, DT: The syntax for CVL isn't pretty. Even a simple example in Fig 6 takes a lot of clauses. Is this really the best way to do it? Figure 7 is worse, with a strange 'busted table' involved. Why is busted table needed in this example, but not Fig 6? Is it because it's zoom-level-independent?
- R2, DT: The mapping of context sets to set cover is really critical and is not clear. Why can a conflict set be chosen only once? Add "for each record"
- R2, DT: Do the "extensions" add anything to the difficulty or time complexity? There's no discussion of whether this could happen.

## Addressed

### Abstract:

- R2, DC: Unclear: "Unfortunately, with current tools, ..." The notion of a zoom level isn't obvious yet.

### Introduction:

- PKK: Rename single-level filtering problem to selection problem, to be consistent with literature
- R2, DT: Not sure what you mean here: "while also specifying how records are rendered"
- Reword "symbolization"


### Multi-scale filtering problem:

- PKK: Drop bottom-up term and introduce ladder and star approach to cover multi-scale case. Write that we use ladder approach and why. Throw in a reference and be done with it.
- PKK: Rename single-level filtering problem to selection problem, to be consistent with literature
- R2, WP: Approach of using conflict sets is underexamined: how many, how large, can they characterize every desirable violation.
- R2, WP: not clear that mapping is necessary
- R2, DT: Section II: it seems you do not handle "regional labels" that might reappear at more general zoom levels. (Eg, "Europe" reappears when the camera pulls out far enough.) That should be made explicit in the text.
- R2, DT: Section 3A: the notion of "weight" is casually introduced. Is it good or bad to have heavy weight? I eventually figured it out, but be clear here.


### CVL Language

- page 4, Description of Fig. 4. The airports are weighting ... -> The airports are weighted
- PKK: Rename single-level filtering problem to selection problem, to be consistent with literature
- R2, DT: "The create constraint... and the generalize statement is used for everything else." What is 'everything else'?


### Multi-scale filtering optimization problem

- PKK: Drop multi-level filtering problem (we don't do it, and won't do it either)
- PKK: Rename single-level filtering problem to selection problem, to be consistent with literature
- R2, WP: mapping to set cover not convincing


### Algorithms for single-scale filtering

- PKK: Rename single-level filtering problem to selection problem, to be consistent with literature

### Implementation

### Experimental results

- page 8, Datasets "... the biggest one containing 23 million points ..." in Table 1, the biggest non-synthetic dataset has "only" 9 million points.
- R1, WP: running time

### Related work

### Conclusion

### Acknowledgements

- PKK: Change acknowledgements to "We would like to thank employees and management at Grontmij and Danish Geodata Agency for valuable discussions and for funding our work. We would also like to thank Amazon for providing an AWS in education grant which we used to implement our experimental setup". Ingen nævnt, ingen glemt.

### References

- Reference [30] Some authors are listed twice.
