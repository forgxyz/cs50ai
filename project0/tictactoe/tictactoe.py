"""
Tic Tac Toe Player
"""

import math

from copy import deepcopy


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
    if (board[0] + board[1] + board[2]).count(EMPTY) % 2 == 1:
        return X
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    available = set()

    # loop thru each place on the board. if EMPTY, add coordinates (i, j) to open set
    for i, row in enumerate(board):
        for j, spot in enumerate(row):

            if spot == EMPTY:
                available.add((i, j))

    return available


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    board_copy = deepcopy(board)

    # determine player making move
    turn = player(board_copy)

    board_copy[action[0]][action[1]] = turn

    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i, row in enumerate(board):

        # winner via 3 across
        if row.count(X) == 3 or row.count(O) == 3:
            return row[0]

        # winner via 3 down
        test_down = []
        for j in range(0, 3):
            test_down.append(board[j][i])

        if test_down.count(X) == 3 or test_down.count(O) == 3:
            return test_down[0]

    # winner via 3 diagonal
    if [board[0][0], board[1][1], board[2][2]].count(X) == 3 or [board[0][0], board[1][1], board[2][2]].count(O) == 3:
        return board[0][0]

    if [board[0][2], board[1][1], board[2][0]].count(X) == 3 or [board[0][2], board[1][1], board[2][0]].count(O) == 3:
        return board[0][0]

    # else no winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) or (board[0] + board[1] + board[2]).count(EMPTY) == 0:
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
