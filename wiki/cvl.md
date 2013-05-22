# CVL

The structure of a CVL query, utilizing all possible clauses

```
GENERALIZE 			{input} ->  {output} 

AT  				{Z} ZOOM LEVELS

RANK BY 			{float-valued expression}

PARTITION BY 		{expression}

SUBJECT TO 
PROXIMITY 			{d} 
AND CELLBOUND 		{K} 
AND ALLORNOTHING 	{true/false}

PERFORM
	SIMPLIFY 		{true/false}
```