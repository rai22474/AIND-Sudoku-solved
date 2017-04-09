rows = 'ABCDEFGHI'
cols = '123456789'


def cross(a, b):
    """Cross product of elements in A and elements in B."""
    return [s + t for s in a for t in b]


boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]

diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'],
                  ['I1', 'H2', 'G3', 'F4', 'E5', 'D6', 'C7', 'B8', 'A9']]

unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

assignments = []


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
    sudoku_without_naked_twins = values.copy()
    for unit in unitlist:
        twins = discover_naked_twins(unit, values)

        if exist_naked_twins(twins):
            remove_twins_values(twins, unit, sudoku_without_naked_twins)

    return sudoku_without_naked_twins


def remove_twins_values(twins, unit, values):
    for box in unit:
        if box in twins:
            continue

        box_values = list(values[box])

        for twin_value in list(values[twins[0]]):
            if twin_value in list(values[box]):
                box_values.remove(twin_value)
                assign_value(values, box, ''.join(box_values))


def exist_naked_twins(twins):
    return len(twins) != 0


def discover_naked_twins(unit, values):
    possible_naked_twins = find_possible_naked_twins(unit, values)
    twins = []

    for candidate_box in possible_naked_twins:
        for box in possible_naked_twins:
            if candidate_box == box:
                continue

            if possible_naked_twins[box] == possible_naked_twins[candidate_box]:
                twins.append(box)

    return twins


def find_possible_naked_twins(unit, values):
    possible_naked_twins = dict()

    for box in unit:
        if len(values[box]) != 2:
            continue

        possible_naked_twins[box] = values[box]

    return possible_naked_twins


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
    for value in grid:
        values.append('123456789') if value == '.' else values.append(value)

    return dict(zip(cross(rows, cols), values))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    sudoku_with_eliminated_values = {}

    for key in values:
        current_value = values[key]

        if len(current_value) == 1:
            sudoku_with_eliminated_values[key] = values[key]
        else:
            sudoku_with_eliminated_values[key] = eliminate_values(key, values)

    return sudoku_with_eliminated_values


def eliminate_values(box, values):
    box_values = list(values[box])

    for peer in peers[box]:
        peer_value = values[peer]

        if len(peer_value) == 1:
            if peer_value in box_values:
                box_values.remove(peer_value)

    return ''.join(box_values)


def only_choice(values):
    sudoku_with_only_choice_values = {}

    for box in values:
        box_values = list(values[box])

        if len(box_values) == 1:
            sudoku_with_only_choice_values[box] = values[box]
            continue

        for unit in units[box]:
            choice = is_the_only_choice(box, box_values, unit, values)

            if box in sudoku_with_only_choice_values:
                if len(sudoku_with_only_choice_values[box]) == 1:
                    continue

            if choice[0]:
                sudoku_with_only_choice_values[box] = choice[1]
            else:
                sudoku_with_only_choice_values[box] = values[box]

    return sudoku_with_only_choice_values


def is_the_only_choice(box, box_values, unit, values):
    for box_value in box_values:
        if is_unique_value_in_unit(box, box_value, unit, values):
            return True, box_value

    return False, 0


def is_unique_value_in_unit(box, box_value, unit, values):
    for box_in_unit in unit:
        if box == box_in_unit:
            continue

        if box_value in list(values[box_in_unit]):
            return False

    return True


constraints = [eliminate, only_choice, naked_twins]


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        for constraint in constraints:
            values = constraint(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    solution = reduce_puzzle(values)

    if not solution:
        return False

    if not is_the_puzzle_solved(solution):
        box = select_fewest_possibilities(solution)

        for value in list(solution[box]):
            attempt = solution.copy()
            assign_value(attempt, box, value)

            attempt_solution = search(attempt)

            if not attempt_solution:
                continue

            if is_the_puzzle_solved(attempt_solution):
                return attempt_solution

    return solution


def is_the_puzzle_solved(values):
    for box in values:
        if len(values[box]) != 1:
            return False

    return True


def select_fewest_possibilities(values):
    box_with_fewest_possibilities = ''
    current_value = '123456789'

    for box in values:
        if len(values[box]) != 1 and len(current_value) >= len(values[box]):
            current_value = values[box]
            box_with_fewest_possibilities = box

        if len(current_value) == 2:
            break

    return box_with_fewest_possibilities


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return reduce_puzzle(values)


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
