# Speaking Practice Grading Algorithm
Here is where we will explain the model begind the grading algorithm.
The documentation should include the different categories of grading, the criteria of those categories, and an overview of the implementation of each sub-algorithm.

## Word Presence : 50% of total
80% is based upon the presence and amount of each word from the correct expression <br />
20% is based upon having the same number of words in the expression. <br />

## Word Order : 50 % of total
25% is based upon the postion of words in the expression. <br />
75% is based upon the order in which the words appear. <br />

## Overrall Equation : ((Word Presence + Word Count) * .5) + ((Word Position + Word Order) * .5)
Percentage Based : ((80% + 20%) * .5) + ((25% + 75%) * .5)