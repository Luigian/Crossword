import sys
import PIL

from PIL.Image import new

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for value in self.domains[var].copy():
                if len(value) != var.length:
                    self.domains[var].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        i, j = self.crossword.overlaps[x, y]
        revise = False

        for x_value in self.domains[x].copy():
            consistency = False
            for y_value in self.domains[y]:
                if x_value[i] == y_value[j]:
                    consistency = True
                    break
            if not consistency:        
                self.domains[x].remove(x_value)
                revise = True
                    
        return revise

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            arcs = list()
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))

        while arcs:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if not len(self.domains[x]):
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        arc = (z, x)
                        if not arc in arcs: 
                            arcs.append(arc)
        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if not assignment or len(assignment) != len(self.crossword.variables):
            return False
        for x in self.crossword.variables:
            if not assignment[x]:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x in assignment:
            if len(assignment[x]) != x.length:
                return False
            for y in assignment:
                if x is y:
                    continue
                if assignment[x] == assignment[y]:
                    return False
                if y in self.crossword.neighbors(x):
                    i, j = self.crossword.overlaps[x, y]
                    if assignment[x][i] != assignment[y][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        counts = list()
        values = list()

        if not self.domains[var]:
            return values
        
        for var_value in self.domains[var]:
            count = 0
            for y in self.crossword.neighbors(var):
                if y not in assignment:
                    i, j = self.crossword.overlaps[var, y]
                    for y_value in self.domains[y]:
                        if var_value == y_value or var_value[i] != y_value[j]:
                            count += 1
            counts.append((var_value, count))
        counts.sort(key=lambda tup: tup[1])   
        
        for tup in counts:
            values.append(tup[0])
        return values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = list()
        for var in self.crossword.variables:
            if var not in assignment:
                d = len(self.domains[var])
                n = len(self.crossword.neighbors(var))
                unassigned.append((var, d, n))

        unassigned.sort(key=lambda tup: tup[1])
        for tup in unassigned:
            if tup[1] != unassigned[0][1]:
                unassigned.remove(tup)
        
        unassigned.sort(key=lambda tup: tup[2], reverse=True)
        return unassigned[0][0]

    def domains_backup(self, var, assignment):
        """
        Makes a backup copy of the domains belonging to the variables
        that are going to be checked later for arc consistency, in case we
        need to undo the inferences and recover the previous state of these
        domains.
        """
        domains = dict()
        for y in self.crossword.neighbors(var):
            if y not in assignment:
                domains[y] = self.domains[y]
        domains[var] = self.domains[var]
        return domains

    def inferences(self, var, assignment):
        """
        Try to enforce arc consistency between the last variable assigned 
        and their neighbors.
        """
        arcs = list()
        for y in self.crossword.neighbors(var):
            if y not in assignment:
                arcs.append((y, var))
        self.domains[var] = {assignment[var]}
        return self.ac3(arcs)
        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            domains = self.domains_backup(var, assignment)
            if self.inferences(var, assignment):
                if self.consistent(assignment):
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result
            assignment.pop(var)
            for x in domains:
                self.domains[x] = domains[x] 
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
