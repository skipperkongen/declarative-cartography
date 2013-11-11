# Plan for revision

## Important reviewer comments

* Section II: it seems you do not handle "regional labels" that might reappear at more general zoom levels. (Eg, "Europe" reappears when the camera pulls out far enough.) That should be made explicit in the text. Kostas: This could be done by 1) using star-approach instead of ladder-approach and 2) using a zoom-level dependent weighing function. Kostas: Use term ladder-approach, instead of bottom-up approach, and add a citation to (find paper in my survey).



## Points from Skype

[10/16/13 2:14:32 PM] pimin konstantin kefaloukos: high-level plan: follow through on promises (what we will fix)
[10/16/13 2:14:57 PM] pimin konstantin kefaloukos: - summary discussion of aggregation
[10/16/13 2:15:06 PM] pimin konstantin kefaloukos: - justification of algorithms
[10/16/13 2:15:49 PM] pimin konstantin kefaloukos: difficult part:
[10/16/13 2:16:16 PM] pimin konstantin kefaloukos: - read the reviews carefully
[10/16/13 2:18:59 PM] pimin konstantin kefaloukos: - paper was discussed! read carefully the reject review!
[10/16/13 2:19:34 PM] pimin konstantin kefaloukos: - now we see strong and weak points
[10/16/13 2:20:48 PM] pimin konstantin kefaloukos: if we have time: create a running example
[10/16/13 2:22:08 PM] pimin konstantin kefaloukos: very important: justification for mapping to an np-hard problem
[10/16/13 2:22:30 PM] pimin konstantin kefaloukos: very important: we have to address hardness of problem
[10/16/13 2:23:27 PM] pimin konstantin kefaloukos: easy way out: if proximity plus ranking is np-hard, then we're done
[10/16/13 2:24:01 PM] pimin konstantin kefaloukos: very important: why do we model it using conflict sets, why not use a more geometric approach
[10/16/13 2:25:30 PM] pimin konstantin kefaloukos: point 1: if we use conflict sets (ok, because it's good way to reason about), WHY model using an NP-hard problem?
[10/16/13 2:26:18 PM] pimin konstantin kefaloukos: point 2: why is using conflict sets a good idea to start with? For example, could a more geometric approach be better?
[10/16/13 2:27:07 PM] pimin konstantin kefaloukos: @point 2: is there a "conflict free" formulation
[10/16/13 2:27:53 PM] pimin konstantin kefaloukos: @point 2: we use conflict sets because it's a generic way to express user-defined constraints
[10/16/13 2:29:23 PM] pimin konstantin kefaloukos: very important (an easy): fix typos etc
[10/16/13 2:30:14 PM] pimin konstantin kefaloukos: not important: the syntax isn't pretty... we have to ignore
[10/16/13 2:31:07 PM] pimin konstantin kefaloukos: point 3: fix the things we promised to fix
[10/16/13 2:31:26 PM] pimin konstantin kefaloukos: point 4: fix typos
[10/16/13 2:32:21 PM] pimin konstantin kefaloukos: @point 1 and 2: bring Martin onboard to address hardness
[10/16/13 2:34:41 PM] pimin konstantin kefaloukos: method: first phase, add the points.... second phase: compress the paper to below page limit
[10/16/13 2:35:06 PM] pimin konstantin kefaloukos: @method: careful not to add TOO much in first phase
[10/16/13 2:36:10 PM] pimin konstantin kefaloukos: deadline: November 29, 2013
[10/16/13 2:39:27 PM] pimin konstantin kefaloukos: Step 1: prepare arguments for points 1 and 2 in separate document, using Skype calls, physical meetings
[10/16/13 2:39:42 PM] pimin konstantin kefaloukos: @step 1: Kostas coordinates step 1
[10/16/13 2:40:18 PM] pimin konstantin kefaloukos: Step 2: put the arguments in the paper
[10/16/13 2:40:45 PM] pimin konstantin kefaloukos: Step 3,4: fix typos, add paragraphs we promised
[10/16/13 2:40:53 PM] pimin konstantin kefaloukos: Concludes phase 1
[10/16/13 2:40:58 PM] pimin konstantin kefaloukos: Step 5: Compress
[10/16/13 2:42:01 PM] pimin konstantin kefaloukos: @step 3: maybe address graphs Kostas was not too happy about, scalability
[10/16/13 2:45:54 PM] pimin konstantin kefaloukos: step 4.5: Make clear that it's not a DB plugin, it's a compiler that generates code for Postgres. Publish github URL and Amazon. All-in-all make it clearer
[10/16/13 2:46:36 PM] pimin konstantin kefaloukos: @step 4.5: Separate runtime from compiled output
[10/16/13 2:47:48 PM] pimin konstantin kefaloukos: @step 4.5: add README to github saying: this is not a release version etc... not before camera-ready, but definitely before conference
[10/16/13 2:48:11 PM] pimin konstantin kefaloukos: @step 4.5: add stuff we took out back into code, before conference
[10/16/13 2:50:04 PM] pimin konstantin kefaloukos: @step 4.5: put url in paper




[11/4/13 1:26:17 PM] pimin konstantin kefaloukos: Notes from meeting with Martin, Marcos and Kostas:
[11/4/13 1:28:29 PM] pimin konstantin kefaloukos: @point 2: we have conflict sets because we want constraints. we want constraints because it is the usual way to reason about generalization... cite
[11/4/13 1:31:18 PM] pimin konstantin kefaloukos: ref: thinning and "The constraint method for solving spatial conflicts in cartographic generalization"
[11/4/13 1:32:59 PM] pimin konstantin kefaloukos: remember to check if page limit has increased for camera ready

# Ideas

* Add image of bi-partite graph as explanation of mapping from conflict sets to set cover. This has worked well in presentations. See zurich2 presentation for example.
