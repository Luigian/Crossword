# Crossword

## An AI to generate crossword puzzles.

<img src="resources/crossword_output.png" width="600">

How might we go about generating a crossword puzzle? Given the structure of a crossword puzzle (i.e., which squares of the grid are meant to be filled in with a letter), and a list of words to use, the problem becomes one of choosing which words should go in each vertical or horizontal sequence of squares. We can model this sort of problem as a constraint satisfaction problem. Each sequence of squares is one variable, for which we need to decide on its value (which word in the domain of possible words will fill in that sequence).

As with many constraint satisfaction problems, these variables have both unary and binary constraints. The unary constraint on a variable is given by its length. The binary constraints on a variable are given by its overlap with neighboring variables: a single square that is common to them both. For this problem, we’ll add the additional constraint that all words must be different.

The challenge, then, was write a program to find a satisfying assignment: a different word (from a given vocabulary list) for each variable such that all of the unary and binary constraints are met.

**Optimization**

Optimization is choosing the best option from a set of possible options. Problems where we tried to find the best possible option, such as in the minimax algorithm, but there are tools that we can use to solve an even broader range of problems.

**Constraint Satisfaction**

Constraint Satisfaction problems are a class of problems where variables need to be assigned values while satisfying some conditions. Constraints satisfaction problems have the following properties:

- Set of variables (x₁, x₂, …, xₙ)
- Set of domains for each variable {D₁, D₂, …, Dₙ}
- Set of constraints C

These problems can be solved using constraints that are represented as a graph. Each node on the graph is a variable, and an edge is drawn between two variables to represent a costraint.

<img src="resources/constraint_graph.png" width="400">

**Node Consistency**

A Unary Constraint is a constraint that involves only one variable. Node consistency is when all the values in a variable’s domain satisfy the variable’s unary constraints.

**Arc Consistency**

A Binary Constraint is a constraint that involves two variables. Arc consistency is when all the values in a variable’s domain satisfy the variable’s binary constraints. In other words, to make X arc-consistent with respect to Y, remove elements from X’s domain until every choice for X has a possible choice for Y. Often we are interested in making the whole problem arc-consistent and not just one variable with respect to another. In this case, we will use an algorithm called AC-3. This algorithm adds all the arcs in the problem to a queue. Each time it considers an arc, it removes it from the queue. Then, it runs the Revise algorithm to see if this arc is consistent. If changes were made to make it consistent, further actions are needed. If the resulting domain of X is empty, it means that this constraint satisfaction problem is unsolvable (since there are no values that X can take that will allow Y to take any value given the constraints). If the problem is not deemed unsolvable in the previous step, then, since X’s domain was changed, we need to see if all the arcs associated with X are still consistent. That is, we take all of X’s neighbors except Y, and we add the arcs between them and X to the queue. However, if the Revise algorithm returns false, meaning that the domain wasn’t changed, we simply continue considering the other arcs.

While the algorithm for arc consistency can simplify the problem, it will not necessarily solve it, since it considers binary constraints only and not how multiple nodes might be interconnected.

**Backtracking Search**

A constraint satisfaction problem can be seen as a search problem:

- Initial state: empty assignment (all variables don’t have any values assigned to them).
- Actions: add a {variable = value} to assignment; that is, give some variable a value.
- Transition model: the transition model returns the state that includes the assignment following the latest action.
- Goal test: check if all variables are assigned a value and all constraints are satisfied.
- Path cost function: all paths have the same cost. As opposed to typical search problems, optimization problems care about the solution and not the route to the solution.

However, going about a constraint satisfaction problem naively, as a regular search problem, is massively inefficient. Instead, we can make use of the structure of a constraint satisfaction problem to solve it more efficiently.

Backtracking search is a type of a search algorithm that takes into account the structure of a constraint satisfaction search problem. In general, it is a recursive function that attempts to continue assigning values as long as they satisfy the constraints. If constraints are violated, it tries a different assignment. In words, this algorithm starts with returning the current assignment if it is complete. If the assignment is not complete, the algorithm selects any of the variables that do not have an assignment yet. Then, the algorithm tries to assign a value to the variable, and runs the Backtrack algorithm again on the resulting assignment (recursion). Then, it checks the resulting value. If it is not failure, it means that the assignment worked out, and it should return this assignment. If the resulting value is failure, then the latest assignment is removed, and a new possible value is attempted, repeating the same process. If all possible values in the domain returned failure, this means that we need to backtrack. That is, that the problem is with some previous assignment. If this happens with the variable we start with, then it means that no solution satisfies the constraints.

**Inference**

Although backtracking search is more efficient than simple search, it still takes a lot of computational power. Enforcing arc consistency, on the other hand, is less resource intensive. By interleaving backtracking search with inference (enforcing arc consistency), we can get at a more efficient algorithm. This algorithm is called the Maintaining Arc-Consistency algorithm. This algorithm will enforce arc-consistency after every new assignment of the backtracking search. Specifically, after we make a new assignment to X, we will call the AC-3 algorithm and start it with a queue of all arcs (Y,X) where Y is a neighbor of X (and not a queue of all arcs in the problem).

**Heuristics**

A heuristic is a rule of thumb, meaning that, more often than not, it will bring to a better result than following a naive approach, but it is not guaranteed to do so. There are additional ways to make the algorithm more efficient:

- Selecting the variable to be assigned. So far, we selected an unassigned variable randomly. However, some choices are more likely to bring to a solution faster than others. This requires the use of heuristics. Minimum Remaining Values (MRV) is one such heuristic. The idea here is that if a variable’s domain was constricted by inference, and now it has only one value left (or even if it’s two values), then by making this assignment we will reduce the number of backtracks we might need to do later. That is, we will have to make this assignment sooner or later, since it’s inferred from enforcing arc-consistency. If this assignment brings to failure, it is better to find out about it as soon as possible and not backtrack later. Another heuristic is the Degree heuristic which relies on the degrees of variables, where a degree is how many arcs connect a variable to other variables. By choosing the variable with the highest degree, with one assignment, we constrain multiple other variables, speeding the algorithm’s process. Both heuristics are not always applicable. For example, when multiple variables have the same least number of values in their domain, or when multiple variables have the same highest degree.

- Selecting the value to assign. Another way to make the algorithm more efficient is employing yet another heuristic when we select a value from the domain of a variable. Here, we would like to use the Least Constraining Values heuristic, where we select the value that will constrain the least other variables. The idea here is that, while in the degree heuristic we wanted to use the variable that is more likely to constrain other variables, here we want this variable to place the least constraints on other variables. That is, we want to locate what could be the largest potential source of trouble (the variable with the highest degree), and then render it the least troublesome that we can (assign the least constraining value to it).

## Implementation

There are two Python files in this project: `crossword.py` and `generate.py`. 

The first file defines two classes, `Variable` (to represent a variable in a crossword puzzle) and `Crossword` (to represent the puzzle itself). The `Crossword` class requires two values to create a new crossword puzzle: a `structure_file` that defines the structure of the puzzle and a `words_file` that defines a list of words to use for the vocabulary of the puzzle. Three examples of each of these files can be found in the `data` directory.

The `Crossword` object stores the `crossword.overlaps` which is a dictionary mapping a pair of variables to their overlap. For any two distinct variables it will be `None` if the two variables have no overlap, or will be a pair of integers `(i, j)` if the variables do overlap. The pair `(i, j)` should be interpreted to mean that the ith character of v1’s value must be the same as the jth character of v2’s value. The `Crossword` objects also support a method `neighbors` that returns all of the variables that overlap with a given variable.

In `generate.py`, we define a class `CrosswordCreator` that we’ll use to solve the crossword puzzle. When a `CrosswordCreator` object is created, it gets a `crossword` property that should be a `Crossword` object. Each `CrosswordCreator` object also gets a `domains` property: a dictionary that maps variables to a set of possible words the variable might take on as a value. Initially, this set of words is all of the words in our vocabulary. The solve function does three things: first, it calls `enforce_node_consistency` to enforce node consistency on the crossword puzzle, ensuring that every value in a variable’s domain satisfy the unary constraints. Next, the function calls `ac3` to enforce arc consistency, ensuring that binary constraints are satisfied. Finally, the function calls `backtrack` on an initially empty assignment to try to calculate a solution to the problem.

## Resources

* [Optimization - Lecture 3 - CS50's Introduction to Artificial Intelligence with Python 2020][cs50 lecture]

## Usage

**To install Pillow and Pygame:**

* Inside the `crossword` directory: `pip3 install -r requirements.txt`

**To generate crossword puzzles:** 

* Inside the `crossword` directory: `python generate.py data/structure1.txt data/words1.txt output.png`

## Credits

[*Luis Sanchez*][linkedin] 2021.

Project and images from the course [CS50's Introduction to Artificial Intelligence with Python 2020][cs50 ai] from HarvardX.

[cs50 lecture]: https://youtu.be/qK46ET1xk2A?t=3070
[linkedin]: https://www.linkedin.com/in/luis-sanchez-13bb3b189/
[cs50 ai]: https://cs50.harvard.edu/ai/2020/
