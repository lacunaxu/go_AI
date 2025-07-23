import copy
import random
from read import readInput
from write import writeOutput

BOARD_SIZE = 5

# === Helper functions ===
def find_adjacent_stones(board, row, col):
    neighbors = [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
    return [point for point in neighbors if 0 <= point[0] < BOARD_SIZE and 0 <= point[1] < BOARD_SIZE]

def find_ally_neighbors(board, row, col):
    allies = []
    for point in find_adjacent_stones(board, row, col):
        if board[point[0]][point[1]] == board[row][col]:
            allies.append(point)
    return allies

def find_ally_cluster(board, row, col):
    queue = [(row, col)]
    cluster = []
    while queue:
        node = queue.pop(0)
        cluster.append(node)
        for neighbor in find_ally_neighbors(board, node[0], node[1]):
            if neighbor not in queue and neighbor not in cluster:
                queue.append(neighbor)
    return cluster

def cluster_liberty(board, row, col):
    count = 0
    for point in find_ally_cluster(board, row, col):
        for neighbor in find_adjacent_stones(board, point[0], point[1]):
            if board[neighbor[0]][neighbor[1]] == 0:
                count += 1
    return count

def find_dead_stones(board, color):
    dead_stones = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == color:
                if cluster_liberty(board, i, j) == 0 and (i, j) not in dead_stones:
                    dead_stones.append((i, j))
    return dead_stones

def remove_stones(board, stones):
    for stone in stones:
        board[stone[0]][stone[1]] = 0
    return board

def remove_dead_stones(board, color):
    dead_stones = find_dead_stones(board, color)
    if not dead_stones:
        return board
    return remove_stones(board, dead_stones)

def ko_(prev_board, board):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] != prev_board[i][j]:
                return False
    return True

def good_move(board, prev_board, player, row, col):
    if board[row][col] != 0:
        return False
    board_copy = copy.deepcopy(board)
    board_copy[row][col] = player
    dead_pieces = find_dead_stones(board_copy, 3 - player)
    board_copy = remove_dead_stones(board_copy, 3 - player)
    if cluster_liberty(board_copy, row, col) >= 1 and not (dead_pieces and ko_(prev_board, board_copy)):
        return True
    return False

def find_valid_moves(board, prev_board, player):
    valid_moves = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if good_move(board, prev_board, player, i, j):
                valid_moves.append((i, j))
    return valid_moves

def heuristic(board, player):
    maximizer, minimizer = 0, 0
    heur_max, heur_min = 0, 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                maximizer += 1
                heur_max += maximizer + cluster_liberty(board, i, j)
            elif board[i][j] == 3 - player:
                minimizer += 1
                heur_min += minimizer + cluster_liberty(board, i, j)
    return heur_max - heur_min

def make_move(board, move, player):
    board_copy = copy.deepcopy(board)
    board_copy[move[0]][move[1]] = player
    board_copy = remove_dead_stones(board_copy, 3 - player)
    return board_copy

def minimax(curr_state, prev_state, depth, alpha, beta, player):
    moves = []
    best = -float('inf')
    for move in find_valid_moves(curr_state, prev_state, player):
        next_state = make_move(curr_state, move, player)
        score = -min_play(next_state, curr_state, depth - 1, -beta, -alpha, 3 - player)
        if score > best or not moves:
            best = score
            alpha = best
            moves = [move]
        elif score == best:
            moves.append(move)
    return moves

def min_play(curr_state, prev_state, depth, alpha, beta, player):
    best = heuristic(curr_state, player)
    if depth == 0:
        return best
    for move in find_valid_moves(curr_state, prev_state, player):
        next_state = make_move(curr_state, move, player)
        score = -max_play(next_state, curr_state, depth - 1, -beta, -alpha, 3 - player)
        if score > best:
            best = score
        if -best < alpha:
            return best
        if best > beta:
            beta = best
    return best

def max_play(curr_state, prev_state, depth, alpha, beta, player):
    best = heuristic(curr_state, player)
    if depth == 0:
        return best
    for move in find_valid_moves(curr_state, prev_state, player):
        next_state = make_move(curr_state, move, player)
        score = -min_play(next_state, curr_state, depth - 1, -beta, -alpha, 3 - player)
        if score > best:
            best = score
        if -best < alpha:
            return best
        if best > beta:
            beta = best
    return best

# === Main Execution ===
if __name__ == '__main__':
    color, prev_board, curr_board = readInput(BOARD_SIZE)

    checker = 0
    center_occupied = False
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if curr_board[i][j] != 0:
                if i == 2 and j == 2:
                    center_occupied = True
                checker += 1

    if (checker == 0 and color == 1) or (checker == 1 and color == 2 and not center_occupied):
        action = (2, 2)
    else:
        actions = minimax(curr_board, prev_board, 2, -float('inf'), -float('inf'), color)
        action = random.choice(actions) if actions else 'PASS'

    writeOutput(action)
