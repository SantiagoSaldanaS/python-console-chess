#  Santiago Saldaña Subías - A01708446 (18/10/2024)

# IMPORTANT NOTE: This program was made to be run in PyCharm's console. It has not been tested anywhere else but
# Visual Studio, in which the board did not look quite right.

# We import stockfish for its move checking and analysis capabilities. You HAVE to install this module
# through pip install stockfish on your terminal. Otherwise, the module will not be found.
# If using PyCharm you have to download the stockfish package from the interpreter modifier menu instead.
from stockfish import Stockfish

# We import random just to flip a coin and decide whether the computer or user should be white or black.
import random

# We import time to add some dynamic movement to some text on the tutorials.
import time as t

# We import os to manage files correctly.
import os

# Stockfish setup. Path should point to the .exe of the stockfish version to use. Other versions have not been tested.
stockfish = Stockfish(path="stockfish/stockfish-windows-x86-64-avx2.exe", depth=18,
                      parameters={"Threads": 2, "Minimum Thinking Time": 5})

# Colors' format used for the board and pieces.
black = '\033[38;2;0;0;0m'  # Black piece rgb color
white = '\033[38;2;255;255;255m'  # White piece rgb color
menu_white = '\033[38;2;230;235;230m'  # Less bright white for UIs.
white_square = '\033[48;2;174;160;139m'  # Background rgb color for white squares.
black_square = '\033[48;2;130;106;81m'  # Background rgb color for dark squares.
underline = '\033[4m'  # Allows to underline text.
reset = '\033[0m'  # Format stopper.

if str(stockfish.get_stockfish_major_version()) != '17':
    print(f"\n{underline}Advertencia. Versión no verificada de stockfish. Use a su propia discreción.{reset}")

# Pieces with their color format.
wRook = f'{white}♜'
wKnight = f'{white}♞'
wBishop = f'{white}♝'
wQueen = f'{white}♛'
wKing = f'{white}♚'
wPawn = f'{white}♟'
bRook = f'{black}♜'
bKnight = f'{black}♞'
bBishop = f'{black}♝'
bQueen = f'{black}♛'
bKing = f'{black}♚'
bPawn = f'{black}♟'
empty = ''

# Columns' values to use when drawing the board.
columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
columnsMin = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

# Row's values to use when drawing the board or getting moves.
rowString = ['1', '2', '3', '4', '5', '6', '7', '8']

# Initials for the pieces that are able to promote that vary per language.
englishInitials = ['q', 'b', 'n', 'r']
spanishInitials = ['d', 'a', 'c', 't']

# Common variations of saying 'yes' and 'no' in both english and spanish.
yes = ['yes', 'y', 'si', 's']
no = ['no', 'n']

# All commands supported by the program on its run mode.
commands = ['help', 'quit', 'leave', 'menu', 'draw', 'resign', 'ff', 'forfeit', 'fen', 'evaluation', 'eval',
            'parameters', 'version']

# Game state variables.
turn = 0  # 0 = White, 1 = Black. Defines whose turn it is.
game_over = False  # False (not over), True (over)
program_over = False  # False (not over), True (over)
show_coords = True  # True (show board coordinates), False (hide board coordinates).
change_direction = True  # Whether the board changes directions or not after someone moves on pvp.
flipped = False  # False (facing white), True (facing black). Whether the board is flipped or not.
promotion = False  # Variable that changes whenever the user tries to promote a piece.
playing_computer = False  # Whether the user is facing the computer at the moment or not.
language = 'Español'  # Español / English
auto_export_game = False  # Whether to export all games or not after they are over without asking the user first.
game_moves = []  # History of the moves made in the current game.
level = ''  # Computer level if facing it.


# Function to load languages for UI text from a .txt file.
def load_language_text(_language):
    # We specify the path in which our two .txt files are located.
    file_path = f"languages/{_language}.txt"
    # We create a dictionary to import all the keys and values to (doing this with lists would be much harder).
    _text = {}

    # We open the file path on read mode as utf-8 to maintain spanish characters like accents.
    with open(file_path, 'r', encoding='utf-8') as file:
        # We iterate through each line on the file.
        for line in file:
            # We look for a = symbol to use as a separator between key and value.
            if '=' in line:
                # We separate the line into the keys and values it had marked by the separator.
                key, value = line.strip().split('=', 1)
                # We add to our dictionary the new value on the new key. We also make sure that \n values are being
                # read as \n and not as pure text. (Causes no spaces to be added).
                _text[key] = value.replace('\\n', '\n')

    # We return the newly created dictionary with all the language database.
    return _text


# We set the language to spanish, since we are making the main UI dictionary be what is read from Español.txt
text = load_language_text(language)


# Function to export the move history of a game into a .txt file.
def export_move_history(move_list, fen_code, game_type, check_turn=None):
    # We check if the directory exists. If it does not, we create it.
    if not os.path.exists('saved_game_history'):
        os.makedirs('saved_game_history')

    # We want to make each new export of a game file to be +1 from the previous one. To do this we first define the
    # minimum number we want.
    num = 1
    while True:
        # We define what the file name of the game we are trying to see exists should be.
        _file = f'game_{num}.txt'

        # We add the file name to the directory path to make a complete file path.
        path = os.path.join('saved_game_history', _file)

        # We check if the path does not exist. If that's the case, we stop iterating because we know that the current
        # number of game is the highest and thus actual.
        if not os.path.exists(path):
            break

        # If the path did exist, we add +1 to the game # we are looking for and iterate again.
        num += 1

    # We create the path we now know belongs to a new game in write mode.
    with open(path, 'w') as file:
        # We check if the game was played against a computer. If it was, we write which side was the computer
        # and what its estimated rating was. If it was not we just write Player vs Player.
        if game_type == 'C':
            if check_turn == 0:
                file.write(text['player_computer'].format(num=num, level=level))
            else:
                file.write(text['computer_player'].format(num=num, level=level))
        else:
            file.write(text['player_player'].format(num=num))

        # We iterate over all the game moves to write them into the .txt file. We begin with move 1:
        added = 1
        for move in range(0, len(move_list),
                          2):  # We go from two on two because we want two moves (white and black) per line.
            # The white move will always be the first one, so it's a direct definition.
            white_move = move_list[move]

            # We check if we are not over the length of the list.
            if move + 1 < len(move_list):

                # Because black's move is always second, there is a chance it did not happen and thus does not need to
                # be written on the line. If it did happen though, we just have to add +1 to the index of the list to
                # get it.
                black_move = move_list[move + 1]

                # We write both moves.
                file.write(f"{added}. {white_move}, {black_move}\n")
            else:
                # We write just white's move.
                file.write(f"{added}. {white_move}\n")
            # We add +1 to the line counter.
            added += 1

        # We check if the game was played against a computer once again, because it means that the player was the only
        # one who could have resigned.
        if game_type == 'C':

            # If the game ended by resign and the user was white, it means black won (0-1)
            if (end_state == 'Resign' or end_state == 'Menu') and check_turn == 0:
                file.write("\n0 - 1\n")

            # If the game ended by resign and the user was black, it means white won (1-0)
            elif (end_state == 'Resign' or end_state == 'Menu') and check_turn == 1:
                file.write("\n1 - 0\n")

            # From what I know, draws are not something stockfish does, but I cannot be completely sure.
            elif end_state == 'Draw':
                file.write("\n1/2 - 1/2\n")
        else:
            # To check for human results we just see who had to move when the resignation request was sent.
            # If white resigned it means black won.
            if (end_state == 'Resign' or end_state == 'Menu') and turn == 0:
                file.write("\n0 - 1\n")

            # If black resigned it means white won.
            elif (end_state == 'Resign' or end_state == 'Menu') and turn == 1:
                file.write("\n1 - 0\n")

            # A draw is mutual.
            elif end_state == 'Draw':
                file.write("\n1/2 - 1/2\n")

        # Although it was possible to make a system that writes the result of the game onto the file, it has a huge
        # glaring flaw. Stockfish's module on python apparently does not have any way to check whether the game ended
        # by draw, or by checkmate and by whom. This means that if the game ends naturally (without any resign or
        # draw requests), we have no way of knowing what actually happened. In those cases, sadly nothing can be written
        # on the file.

        # We write the fen code of the final position.
        file.write(f"\nFEN: {fen_code}")

    # We notify the user that the game was saved successfully onto the directory.
    print(text['saved_game'].format(_file=_file))


# Method that brings the board to the default starting position.
def reset_board():
    global position

    # Each index represents a row, and each has its own 8 squares that represent columns within a list. These may
    # contain pieces or blank spaces.
    initialPosition = {
        "8": [bRook, bKnight, bBishop, bQueen, bKing, bBishop, bKnight, bRook],
        "7": [bPawn for _ in range(8)],
        "6": [empty for _ in range(8)],
        "5": [empty for _ in range(8)],
        "4": [empty for _ in range(8)],
        "3": [empty for _ in range(8)],
        "2": [wPawn for _ in range(8)],
        "1": [wRook, wKnight, wBishop, wQueen, wKing, wBishop, wKnight, wRook]
    }

    # We clone the dictionary to not overwrite it and lose the original preset.
    position = initialPosition.copy()


# Function that shows the board state of the position at any given time.
def display_board(board):
    #  clear_screen() To be added.
    print("\n")

    # We create a list of the names of the row keys of the dictionary.
    dict_row_keys = list(board.keys())

    # If the board is flipped, we invert this list of rows. (reversed inverts it).
    if flipped:
        dict_row_keys = reversed(dict_row_keys)

    # idx = Index of row. Enumerate allows us to receive both the index and value (column) of the dictionary keyword.
    for idx, column in enumerate(dict_row_keys):
        if show_coords:
            row = column + '\u2002'
        else:
            row = '\u2002\u2002'

        # We copy the column value list within the row.
        squares = board[column]

        # We invert / reverse their order if its flipped.
        if flipped:
            squares = reversed(squares)

        # jdx = Index of column. Once again, we receive both the number of index of the list and the value within that
        # square (index).
        for jdx, square in enumerate(squares):
            # We add specific padding to each side both of the piece than to the empty space to assure a square board.
            square = square if square is not None else empty
            square_display = f'\u2009\u2009{square}\u2009\u2009' if square.strip() else '\u2009\u2009\u3000\u2009\u2009'

            # Alternate colors based on if it's an even or an odd combination. ( == 0 even, == 1 odd).
            if (idx + jdx) % 2 == 0:
                row += white_square + square_display + reset
            else:
                row += black_square + square_display + reset

        # We print the row with the correct colors, pieces and spacing.
        print(row)

    if show_coords:
        # We add padding identical to the rows.
        column_display = '\u0020\u2002'

        # We get the preset for the columns
        coord_column = columns
        if flipped:
            # If flipped it must be reversed.
            coord_column = reversed(columns)

        # We iterate over each column, adding the appropriate padding to center it to the squares.
        for letter in coord_column:
            column_display += f'\u200A\u2004\u2006{letter}\u0020'
        print(column_display)


def begin_game():
    # We reset the board, set stockfish to the default position and save it on last_position, show the board and then
    # prepare to flip it, reset the turns and reset the game_over variable, as well as defining the end_state, game_moves
    # and whether the computer is playing or not once again.

    global turn, game_over, last_position, flipped, end_state, playing_computer, game_moves
    reset_board()
    stockfish.set_position([])
    last_position = stockfish.get_board_visual()
    flipped = 0
    display_board(position)
    if change_direction:
        flipped = not flipped
    turn = 0
    game_over = False
    end_state = 'Unknown'
    playing_computer = False
    game_moves = []


def change_turn():
    # We flip the value of the booleans turn and flipped, and print whose turn it is.

    global turn, flipped
    if not game_over:
        turn = not turn
        if change_direction is True:
            flipped = not flipped
        if turn is False and playing_computer is False:
            print(text['whites_turn'].format(white=white, reset=reset))
        else:
            print(text['blacks_turn'].format(black=black, reset=reset))


def decode_piece(_piece):
    # We decode the user input and return the icon to display on the board specifically for promotion purposes.
    if turn == 0:
        if _piece == 'r':
            return wRook
        elif _piece == 'n':
            return wKnight
        elif _piece == 'b':
            return wBishop
        elif _piece == 'q':
            return wQueen
    else:
        # Black pieces
        if _piece == 'r':
            return bRook
        elif _piece == 'n':
            return bKnight
        elif _piece == 'b':
            return bBishop
        elif _piece == 'q':
            return bQueen


def decode_piece_cpu(_piece, _turn):
    # Identical to decode_piece() but made specifically for PvC games in which the turn system behaves differently.
    if _turn == 1:
        if _piece == 'r':
            return wRook
        elif _piece == 'n':
            return wKnight
        elif _piece == 'b':
            return wBishop
        elif _piece == 'q':
            return wQueen
    else:
        # Black pieces
        if _piece == 'r':
            return bRook
        elif _piece == 'n':
            return bKnight
        elif _piece == 'b':
            return bBishop
        elif _piece == 'q':
            return bQueen


def decode_column(column):
    # We decode a string value of the column and return its equivalent on integer form to use in display_board().
    formatted_column = column.lower()
    if formatted_column == 'a':
        return 0
    elif formatted_column == 'b':
        return 1
    elif formatted_column == 'c':
        return 2
    elif formatted_column == 'd':
        return 3
    elif formatted_column == 'e':
        return 4
    elif formatted_column == 'f':
        return 5
    elif formatted_column == 'g':
        return 6
    elif formatted_column == 'h':
        return 7


def is_move_command(word):
    global program_over, game_over, end_state

    # We check if the string the user used on certain inputs with a '/' at the beginning is a command.

    wordFormatted = word.lower()

    if wordFormatted in commands:
        # Help
        if wordFormatted == commands[0]:
            # Displays all commands with their brief descriptions.
            print(text['commands_help'].format(menu_white=menu_white, commands0=commands[0], commands1=commands[1],
                                               commands2=commands[2], commands3=commands[3], commands4=commands[4],
                                               commands5=commands[5], commands6=commands[6], commands7=commands[7],
                                               commands8=commands[8], commands9=commands[9], commands10=commands[10],
                                               commands11=commands[11], commands12=commands[12], reset=reset,
                                               white=menu_white))

        # Quit
        elif wordFormatted == commands[1] or wordFormatted == commands[2]:
            # Exits the program.
            program_over = True
            # Quit destroys all program executions directly and leaves an exit message (similar to exit()).
            quit(text['quit_message'])

        # Menu
        elif wordFormatted == commands[3]:
            # Goes back to the menu (another way to resign a game).
            print(text['sure_exit'])
            while True:
                answer = input(text['response1'] + ' ').lower().replace(' ', '')
                if answer in yes:
                    game_over = True
                    end_state = 'Menu'
                    break
                else:
                    break

        # Draw
        elif wordFormatted == commands[4]:
            # Sends a draw request. If both parties accept it the game is drawn.
            if playing_computer is False:
                print(text['sure_draw'])
                while True:
                    answer = input(text['response1'] + ' ').lower().replace(' ', '')
                    if answer in yes:
                        game_over = True
                        end_state = 'Draw'
                        break
                    else:
                        break
            else:
                # This stockfish module cannot accept or even have a way to see draw requests.
                print(text['draw_machine'])

        # Resign
        elif wordFormatted == commands[5] or wordFormatted == commands[6] or wordFormatted == commands[7]:
            # Asks whether the current player to move wants to resign or not.
            print(text['sure_surrender'])
            while True:
                answer = input(text['response1'] + ' ').lower().replace(' ', '')
                if answer in yes:
                    game_over = True
                    end_state = 'Resign'
                    break
                else:
                    break

        # FEN
        elif wordFormatted == commands[8]:
            # Gets the fen code from the current position and prints it.
            print(str(text['fen_position']) + str(stockfish.get_fen_position()))

        # Evaluation
        elif wordFormatted == commands[9] or wordFormatted == commands[10]:
            # Gets the current numerical evaluation according to stockfish (not very reliable).
            eval_dic = stockfish.get_evaluation()
            if eval_dic['type'] == 'cp':
                if eval_dic['value'] > 0:
                    print(text['white_centi_adv'].format(eval=eval_dic['value']))
                elif eval_dic['value'] < 0:
                    print(text['black_centi_adv'].format(eval=eval_dic['value'] * -1))
            elif eval_dic['type'] == 'mate':
                if eval_dic['value'] > 0:
                    print(text['white_mate_in'].format(eval=eval_dic['value']))
                elif eval_dic['value'] < 0:
                    print(text['black_mate_in'].format(eval=eval_dic['value'] * -1))

        # Parameters
        elif wordFormatted == commands[11]:
            # Gets stockfish's parameters and prints them.
            param_dic = stockfish.get_parameters()
            print("")
            for key in param_dic:
                print(f"{key}: {param_dic[key]}")

        # Version
        elif wordFormatted == commands[12]:
            # Gets stockfish's version and prints it.
            print(str(text['current_engine']) + ' ' + str(stockfish.get_stockfish_major_version()) + '.')

    else:
        # Not a valid command.
        print(text['error_command'])


def game_over_checker():
    global game_over

    # To evaluate if the position is checkmate or a draw.
    evaluation = stockfish.get_evaluation()
    if evaluation['value'] == 0:
        move = stockfish.get_best_move()
        # We double-check that no move is possible since get_evaluation() is not always perfect. We use evaluation
        # first because it is quicker, and calling get_best_move() every move significantly increases lag
        # and processing time.
        if move is None:
            game_over = True


def move_piece(origin_column, origin_row, ending_column, ending_row, _movement, promoted_piece):
    # Vital function in charge of updating and syncing both stockfish's and the program's boards according to the move
    # given by the user, only after checking that it is valid and legal.

    global position, stockfish, last_position, new_position

    if game_over is False:
        # Both origin and ending are gotten after adding all original and ending positions given by the user. They will
        # only be used for printing the move after displaying the board.
        origin = origin_column + origin_row
        ending = ending_column + ending_row

        # For some reason stockfish.is_move_correct('original'+'ending') does not work as it always returns True and never
        # False. I figured out a workaround which is to use stockfish.get_board_visual() because whenever an illegal move
        # is given to stockfish.make_moves_from_current_position the position does NOT change. This means that we can check
        # if the move was legal or not by comparing last move's board visual to the new one.

        # We check if there was a promotion attempt, and whether it was valid or not.
        if promotion is False:
            stockfish.make_moves_from_current_position([f"{origin_column}{origin_row}{ending_column}{ending_row}"])
        else:
            stockfish.make_moves_from_current_position(
                [f"{origin_column}{origin_row}{ending_column}{ending_row}{promoted_piece}"])

        new_position = stockfish.get_board_visual()

        if new_position != last_position:
            # If the new board position is different (legal move) we update the console's board and continue with the program.
            moved_piece = position[origin_row][decode_column(origin_column)]

            # If the promotion was valid we decode the piece to add it to the console board.
            if promotion is True:
                moved_piece = decode_piece(promoted_piece)

            # We update the console board with the new data.
            position[origin_row][decode_column(origin_column)] = empty
            position[ending_row][decode_column(ending_column)] = moved_piece

            # We check if the user castled. If they did, we move the appropriate pieces. Done through brute force.
            if promotion is False and turn is False:
                # White castling.
                # Short
                if _movement == 'e1g1':
                    position['1'][decode_column('F')] = position['1'][decode_column('H')]  # Move rook next to the king
                    position['1'][decode_column('H')] = empty  # Empty rook's original position.
                # Long
                elif _movement == 'e1c1':
                    position['1'][decode_column('D')] = position['1'][decode_column('A')]
                    position['1'][decode_column('A')] = empty
            elif promotion is False and turn is True:
                # Black castling.
                # Short
                if _movement == 'e8g8':
                    position['8'][decode_column('F')] = position['8'][decode_column('H')]
                    position['8'][decode_column('H')] = empty
                # Long
                elif _movement == 'e8c8':
                    position['8'][decode_column('D')] = position['8'][decode_column('A')]
                    position['8'][decode_column('A')] = empty

            # En passant checker. It syncs stockfish's empty squares with the display's.
            # It mostly consists of iterating through all the possible squares where a piece could have been
            # taken by an en passant and checking that stockfish's and the console board's empty squares match up.
            # If they don't, stockfish's has priority and the square on console_board gets emptied.
            if promotion is False:
                rows = (4, 5)  # We only check on the rows where an en passant is possible.
                for column in columnsMin:
                    for row in rows:
                        if stockfish.get_what_is_on_square(f'{column}{row}') is None:
                            console_square = position[f'{row}'][decode_column(f'{column}')]
                            if console_square == wPawn or console_square == bPawn:
                                position[f'{row}'][decode_column(f'{column}')] = empty  # We delete the taken pawn.

            # We display the board, print what was moved, flip the turn and update last_position for future comparisons.
            display_board(position)
            print(text['last_move'].format(moved_piece=moved_piece, reset=reset, origin=origin, ending=ending))

            # We also add the move to our move list.
            if not promotion:
                game_moves.append(f"{origin}{ending}")
            else:
                # If it was a promotion we have to handle it too. We just add = and the piece in upper case.
                game_moves.append(f"{origin}{ending}={promoted_piece.upper()}")
            last_position = new_position

            game_over_checker()
            change_turn()

        else:
            # If the new board position is the same as the last one we don't change, move or do anything but print this.
            print(text['error_illegal'])


def valid_movement(_text):
    global promotion

    # Ensure correct assignment based on language
    if language == 'Español':
        piecesInitials = spanishInitials.copy()
    else:
        piecesInitials = englishInitials.copy()

    # We have to check that the input given by the user is correct by chess standards. This does not include legality,
    # just input type.
    while game_over is False:
        _try = input('\n' + _text + ': ')

        initialCoord, finalCoord, successful, _command, promotion = '', '', True, False, False

        promoted_piece = ''  # We define it as blank in case a piece gets promoted.

        try:
            _try = _try.replace(' ', '').replace('.', '')

            # We check if the input given by the user was a command try. If it was we handle it with the is_command func.
            if _try[0] == '/':
                word = _try.replace('/', '')
                is_move_command(word)
                successful = False
                _command = True

            else:
                # Collecting initial coordinates
                # Initial column
                if _try[0] in columnsMin or _try[0].lower() in columnsMin:
                    initialCoord += _try[0].lower()
                else:
                    successful = False

                # Initial row
                if _try[1] in rowString:
                    initialCoord += _try[1]
                else:
                    successful = False

                # Collecting final coordinates
                # Final column
                if _try[2] in columnsMin or _try[2].lower() in columnsMin:
                    finalCoord += _try[2].lower()
                else:
                    successful = False

                # Final row
                if _try[3] in rowString:
                    finalCoord += _try[3]
                else:
                    successful = False

                # Checking for promotion. If the length of the input is longer than 4 strings and contains a = its possible
                # the user is trying to promote a piece.
                if len(_try) > 4 and _try[-2] == '=':
                    if _try[-1] in piecesInitials or _try[-1].lower() in piecesInitials:
                        # Set the promoted piece based on language, as their initials change.
                        if language == 'Español':
                            piece = _try[-1].lower()
                            # We get the index of where the spanish initial matches with the one given by the user and
                            # use it to return the english one there instead (stockfish only takes the english initials).

                            for i in range(len(spanishInitials)):
                                if piece == spanishInitials[i]:
                                    promoted_piece = englishInitials[i]
                                    break

                        else:
                            # If its in english it can go directly to stockfish.
                            promoted_piece = _try[-1].lower()
                        promotion = True
                        finalCoord += promoted_piece

                    else:
                        successful = False

        except IndexError:
            successful = False

        # No red marks were set off the analysis. It is now up to stockfish to make sure it is a legal move.
        if successful is True:
            movement = initialCoord + finalCoord
            return movement

        # We repeat the function until the user gives valid coords.
        if _command is False:
            print(text['error_coords'])


def move_loop():
    # We set the order in which turns work and execute important functions.

    # We define the parameters which allow the movement of pieces.
    movement = valid_movement(text['movement'])
    if game_over is False:
        columnOrigin, rowOrigin, columnEnd, rowEnd, promoted_piece = movement[0], movement[1], movement[2], movement[3], \
                                                                     movement[-1]

        # We try to move the piece based on the previous parameters. If it's an illegal move, nothing will happen or change.
        move_piece(columnOrigin, rowOrigin, columnEnd, rowEnd, movement, promoted_piece)


def game_pvp():
    # We set the parameters to begin the game and run the game loop until the game ends.

    global turn, game_over
    begin_game()
    while game_over is False:
        move_loop()

    # When the game ends we check if it was because of a command like /resign, /draw, /menu, etc. and ask the user
    # whether they want to save the game on a .txt file or not (happens automatically if the settings is on).

    if end_state == 'Resign' and turn == 0:
        print(text['resign_white'])
    elif end_state == 'Resign' and turn == 1:
        print(text['resign_black'])
    elif end_state == 'Draw':
        print(text['draw_end'])
    elif end_state == 'Menu':
        print(text['menu_switch'])
    else:
        print(text['generic_end'])

    if not auto_export_game:
        # Asks the user whether they want to save the game or not.
        save = input(text['save_history'] + " ").lower().replace(' ', '')
        if save in yes:
            export_move_history(game_moves, stockfish.get_fen_position(), 'P')

    else:
        # Automatically saves game.
        export_move_history(game_moves, stockfish.get_fen_position(), 'P')


def game_engine():
    global stockfish, level

    # We set up which parameters stockfish will use against the user in the match.

    print(text['machine_level'].format(underline=underline, reset=reset))

    time = 1

    quickly_exit = False

    while True:
        choice = input(text['response2'] + ' ')
        choice = choice.replace(' ', '').replace('.', '').replace(',', '').lower()
        if choice == '1' or choice == 'principiante' or choice == '100' or choice == 'beginner':
            # I had to really lower the parameters over here to make newish people even stand a chance against the
            # machine. It is really strong even on the lowest settings and without time to think.

            stockfish.set_skill_level(1)
            stockfish.set_elo_rating(100)
            level = '100'
            stockfish.set_depth(1)
            time = 1
            break

        elif choice == '2' or choice == 'intermedio' or choice == '400' or choice == 'intermediate':
            stockfish.set_skill_level(3)
            stockfish.set_elo_rating(400)
            level = '400'
            stockfish.set_depth(1)
            time = 1
            break
        elif choice == '3' or choice == 'avanzado' or choice == '1000' or choice == 'advanced':
            stockfish.set_skill_level(4)
            stockfish.set_elo_rating(1000)
            level = '1,000'
            stockfish.set_depth(3)
            time = 2
            break
        elif choice == '4' or choice == 'experto' or choice == '1600' or choice == 'expert':
            stockfish.set_skill_level(6)
            stockfish.set_elo_rating(1600)
            level = '1,600'
            stockfish.set_depth(10)
            time = 2
            break
        elif choice == '5' or choice == 'maestro' or choice == '2300' or choice == 'master':
            stockfish.set_skill_level(10)
            stockfish.set_elo_rating(2300)
            level = '2,300'
            stockfish.set_depth(15)
            time = 3
            break
        elif choice == '6' or choice == 'granmaestro' or choice == '2600' or choice == 'grandmaster':
            stockfish.set_skill_level(15)
            stockfish.set_elo_rating(2600)
            level = '2,600'
            stockfish.set_depth(18)
            time = 4
            break
        elif choice == '7' or choice == 'campeon' or choice == 'campeondelmundo' or choice == '2800' or choice == 'champion' or choice == 'worldchampion':
            stockfish.set_skill_level(17)
            stockfish.set_elo_rating(2800)
            level = '2,800'
            stockfish.set_depth(18)
            time = 5
            break
        elif choice == '8' or choice == 'imposible' or choice == '3000' or choice == 'impossible' or choice == 'max':
            # A very big issue encountered on the making of the project was stockfish lagging python out and thus
            # desyncing it. This was fixed by not allowing stockfish much time to think, but it's still noticeable
            # to some extent (not as bad as when left on unlimited time). This is much more noticeable on the stronger
            # levels. The behavior basically involved the print() functions not 'firing' off at the right moments
            # (even with flush), and thus not showing the board, notifications and / or movement prompts from input().

            # The way it still somewhat happens is that it might take 1 second for the 'Movement:' text from the input
            # appear after the computer makes its move on the highest levels. Still, it's not visible unless
            # one looks for it.

            stockfish.set_skill_level(20)
            stockfish.set_elo_rating(3000)
            level = '3,000'
            stockfish.set_depth(18)
            time = 6
            break

        elif choice == '/back' or choice == 'back' or choice == '/menu' or choice == 'menu':
            quickly_exit = True
            break

        else:
            print(text['error_option'])

    if not quickly_exit:
        print(text['computer_first'])

        # We ask whether the player was to be white or black.
        while True:
            choice = input(text['response2'] + ' ')
            choice = choice.replace(' ', '').replace('.', '').replace(',', '').lower()
            if choice in yes:
                beginning = 1
                break
            elif choice in no:
                beginning = 0
                break
            elif choice == '' or choice == 'random' or choice == 'aleatorio':
                beginning = random.randint(0, 1)
                break
            else:
                print(text['error_option'])

        # We run the main game loop of the match between stockfish and the user.
        game_pvc(beginning, time)


def change_turn_cpu(_turn):
    # Personalized change_turn function for the PvC match.
    # It varies in function because it can print if the machine is thinking, and it addresses the user directly as you.

    global turn, flipped
    if not game_over:
        turn = not turn
        if turn is False:
            if _turn == 0:
                print(text['your_turn_white'].format(white=white, reset=reset))
            elif _turn == 1:
                print(text['your_turn_black'].format(black=black, reset=reset))
        else:
            print(text['computer_thinking'])


def begin_game_cpu(_turn):
    global turn, game_over, last_position, flipped, end_state, playing_computer, change_start, game_moves

    # Specific settings for matches against stockfish.
    reset_board()
    stockfish.set_position([])
    game_over = False
    end_state = 'Unknown'
    playing_computer = True  # Set to True
    last_position = stockfish.get_board_visual()
    # This is different, and it's based on what the user selected their color to be.
    if _turn == 1:
        flipped = 1
        change_start = True
        turn = 1
    else:
        flipped = 0
        display_board(position)
        turn = 0
    game_moves = []


def move_piece_player(origin_column, origin_row, ending_column, ending_row, _movement, promoted_piece, _turn):
    # Basically the same as move_piece() except for the fact that it's specialized for the PvC match.
    # This can be seen in how it alternates moves and how it can call cancel_cpu_move (to avoid stockfish changing colors
    # since the user's input was not valid). With more time I would have been able to mix both functions, but I currently
    # do not have enough for that without breaking something. This would be the first thing I would change if I had to
    # revisit this project.

    # (Actually, the first try in making a PvC system used the original move_piece() function, but it broke everything due
    # to the differences in how turns are treated in each match).

    global position, stockfish, last_position, new_position, cancel_cpu_move

    if game_over is False:
        origin = origin_column + origin_row
        ending = ending_column + ending_row

        if promotion is False:
            stockfish.make_moves_from_current_position([f"{origin_column}{origin_row}{ending_column}{ending_row}"])
        else:
            stockfish.make_moves_from_current_position(
                [f"{origin_column}{origin_row}{ending_column}{ending_row}{promoted_piece}"])
        new_position = stockfish.get_board_visual()

        if new_position != last_position:
            moved_piece = position[origin_row][decode_column(origin_column)]
            if promotion is True:
                moved_piece = decode_piece(promoted_piece)
            position[origin_row][decode_column(origin_column)] = empty
            position[ending_row][decode_column(ending_column)] = moved_piece

            if promotion is False:
                if _movement == 'e1g1':
                    position['1'][decode_column('F')] = position['1'][decode_column('H')]
                    position['1'][decode_column('H')] = empty
                elif _movement == 'e1c1':
                    position['1'][decode_column('D')] = position['1'][decode_column('A')]
                    position['1'][decode_column('A')] = empty
                elif _movement == 'e8g8':
                    position['8'][decode_column('F')] = position['8'][decode_column('H')]
                    position['8'][decode_column('H')] = empty
                elif _movement == 'e8c8':
                    position['8'][decode_column('D')] = position['8'][decode_column('A')]
                    position['8'][decode_column('A')] = empty

            if promotion is False:
                rows = (4, 5)
                for column in columnsMin:
                    for row in rows:
                        if stockfish.get_what_is_on_square(f'{column}{row}') is None:
                            console_square = position[f'{row}'][decode_column(f'{column}')]
                            if console_square == wPawn or console_square == bPawn:
                                position[f'{row}'][decode_column(f'{column}')] = empty

            display_board(position)
            print(text['you_moved'].format(moved_piece=moved_piece, reset=reset, origin=origin, ending=ending))
            if not promotion:
                game_moves.append(f"{origin}{ending}")
            else:
                game_moves.append(f"{origin}{ending}={promoted_piece.upper()}")

            change_turn_cpu(_turn)
            last_position = new_position

            game_over_checker()

        else:
            print(text['error_illegal'])
            cancel_cpu_move = True


def move_player_loop(_turn):
    # Almost same thing as the normal move_loop but calls move_piece_player() instead.
    movement = valid_movement(text['movement'])
    if game_over is False:
        columnOrigin, rowOrigin, columnEnd, rowEnd, promoted_piece = movement[0], movement[1], movement[2], movement[3], \
                                                                     movement[-1]

        move_piece_player(columnOrigin, rowOrigin, columnEnd, rowEnd, movement, promoted_piece, _turn)


def move_piece_cpu(_turn, time):
    global position, stockfish, last_position, new_position, promotion, game_over
    # This function is very important. It adapts what stockfish gives back from get_best_move_time() into the
    # visual console implementation. It uses similar checks as the player move functions but also differs in some ways
    # (for example in how it checks if it's trying to promote).

    promotion = False
    if game_over is False:
        computer_move = stockfish.get_best_move_time(time)
        if computer_move:
            if len(computer_move) >= 5:
                promotion = True
            origin_column, origin_row, ending_column, ending_row, promoted_piece = computer_move[0], computer_move[1], \
                                                                                   computer_move[2], computer_move[3], \
                                                                                   computer_move[-1].lower()
            origin = origin_column + origin_row
            ending = ending_column + ending_row

            if promotion is False:
                stockfish.make_moves_from_current_position([f"{origin_column}{origin_row}{ending_column}{ending_row}"])
            else:
                stockfish.make_moves_from_current_position(
                    [f"{origin_column}{origin_row}{ending_column}{ending_row}{promoted_piece}"])
            new_position = stockfish.get_board_visual()

            moved_piece = position[origin_row][decode_column(origin_column)]
            if promotion is True:
                moved_piece = decode_piece_cpu(promoted_piece, _turn)
            position[origin_row][decode_column(origin_column)] = empty
            position[ending_row][decode_column(ending_column)] = moved_piece

            if promotion is False:
                if computer_move == 'e1g1':
                    position['1'][decode_column('F')] = position['1'][decode_column('H')]
                    position['1'][decode_column('H')] = empty
                elif computer_move == 'e1c1':
                    position['1'][decode_column('D')] = position['1'][decode_column('A')]
                    position['1'][decode_column('A')] = empty
                elif computer_move == 'e8g8':
                    position['8'][decode_column('F')] = position['8'][decode_column('H')]
                    position['8'][decode_column('H')] = empty
                elif computer_move == 'e8c8':
                    position['8'][decode_column('D')] = position['8'][decode_column('A')]
                    position['8'][decode_column('A')] = empty

            if promotion is False:
                rows = (4, 5)
                for column in columnsMin:
                    for row in rows:
                        if stockfish.get_what_is_on_square(f'{column}{row}') is None:
                            console_square = position[f'{row}'][decode_column(f'{column}')]
                            if console_square == wPawn or console_square == bPawn:
                                position[f'{row}'][decode_column(f'{column}')] = empty

            display_board(position)
            print(text['computer_moved'].format(moved_piece=moved_piece, reset=reset, origin=origin, ending=ending))
            if not promotion:
                game_moves.append(f"{origin}{ending}")
            else:
                game_moves.append(f"{origin}{ending}={promoted_piece.upper()}")

            change_turn_cpu(_turn)
            last_position = new_position

            game_over_checker()
        else:
            # If it returns None then the game is over.
            game_over = True


def game_pvc(_turn: int, time: int):
    global cancel_cpu_move

    # Main loop / move order for the PvC implementation. Cancel cpu move means that the player's move was unsuccessful
    # and thus stockfish should NOT play again (because it means they would be the new opposite pieces).

    cancel_cpu_move = False

    begin_game_cpu(_turn)

    while game_over is False:
        # If the user is White
        if _turn == 0:
            # Calls the user move_loop
            if not game_over:
                move_player_loop(_turn)

            # Runs the computer's move loop if the previous step was successful.
            if cancel_cpu_move is False:
                move_piece_cpu(_turn, time)
            else:
                cancel_cpu_move = False

        # If the user is Black
        if _turn == 1:
            # The computer begins, although it can be cancelled if the user's move is wrong.
            if cancel_cpu_move is False:
                move_piece_cpu(_turn, time)
            else:
                cancel_cpu_move = False
            # The user moves (or tries to at the very least).
            if not game_over:
                move_player_loop(_turn)

    # Basically the same thing as in the PvP implementation. We try to see if the end game ended by a command, and check
    # if we export the move_history or not.

    if end_state == 'Resign' and turn == 0:
        print(text['resign_white'])
    elif end_state == 'Resign' and turn == 1:
        print(text['resign_black'])
    elif end_state == 'Draw':
        print(text['draw_end'])
    elif end_state == 'Menu':
        print(text['menu_switch'])
    else:
        print(text['generic_end'])

    if not auto_export_game:
        save = input(text['save_history'] + " ").lower().replace(' ', '')
        if save in yes:
            export_move_history(game_moves, stockfish.get_fen_position(), 'C', _turn)
    else:
        export_move_history(game_moves, stockfish.get_fen_position(), 'C', _turn)


def interface_options():
    # We show all the options the program has and force the user to choose one.

    print(text['menu_options'])
    print(f"\n{menu_white}===================================================={reset}")
    while True:
        choice = input(text['response2'] + ' ')
        choice = choice.replace(' ', '').replace('.', '').lower()
        if choice == '1' or choice == 'pvp':
            return 1
        elif choice == '2' or choice == 'pvc' or choice == 'computer' or choice == 'pc' or choice == 'computadora':
            return 2
        elif choice == '3' or choice == 'tutorial':
            return 3
        elif choice == '4' or choice == 'settings' or choice == 'configuracion':
            return 4
        elif choice == '5' or choice == 'credits' or choice == 'creditos':
            return 5
        elif choice == '6' or choice == 'leave' or choice == 'quit' or choice == 'salir':
            return 6
        else:
            print(text['error_option'])


def tutorial_positions(showing):
    # Brute force positions used in the notation tutorial part of the tutorial menu.
    if showing == 'knight':
        knight_position = {
            "8": [empty for _ in range(8)],
            "7": [empty for _ in range(8)],
            "6": [empty for _ in range(8)],
            "5": [empty for _ in range(8)],
            "4": [empty, empty, empty, bKnight, empty, empty, empty, empty],
            "3": [empty for _ in range(8)],
            "2": [empty for _ in range(8)],
            "1": [empty for _ in range(8)],
        }
        display_board(knight_position)
    elif showing == 'knight_moved':
        knight_position = {
            "8": [empty for _ in range(8)],
            "7": [empty for _ in range(8)],
            "6": [empty, empty, empty, empty, bKnight, empty, empty, empty],
            "5": [empty for _ in range(8)],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [empty for _ in range(8)],
            "1": [empty for _ in range(8)],
        }
        display_board(knight_position)
    elif showing == 'king':
        king_position = {
            "8": [empty for _ in range(8)],
            "7": [empty for _ in range(8)],
            "6": [empty for _ in range(8)],
            "5": [empty for _ in range(8)],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [empty for _ in range(8)],
            "1": [wRook, empty, empty, empty, wKing, empty, empty, wRook],
        }
        display_board(king_position)
    elif showing == 'king_left':
        king_position = {
            "8": [empty for _ in range(8)],
            "7": [empty for _ in range(8)],
            "6": [empty for _ in range(8)],
            "5": [empty for _ in range(8)],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [empty for _ in range(8)],
            "1": [empty, empty, wKing, wRook, empty, empty, empty, wRook],
        }
        display_board(king_position)
    elif showing == 'king_right':
        king_position = {
            "8": [empty for _ in range(8)],
            "7": [empty for _ in range(8)],
            "6": [empty for _ in range(8)],
            "5": [empty for _ in range(8)],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [empty for _ in range(8)],
            "1": [wRook, empty, empty, empty, empty, wRook, wKing, empty],
        }
        display_board(king_position)
    elif showing == 'promotion':
        promotion_position = {
            "8": [empty, empty, empty, empty, empty, empty, empty, bKing],
            "7": [empty, empty, empty, empty, wPawn, wKing, bPawn, bPawn],
            "6": [empty for _ in range(8)],
            "5": [empty for _ in range(8)],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [empty for _ in range(8)],
            "1": [empty for _ in range(8)],
        }
        display_board(promotion_position)
    elif showing == 'promoted':
        promotion_position = {
            "8": [empty, empty, empty, empty, wRook, empty, empty, bKing],
            "7": [empty, empty, empty, empty, empty, wKing, bPawn, bPawn],
            "6": [empty for _ in range(8)],
            "5": [empty for _ in range(8)],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [empty for _ in range(8)],
            "1": [empty for _ in range(8)],
        }
        display_board(promotion_position)
    elif showing == 'passant':
        passant_position = {
            "8": [bRook, bKnight, bBishop, bQueen, bKing, bBishop, bKnight, bRook],
            "7": [empty, bPawn, bPawn, bPawn, bPawn, bPawn, bPawn, bPawn],
            "6": [empty for _ in range(8)],
            "5": [bPawn, empty, empty, wPawn, empty, empty, empty, empty],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [wPawn, wPawn, wPawn, empty, wPawn, wPawn, wPawn, wPawn],
            "1": [wRook, wKnight, wBishop, wQueen, wKing, wBishop, wKnight, wRook]
        }
        display_board(passant_position)
    elif showing == 'passant_two':
        passant_position = {
            "8": [bRook, bKnight, bBishop, bQueen, bKing, bBishop, bKnight, bRook],
            "7": [empty, bPawn, bPawn, bPawn, empty, bPawn, bPawn, bPawn],
            "6": [empty for _ in range(8)],
            "5": [bPawn, empty, empty, wPawn, bPawn, empty, empty, empty],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [wPawn, wPawn, bPawn, empty, bPawn, bPawn, bPawn, bPawn],
            "1": [wRook, wKnight, wBishop, wQueen, wKing, wBishop, wKnight, wRook]
        }
        display_board(passant_position)
    elif showing == 'passant_three':
        passant_position = {
            "8": [bRook, bKnight, bBishop, bQueen, bKing, bBishop, bKnight, bRook],
            "7": [empty, bPawn, bPawn, bPawn, empty, bPawn, bPawn, bPawn],
            "6": [empty, empty, empty, empty, wPawn, empty, empty, empty],
            "5": [bPawn, empty, empty, empty, empty, empty, empty, empty],
            "4": [empty for _ in range(8)],
            "3": [empty for _ in range(8)],
            "2": [wPawn, wPawn, wPawn, empty, wPawn, wPawn, wPawn, wPawn],
            "1": [wRook, wKnight, wBishop, wQueen, wKing, wBishop, wKnight, wRook]
        }
        display_board(passant_position)


def liner():
    # Just a spacer tool to make things more legible on the tutorial.
    print("\n------------------------------------------------------")


def tutorial():
    global flipped

    # Very long function that consists mostly of print text and waiting for the user's input to print even more text.
    # The most complex use it serves is simulating a real game to train the user to use the notation of the
    # software correctly.

    while True:
        print(f"\n{menu_white}====================================================")
        print(text['tutorial'])
        print(f"===================================================={reset}")
        print(text['tutorial_menu'])
        choice = input(text['response3'] + ' ').lower().replace(' ', '').replace('/', '')
        if choice == '1' or choice == 'reglas' or choice == 'rules':
            # We briefly show the basic rules of chess. They were retrieved from the website at the bottom of each one.

            learning_rules = True
            while learning_rules is True:

                # We display the options the user can choose to learn about some rules briefly.
                print(text['rules_choice'].format(menu_white=menu_white, reset=reset))
                print("\n----------------------------")
                print(text['rules_menu'])
                print("----------------------------")
                rule = input(text['response2'] + ' ').lower().replace(' ', '').replace('/', '')
                if rule == '1':
                    # Rule 1 is about the board's composition.
                    liner()
                    print(text['rule1'].format(menu_white=menu_white, reset=reset))
                    liner()

                    # All empty inputs are for the user to click enter or type anything to continue with the
                    # program. This makes it, so they can read the text without it being shifted up by the
                    # immediate following text.
                    input("")

                elif rule == '2':
                    # Rule 2 is about the pieces.
                    liner()
                    print(text['rule2'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '3':
                    # Rule 3 is about how turns work.
                    liner()
                    print(text['rule3'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '4':
                    # Rule 4 is about castling.
                    liner()
                    print(text['rule4'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '5':
                    # Rule 5 is about checking the king.
                    liner()
                    print(text['rule5'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '6':
                    # Rule 6 is about checkmate.
                    liner()
                    print(text['rule6'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '7':
                    # Rule 7 is about drawing a game.
                    liner()
                    print(text['rule7'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '8':
                    # Rule 8 is about pawn promotions.
                    liner()
                    print(text['rule8'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '9':
                    # Rule 9 is about algebraic notation.
                    liner()
                    print(text['rule9'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == '10':
                    # Rule 10 is about the official FIDE rules.
                    liner()
                    print(text['rule10'].format(menu_white=menu_white, reset=reset))
                    liner()
                    input("")

                elif rule == 'back' or rule == '11' or rule == 'atras' or rule == 'volver':
                    # We return to the main tutorial menu.
                    break
                else:
                    # We force the user to choose a valid option
                    print(text['error_option'])

        elif choice == '2' or choice == 'notacion' or choice == 'notation':
            # We explain more in depth about notation and how the program expects the user to write it. We also
            # add a little 'test' to make the user comfortable using it across all special moves and
            # other areas of the game. The positions and moves were done coded in brute force to avoid breaking the
            # main program.

            print(text['program_notation'].format(menu_white=menu_white, reset=reset))
            print(text['notation_explanation1'])
            input("")
            print(text['notation_explanation2'])
            print(text['notation_explanation3'])
            input("")

            # First test showcasing a knight's movement.
            print(text['first_test'].format(menu_white=menu_white, reset=reset), end='')

            # We change the board so its facing black.
            flipped = 1
            tutorial_positions('knight')

            # We force the user to make the right move.
            while True:
                move = input('\n' + text['movement'] + ' ').lower().replace(' ', '')
                if move == 'd4e6':
                    # If the move is right we continue with the program.
                    break
                # Error message reminding the user what type of move it needs to make.
                print(text['error_smith_knight'])

            # When the loop is broken it means that the user made the right move, so we showcase the new board
            # position and print some positive feedback to the user.
            tutorial_positions('knight_moved')
            print(text['well_done'].format(menu_white=menu_white, reset=reset))

            # We force the program to wait for 2 seconds to the user can read the message before continuing.
            t.sleep(2)

            # We change back the side of the board towards white.
            flipped = 0

            # Second test showcasing the king castling.
            print(text['second_test'].format(menu_white=menu_white, reset=reset))
            tutorial_positions('king')

            # Same things as before, just that in this case there are two valid moves.
            while True:
                move = input('\n' + text['movement'] + ' ').lower().replace(' ', '')
                if move == 'e1g1':
                    # Kingside castle.
                    tutorial_positions('king_right')
                    break

                elif move == 'e1c1':
                    # Queenside castle.
                    tutorial_positions('king_left')
                    break

                # Error message telling the user to castle.
                print(text['error_smith_castle'])

            # Positive feedback.
            print(text['well_done'].format(menu_white=menu_white, reset=reset))
            t.sleep(2)

            # Third test showcasing a pawn promotion.
            print(text['third_test'].format(menu_white=menu_white, reset=reset))
            tutorial_positions('promotion')

            # Same thing as before. This time it is made for promotion.
            while True:
                move = input('\n' + text['movement'] + ' ').lower().replace(' ', '')
                if move == 'e7e8=t' or move == 'e7e8=r':
                    tutorial_positions('promoted')
                    break

                # Error message telling the user they need to promote.
                print(text['error_smith_promotion'])

            # Positive feedback.
            print(text['well_done'].format(menu_white=menu_white, reset=reset))
            t.sleep(2)

            # Fourth test showcasing an en passant.
            print(text['fourth_test'].format(menu_white=menu_white, reset=reset))

            # The enemy must move first for an en passant to be possible, so we showcase the board two times
            # (Before the enemy moves, and after).
            tutorial_positions('passant')
            t.sleep(2)

            # We show black's movement.
            tutorial_positions('passant_two')

            # We force the user to make the right move to eat the pawn on en passant.
            while True:
                move = input('\n' + text['movement'] + ' ').lower().replace(' ', '')
                if move == 'd5e6':
                    tutorial_positions('passant_three')
                    break

                # Error message telling the user to make an en passant.
                print(text['error_smith_en_passant'])

            # Positive feedback with a congratulations message since the user finished the test.
            print(str(text['finish_test'].format(menu_white=menu_white, reset=reset)))
            t.sleep(4)

        elif choice == '3' or choice == 'comandos' or choice == 'commands':
            # Basically just the /help command but for people who do not know it exists. It also adds some extra
            # information.

            print(text['tutorial_commands'].format(menu_white=menu_white, reset=reset))
            print(text['tutorial_commands_explanation'])
            print(text['commands_help'].format(menu_white=menu_white, commands0=commands[0], commands1=commands[1],
                                               commands2=commands[2], commands3=commands[3], commands4=commands[4],
                                               commands5=commands[5], commands6=commands[6], commands7=commands[7],
                                               commands8=commands[8], commands9=commands[9], commands10=commands[10],
                                               commands11=commands[11], commands12=commands[12], reset=reset,
                                               white=menu_white))
            input("")
        elif choice == '4' or choice == 'back' or choice == 'menu':
            # We leave this menu.
            break
        else:
            print(text['error_option'])


def program_credits():
    # Credits print function.
    print("\n=====================================================================")
    print(text['credits'])
    print("\n=====================================================================\n")

    input("")


def settings():
    global language, show_coords, change_direction, auto_export_game, text
    # Basically a function that prints the settings and allows the user to invert them. All of them are basically in binary
    # which means that the user can just select them and invert them without having to tell the program what to change it to.

    changing_settings = True
    while changing_settings is True:
        print(f"\n{menu_white}====================================================")
        print(text['settings'])
        print(f"===================================================={reset}")
        print(text['language'].format(menu_white=menu_white, reset=reset, language=language))
        if not show_coords:
            print(text['show_coords_no'].format(menu_white=menu_white, reset=reset))
        else:
            print(text['show_coords_yes'].format(menu_white=menu_white, reset=reset))
        if not change_direction:
            print(text['change_dir_no'].format(menu_white=menu_white, reset=reset))
        else:
            print(text['change_dir_yes'].format(menu_white=menu_white, reset=reset))
        if not auto_export_game:
            print(text['auto_export_no'].format(menu_white=menu_white, reset=reset))
        else:
            print(text['auto_export_yes'].format(menu_white=menu_white, reset=reset))

        print(f"\n{menu_white}===================================================={reset}")

        print(text['make_changes'])
        while True:
            choice = input(text['response2'] + ' ').lower().replace(' ', '')
            if choice == '1':
                if language == 'Español':
                    language = 'English'
                    print("Changing language to english.")
                else:
                    language = 'Español'
                    print("Cambiando el idioma a español.")
                text = load_language_text(language)
                break
            elif choice == '2':
                show_coords = not show_coords
                if not show_coords:
                    print(text['deactivate_show_coords'])
                else:
                    print(text['activate_show_coords'])
                break
            elif choice == '3':
                change_direction = not change_direction
                if not change_direction:
                    print(text['deactivate_change_dir'])
                else:
                    print(text['activate_change_dir'])
                break
            elif choice == '4':
                auto_export_game = not auto_export_game
                if not auto_export_game:
                    print(text['deactivate_export'])
                else:
                    print(text['activate_export'])
                break
            elif choice == '' or choice == '/back' or choice == '/menu':
                changing_settings = False
                break
            else:
                print(text['error_option'])
        while changing_settings is True:
            print(text['change_else'].format(underline=underline, reset=reset))
            choice = input(text['response1'] + ' ')
            if choice in yes:
                break
            elif choice in no or choice == '/back' or choice == '/menu' or choice == '':
                changing_settings = False
                break
            else:
                print(text['error_option'])


def menu():
    global program_over
    # Main menu with all options and paths the user can take (menus, type of matches, etc.).
    print(text['to_continue'].format(underline=underline, reset=reset))
    choice = interface_options()
    if choice == 1:
        try:
            stockfish.reset_engine_parameters()
            game_pvp()
        except KeyboardInterrupt:
            quit(text['quit_message'])
    elif choice == 2:
        try:
            stockfish.reset_engine_parameters()
            game_engine()
        except KeyboardInterrupt:
            quit(text['quit_message'])
    elif choice == 3:
        try:
            tutorial()
        except KeyboardInterrupt:
            quit(text['quit_message'])
    elif choice == 4:
        try:
            settings()
        except KeyboardInterrupt:
            quit(text['quit_message'])
    elif choice == 5:
        try:
            program_credits()
        except KeyboardInterrupt:
            quit(text['quit_message'])
    else:
        program_over = True
        quit(text['quit_message'])


def main():
    while program_over is False:
        # Function that kickstarts the whole program by calling the menu in. It also serves as the main banner of welcome.
        print(f"\n{menu_white}====================================================")
        print(text['welcome'])
        print(f"===================================================={reset}")
        menu()


if __name__ == '__main__':
    # We start the program.
    main()
