assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

# def cross(a, b):
#     return [s+t for s in a for t in b]

def cross(A, B):
    "Cross product of elements in A and elements in B."
    cross_prod = []
    for x in A:
        for y in B:
            cross_prod.append(x+y)
    return cross_prod

#Define each box in game of sudoku (81 boxes '9x9')
boxes = cross(rows, cols)

#Define each row in sudoku (9 rows)
row_units = [cross(r, cols) for r in rows]

#Desine each column in sudoku (9 columns)
column_units = [cross(rows, c) for c in cols]

#Define each '3x3' square unit (x9 units)
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

#Define the 2 diagonals on the 9x9 sudoku board
#diag_units = [[x+y for x,y in zip(rows,cols)],[x+y for x,y in zip(rows,cols[::-1])]]
diag_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'], ['I1', 'H2', 'G3', 'F4', 'E5', 'D6', 'C7', 'B8', 'A9']]

#Defining all units - rows/columns/3x3Squares - 27 units
unitlist = row_units + column_units + square_units + diag_units

#Define every box and the units it is part of
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

#Define the peers for every box - each box has 24 peers
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    naked_twin_values = {} #Dict to track twins in entire sudoku across all units
    
    # Find all instances of naked twins
    
    #Identify the boxes with 2 possible solutions and candidates to be naked twins
    for unit in unitlist:
        box_value = {}  #Dict to map possible pair of values in a box 
        for box in unit: 
            if (len(values[box]) == 2):
                if not values[box] in box_value:
                    box_value[values[box]] = [box]
                else:
                    box_value[values[box]].append(box)
                    
        #Filter the box_value dict to get the naked twins (real)
        for key in box_value:
            if (len(box_value[key]) == 2):
                if not key in naked_twin_values:
                    naked_twin_values[key] = [unit]
                else:
                    naked_twin_values[key].append(unit)
                    
    # Eliminate the naked twins as possibilities for their peers
    for key in naked_twin_values:
        for unit in naked_twin_values[key]:
            for box in unit:
                if values[box] != key:
                    #values[box] = values[box].replace(key[0], '')
                    assign_value(values, box, values[box].replace(key[0],''))
                    #values[box] = values[box].replace(key[1], '')
                    assign_value(values, box, values[box].replace(key[1],''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    values = []
    for x in grid:
        if x == '.':
            values.append('123456789')
        elif x in '123456789':
            values.append(x)
    
    if len(values) == 81:
        return (dict(zip(boxes,values)))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    #Find all boxes with single/solved values
    single_box = []
    for box in boxes:
        if (len(values[box]) == 1):
            single_box.append(box)
    #Find value in the solved boxes and scan peer units to remove the known solved numbers
    for b in single_box:
        val = values[b]
        for p in peers[b]:
            #values[p] = values[p].replace(val, '')
            assign_value(values, p, values[p].replace(val, ''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    #Scan thru all units for values 1-9 and create a list of box#s holding a given value. 
    #If only 1 box has a #, overrite the box with that value and hence solve it. 
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                #values[dplaces[0]] = digit
                assign_value (values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Use the naked twins stratergy
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
