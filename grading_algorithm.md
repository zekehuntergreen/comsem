# Speaking Practice Grading Algorithm
Here is where we will explain the model begind the grading algorithm.
The documentation should include the different categories of grading, the criteria of those categories, and an overview of the implementation of each sub-algorithm.

## Presence : 50% of total
Graded solely upon the presence of all the words from the correct expression

## Word Order : 50 % of total
10% is based upon having the same number of words in the expression
20% is based upon the postion of words in the expression
70% is based upon the order in which the words appear

## Overrall Equation : ((Presence) * .5) + ((Word Count + Word Position + Word Order) * .5)
