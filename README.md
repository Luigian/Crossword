# Crossword

## An AI to generate crossword puzzles.

<img src="resources/crossword_output.png" width="600">

How might we go about generating a crossword puzzle? Given the structure of a crossword puzzle (i.e., which squares of the grid are meant to be filled in with a letter), and a list of words to use, the problem becomes one of choosing which words should go in each vertical or horizontal sequence of squares. We can model this sort of problem as a constraint satisfaction problem. Each sequence of squares is one variable, for which we need to decide on its value (which word in the domain of possible words will fill in that sequence).

As with many constraint satisfaction problems, these variables have both unary and binary constraints. The unary constraint on a variable is given by its length. The binary constraints on a variable are given by its overlap with neighboring variables: a single square that is common to them both. For this problem, we’ll add the additional constraint that all words must be different.

The challenge, then, was write a program to find a satisfying assignment: a different word (from a given vocabulary list) for each variable such that all of the unary and binary constraints are met.

## Implementation

There are two Python files in this project: crossword.py and generate.py. 

The first file defines two classes, Variable (to represent a variable in a crossword puzzle) and Crossword (to represent the puzzle itself). The Crossword class requires two values to create a new crossword puzzle: a structure_file that defines the structure of the puzzle and a words_file that defines a list of words to use for the vocabulary of the puzzle. Three examples of each of these files can be found in the data directory of the project.

The Crossword object stores the crossword.overlaps which is a dictionary mapping a pair of variables to their overlap. For any two distinct variables it will be None if the two variables have no overlap, or will be a pair of integers (i, j) if the variables do overlap. The pair (i, j) should be interpreted to mean that the ith character of v1’s value must be the same as the jth character of v2’s value. The Crossword objects also support a method neighbors that returns all of the variables that overlap with a given variable.

In generate.py, we define a class CrosswordCreator that we’ll use to solve the crossword puzzle. When a CrosswordCreator object is created, it gets a crossword property that should be a Crossword object. Each CrosswordCreator object also gets a domains property: a dictionary that maps variables to a set of possible words the variable might take on as a value. Initially, this set of words is all of the words in our vocabulary. The solve function does three things: first, it calls enforce_node_consistency to enforce node consistency on the crossword puzzle, ensuring that every value in a variable’s domain satisfy the unary constraints. Next, the function calls ac3 to enforce arc consistency, ensuring that binary constraints are satisfied. Finally, the function calls backtrack on an initially empty assignment to try to calculate a solution to the problem.

## Resources

* [Search - Lecture 0 - CS50's Introduction to Artificial Intelligence with Python 2020][cs50 lecture]

## Usage

**To install Pillow:**

* Inside the `crossword` directory: `pip3 install Pillow`

**To install pygame:**

* Inside the `crossword` directory: `pip3 install -r requirements.txt`

**To play Tic-Tac-Toe against the AI:** 

* Inside the `tictactoe` directory: `python runner.py`

## Credits

[*Luis Sanchez*][linkedin] 2021.

Project and images from the course [CS50's Introduction to Artificial Intelligence with Python 2020][cs50 ai] from HarvardX.

[cs50 lecture]: https://youtu.be/D5aJNFWsWew?t=4324
[linkedin]: https://www.linkedin.com/in/luis-sanchez-13bb3b189/
[cs50 ai]: https://cs50.harvard.edu/ai/2020/
