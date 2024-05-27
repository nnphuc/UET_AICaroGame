import sys
import copy
import numpy as np

def get_move(board, player):
    return best_move(board, player)

def is_empty(board):
    return board == [[' '] * len(board)] * len(board)

def is_in(board, y, x):
    return 0 <= y < len(board) and 0 <= x < len(board)

def march(board, y, x, dy, dx, length):
    '''
    tìm vị trí xa nhất trong dy,dx trong khoảng length

    '''
    yf = y + length * dy
    xf = x + length * dx
    # chừng nào yf,xf không có trong board
    while not is_in(board, yf, xf):
        yf -= dy
        xf -= dx

    return yf, xf


def score_ready(scorecol):
    '''
    Khởi tạo hệ thống điểm

    '''
    sumcol = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}
    for key in scorecol:
        for score in scorecol[key]:
            if key in sumcol[score]:
                sumcol[score][key] += 1
            else:
                sumcol[score][key] = 1

    return sumcol

def sum_sumcol_values(sumcol):
    '''
    hợp nhất điểm của mỗi hướng
    '''
    for key in sumcol:
        if key == 5:
            sumcol[5] = int(1 in sumcol[5].values())
        else:
            sumcol[key] = sum(sumcol[key].values())

def score_of_list(lis, col):
    blank = lis.count(' ')
    filled = lis.count(col)

    if blank + filled < 5:
        return -1
    elif blank == 5:
        return 0
    else:
        return filled


def row_to_list(board, y, x, dy, dx, yf, xf):
    '''
    trả về list của y,x từ yf,xf

    '''
    row = []
    while y != yf + dy or x != xf + dx:
        row.append(board[y][x])
        y += dy
        x += dx
    return row


def score_of_row(board, cordi, dy, dx, cordf, col):
    '''
    trả về một list với mỗi phần tử đại diện cho số điểm của 5 khối
    '''
    colscores = []
    y, x = cordi
    yf, xf = cordf
    row = row_to_list(board, y, x, dy, dx, yf, xf)
    for start in range(len(row) - 4):
        score = score_of_list(row[start:start + 5], col)
        colscores.append(score)

    return colscores

def score_of_col_one(board, col, y, x):
    '''
    trả lại điểm số của column trong y,x theo 4 hướng,
    key: điểm số khối đơn vị đó -> chỉ ktra 5 khối thay vì toàn bộ
    '''

    scores = {(0, 1): [], (-1, 1): [], (1, 0): [], (1, 1): []}

    scores[(0, 1)].extend(score_of_row(board, march(board, y, x, 0, -1, 4), 0, 1, march(board, y, x, 0, 1, 4), col))

    scores[(1, 0)].extend(score_of_row(board, march(board, y, x, -1, 0, 4), 1, 0, march(board, y, x, 1, 0, 4), col))

    scores[(1, 1)].extend(score_of_row(board, march(board, y, x, -1, -1, 4), 1, 1, march(board, y, x, 1, 1, 4), col))

    scores[(-1, 1)].extend(score_of_row(board, march(board, y, x, -1, 1, 4), 1, -1, march(board, y, x, 1, -1, 4), col))

    return score_ready(scores)

def possible_moves(board):
    taken = []
    # mảng directions lưu hướng đi (8 hướng)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1)]
    # cord: lưu các vị trí không đi
    cord = {}

    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != ' ':
                taken.append((i, j))
    for direction in directions:
        dy, dx = direction
        for coord in taken:
            y, x = coord
            for length in [1, 2, 3, 4]:
                move = march(board, y, x, dy, dx, length)
                if move not in taken and move not in cord:
                    cord[move] = False
    return cord

def is_o_first_moves(board):
    count_o = 0
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == 'o':
                count_o += 1
    return count_o == 0

def play_o_first_move(board):
    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == 'x':
                return (y, x-1)


def TF34score(score3, score4):
    '''
    trả lại trường hợp chắc chắn có thể thắng(4 ô liên tiếp)
    '''
    for key4 in score4:
        if score4[key4] >= 1:
            for key3 in score3:
                if key3 != key4 and score3[key3] >= 2:
                    return True
    return False

def calculate_score(board, player, opponent, y, x):
    thread_score = 100000000
    if player == 'x':
        attack_score = calculate_individual_score(board, player, y, x, thread_score + 4000000)
        defense_score = calculate_individual_score(board, opponent, y, x, thread_score - 4000000)
    else:
        attack_score = calculate_individual_score(board, player, y, x, thread_score - 4000000)
        defense_score = calculate_individual_score(board, opponent, y, x, thread_score + 4000000)
    return attack_score + defense_score

def calculate_individual_score(board, player, y, x, thread_score):
    board[y][x] = player
    multiply_rate = 12
    sum_player = score_of_col_one(board, player, y, x)
    num_threads = winning_situation(sum_player)
    score = num_threads * thread_score
    sum_sumcol_values(sum_player)
    weights = np.array([multiply_rate, multiply_rate ** 2, multiply_rate ** 3, multiply_rate ** 4, multiply_rate ** 5])
    keys = [-1, 1, 2, 3, 4]
    values = np.array([sum_player[key] for key in keys])
    score += np.dot(weights, values)
    board[y][x] = ' '
    return score


def winning_situation(sumcol):
    '''
    trả lại tình huống chiến thắng dạng như:
    {0: {}, 1: {(0, 1): 4, (-1, 1): 3, (1, 0): 4, (1, 1): 4}, 2: {}, 3: {}, 4: {}, 5: {}, -1: {}}
    1-5 lưu điểm có độ nguy hiểm từ thấp đến cao,
    -1 là rơi vào trạng thái tồi, cần phòng thủ
    '''

    if 1 in sumcol[5].values():
        return 1000
    elif len(sumcol[4]) >= 2 or (len(sumcol[4]) >= 1 and max(sumcol[4].values()) >= 2):
        return 70
    elif TF34score(sumcol[3], sumcol[4]):
        return 70
    else:
        score3 = sorted(sumcol[3].values(), reverse=True)
        if len(score3) >= 2 and score3[0] >= score3[1] >= 2:
            return 10
    return 0

def best_move(board, player):
    global best_moves_current_player
    if player == 'x':
        if is_empty(board):
            return int(len(board) / 2), int(len(board) / 2)
        opponent = 'o'
    else:
        if is_o_first_moves(board):
            return play_o_first_move(board)
        opponent = 'x'

    predicted_move = (0, 0)
    max_score = -sys.maxsize

    moves = possible_moves(board)

    for move in moves:
        y, x = move
        temp_score = calculate_score(board, player, opponent, y, x)
        if temp_score > max_score:
            max_score = temp_score
            predicted_move = move
            print(move, "SCORE:", max_score)
    if player == 'x':
        attack_score = calculate_individual_score(board, player, predicted_move[0], predicted_move[1], 1000000)
        defense_score = calculate_individual_score(board, opponent, predicted_move[0], predicted_move[1], 1000000 - 50000)
    else:
        attack_score = calculate_individual_score(board, player, predicted_move[0], predicted_move[1], 1000000)
        defense_score = calculate_individual_score(board, opponent, predicted_move[0], predicted_move[1], 1000000 + 50000)
    print("Attack:", attack_score, "Defense:", defense_score)
    return predicted_move