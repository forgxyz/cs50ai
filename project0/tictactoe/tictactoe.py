"""
Tic Tac Toe Player
"""


from copy import deepcopy
from math import inf


X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # X goes first, so O goes when there are an even number of spaces remaining
    # player returned when in terminal state is irrelevant
    remaining = 0
    for row in board:
        remaining += row.count(EMPTY)
    if remaining % 2 == 0:
        return O
    # odd number of EMPTY spaces indicates it is either initial_state or otherwise X's turn
    return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # to be used in miximax
    actions = set()
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell == EMPTY:
                actions.add((i, j))
    # returns set of tuples of coordinates where the cell is empty
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # check validity
    row, cell = action[0], action[1]
    if board[row][cell] != EMPTY:
        raise Exception(f"Invalid move. {(row, cell)} is not empty.")

    # add an X or an O to the board('s copy)
    result = deepcopy(board)
    result[row][cell] = player(board)
    return result


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    conditions = []
    # condition: horizontal
    for row in board:
        conditions.append(row)

    # condition: vertical
    # ugly implementation...........
    # TODO - revisit this
    zero, one, two = [], [], []
    temp = [zero, one, two]
    for row in board:
        zero.append(row[0])
        one.append(row[1])
        two.append(row[2])
    for row in temp:
        conditions.append(row)

    # condition: diagonal
    # straightforward but does it need logic? i can probably tie in the diagonals with the verticals
    # use pandas to pivot?
    conditions.append([board[0][0], board[1][1], board[2][2]])
    conditions.append([board[0][2], board[1][1], board[2][0]])

    if [X, X, X] in conditions:
        return X
    if [O, O, O] in conditions:
        return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # game over if there is a winner or no more possible moves
    if winner(board) or not any([True for row in board if EMPTY in row]):
        return True
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # TODO - there is a better way to do this one, too
    result = winner(board)
    if result == X:
        return 1
    if result == O:
        return -1
    return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if player(board) == X:
        return max_val(board, board)
    else:
        return min_val(board, board)


def max_val(board, original):
    if terminal(board):
        return utility(board)

    v = -inf
    moves = {}
    for action in actions(board):
        v = max(v, min_val(result(board, action), original))
        if board == original:
            moves[min_val(result(board, action), original)] = action
    if board == original:
        return moves[max(moves.keys())]
    return v


def min_val(board, original):
    if terminal(board):
        return utility(board)

    v = inf
    moves = {}
    for action in actions(board):
        v = min(v, max_val(result(board, action), original))
        if board == original:
            moves[max_val(result(board, action), original)] = action
    if board == original:
        return moves[min(moves.keys())]
    return v
