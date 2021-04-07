import sys

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

        # loop thru self.domain to access each variable
        for var, domain in self.domains.items():
            # remove words that do not fit the length of the space
            inconsistent = []
            for word in domain:
                if len(word) != var.length:
                    inconsistent.append(word)

            for word in inconsistent:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        # binary constraint: neighbor overlap
        # assess domain of x for consistency with domain of y (i.e. is overlap the same letter?)

        if self.crossword.overlaps[x, y] is None:
            # then no overlap between x and y, no revisions made
            return revised

        # get overlapping values between vars x and y, return value will be some pair (i, j)
        i, j = self.crossword.overlaps[x, y]
        removable = []
        for x_word in self.domains[x]:
            # flag resets for each x_word
            flag = 0
            for y_word in self.domains[y]:
                if x_word[i] == y_word[j]:
                    # x is arc consistent with y if there is a value in the domain of y
                    # not editing y here, just looking for at least 1 matching word for each in x domain
                    flag = 1

            # if flag not triggered, then none of the values in domain y match the current x word
            if not flag:
                removable.append(x_word)
                revised = True

        # removing from domain here as i was triggering an error for changing set during iteration
        for x_word in removable:
            self.domains[x].remove(x_word)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # setup
        # queue = arcs
        if arcs is None:
            arcs = []
            # grab all neighbor pairs in the problem and add them to arcs
            for pair, overlaps in self.crossword.overlaps.items():
                # Crossword.overlaps is dict of ALL pairs, need just the ones w overlap
                if overlaps is not None:
                    arcs.append(pair)

        # loop
        while len(arcs) != 0:
            # loop thru arcs until it is empty
            # grab one arc (pair of variables that are neighbors) & remove it from the queue as we are now considering it
            x, y = arcs.pop()

            # run it thru revise()
            # if false - nothing was changed do nothing, if true - x was changed
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                # check length of domain, if 0 then we cannot solve
                    return False
                # otherwise, we need to re-review previous arcs now that there has been a change
                for pair, overlaps in self.crossword.overlaps.items():
                    if overlaps is not None:
                        if x in pair:
                            # gather all arcs that include the changed x EXCEPT the current y cause that would be duplicative and add to queue
                            if y in pair:
                                continue
                            # check (Z, X) because X is what changed - make sure Z is still arc consistent with this new X
                            if x == pair[0]:
                                continue
                            arcs.append(pair)
            # if we made it thru all of that, congrats you did it
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        if len(assignment) == len(self.crossword.variables):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check each assigned word for length, uniqueness, proper overlap
        # unique
        if list(assignment.values()) != list(set(assignment.values)):
            return False

        for var, word in assignment:
            # length
            if len(word) != var.length:
                return False

            # overlap
            # check set of var's neighbors
            for neigh in self.crossword.neighbors(self, var):
                # grab overlap
                i, j = self.crossword.overlaps[var, neigh]
                if word[i] != assignment[neigh][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # setup
        tally = {word: 0 for word in self.domains[var]}
        neighbors = self.crossword.neighbors(var)

        # loop
        for word in self.domains[var]:
            # basically check how many words violate the constraints in neighbor's domain
            # so we select word A from the domain
            # loop thru the domain of var's neighbor(s)
            for neigh in neighbors:
                # if neighbor is in assignment, don't count it
                if neigh in assignment.keys():
                    continue

                i, j = self.crossword.overlaps[var, neigh]
                for neigh_word in self.domains[neigh]:
                    # check each of those words for consistency w overlap (& unique constraint?)
                    if word[i] != neigh_word[j]:
                        tally[word] += 1
                    if word == neigh_word:
                        tally[word] += 1

        least_constraining_domain = sorted(self.domains[var], key=tally.__getitem__)
        return least_constraining_domain


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # setup
        mrv_hueristic = {var: 0 for var in self.crossword.variables if var not in assignment.keys()}
        ld_hueristic = {var: 0 for var in self.crossword.variables if var not in assignment.keys()}

        # loop
        for var in self.crossword.variables:
            if var in assignment.keys():
                # skip assigned variables
                continue

            # compute minimum remaining value hueristic
            mrv_hueristic[var] = len(self.domains[var])

            # compute largest degree hueristic
            ld_hueristic[var] = len(self.crossword.neighbors(var))

        temp = sorted([var for var in self.crossword.variables if var not in assignment.keys()], key=mrv_hueristic.__getitem__)
        return temp[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # check if we've completed assignment and stop the recursion if so
        if self.assignment_complete(assignment):
            return assignment

        # select a var to test
        var = self.select_unassigned_variable(assignment)

        # check all available values for this var
        for value in self.order_domain_values(var, assignment):
            # set var to this value for testing
            assignment[var] = value

            # check if the new assignment is consistent
            if self.consistent(assignment):

                # pass assignment through to backtrack - need to check new assignment and continue if consistent
                result = self.backtrack(assignment)
                if result != False:
                    # if no failure raised, great this value seems to work
                    return assignment

                # otherwise this caused a failure so we need to remove var-val pair from the assignment
                assignment.pop(var)

        # if loop ends without returning consistent result, return failure which triggers backtrack
        return False



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
