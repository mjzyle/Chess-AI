import models
import controller
import pandas as pd
import datetime as dt
from copy import deepcopy


def write_board_data(turn, current_player, board_start, board_end):
    board_start_enc = ''
    board_end_enc = ''
    coverage_start = ''
    coverage_end = ''

    # Encode board layouts before and after move is made
    for x in range(0, 8):
        for y in range(0, 8):
            if board_start.cells[x][y].piece is not None:
                board_start_enc += str(board_start.cells[x][y].piece)
            else:
                board_start_enc += '--'
            
            if board_end.cells[x][y].piece is not None:
                board_end_enc += str(board_end.cells[x][y].piece)
            else:
                board_end_enc += '--'

    # Encode board coverage before and after move is made
    for x in range(0, 8):
        for y in range(0, 8):
            coverage_start += ('-' if board_start.coverage_total[x][y][0] == '' else board_start.coverage_total[x][y][0]) + str(board_start.coverage_total[x][y][1])
            coverage_end += ('-' if board_end.coverage_total[x][y][0] == '' else board_end.coverage_total[x][y][0]) + str(board_end.coverage_total[x][y][1])

    data = {
        'Time': dt.datetime.now(),
        'Turn' : turn,
        'Moving Player': current_player,
        'Starting Board': board_start_enc, 
        'Ending Board': board_end_enc,
        'In Check' : board_end.in_check,
        'Starting Coverage' : coverage_start,
        'Ending Coverage' : coverage_end,
        'White Coverage Score': board_end.coverage_score_white,
        'Black Coverage Score': board_end.coverage_score_black,
        'White Piece Score' : board_end.piece_score_white,
        'Black Piece Score' : board_end.piece_score_black
    }

    return data


def play_game(data_file, white_style, black_style):
    white = models.Player('W', white_style)
    black = models.Player('B', black_style)
    board = controller.setup_board()
    boards = pd.DataFrame(columns=['Time', 'Turn', 'Moving Player', 'Starting Board', 'Ending Board', 'In Check', 'Coverage Start', 'Coverage End', 'White Piece Score', 'Black Piece Score', 'White Coverage Score', 'Black Coverage Score'])

    current_player = 'W'
    in_progress = False
    winner = 'Draw'
    turn = 1
    playing = True
    checkmate = False


    while playing:
        ###########################################
        ## WHITE TURN
        ###########################################
        current_player = 'W'
        in_progress = True
        last_board = deepcopy(board)

        print('White turn ' + str(turn))
        
        # Wait for white player to make move
        while in_progress:
            checkmate, in_progress, board = white.make_move(board)

        boards = boards.append(write_board_data(turn, current_player, last_board, board), ignore_index=True)

        # Check if black player has won (no moves possible for white)
        if checkmate:
            if board.in_check != '':
                winner = 'Black'
            playing = False
            break


        ###########################################
        ## BLACK TURN
        ###########################################
        current_player = 'B'
        in_progress = True
        last_board = deepcopy(board)

        print('Black turn ' + str(turn))

        # Wait for black player to make move
        while in_progress:
            checkmate, in_progress, board = black.make_move(board)

        boards = boards.append(write_board_data(turn, current_player, last_board, board), ignore_index=True)

        # Check if white player has won (no moves possible for black)
        if checkmate:
            if board.in_check != '':
                winner = 'White'
            playing = False
            break


        # Proceed to next turn
        turn += 1

        # Automatic stalemate after n turns or when only two kings are left standing
        if turn > 100:
            playing = False
            break

        # Determine if play has reached a draw (only king pieces are left)
        black_pieces = 0
        white_pieces = 0
        for x in range(0, 8):
            for y in range(0, 8):
                if board.cells[x][y].piece is not None:
                    if board.cells[x][y].piece.color == 'W':
                        white_pieces += 1
                    else:
                        black_pieces += 1
                if black_pieces > 1 or white_pieces > 1:
                    break
            if black_pieces > 1 or white_pieces > 1:
                    break

        if black_pieces == 1 and white_pieces == 1:
            playing = False


    boards.to_csv(data_file)
    print('Winner: ' + winner)
    print('Turns: ' + str(turn))
    print(board)

    return winner, turn

master_data = pd.DataFrame(columns=['Winner'])
start = dt.datetime.now()

#for i in range(0, 10):
#    print('Playing game ' + str(i+1))
#    winner, turns = play_game(r'raw_data/game_' + str(i+1) + '.csv')
#    master_data = master_data.append({
#        'Winner' : winner,
#        'Turns': turns
#    }, ignore_index=True)

winner, turns = play_game('raw_data/off_piece_off_piece.csv', 'offensive_pieces', 'offensive_pieces')
winner, turns = play_game('raw_data/off_cover_off_cover.csv', 'offensive_coverage', 'offensive_coverage')
winner, turns = play_game('raw_data/def_piece_def_piece.csv', 'defensive_pieces', 'defensive_pieces')
winner, turns = play_game('raw_data/def_cover_def_cover.csv', 'defensive_coverage', 'defensive_coverage')


end = dt.datetime.now()
print('Start: ' + str(start))
print('End: ' + str(end))
master_data.to_csv(r'raw_data/master.csv')