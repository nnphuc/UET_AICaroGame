# if is_empty(board):
#     return int(size / 2), int(size / 2)
# new_board = copy.deepcopy(board)
# for row in range(size):
#     for column in range(size):
#         if board[row][column] == 'x':
#             new_board[row][column] = 1
#         elif board[row][column] == 'o':
#             new_board[row][column] = -1
#         else:
#             new_board[row][column] = 0
# if player == 'x':
#     player = 1
# else:
#     player = -1
# engine = AI(new_board, player, depth=4, size=size)
# return engine.one_step()