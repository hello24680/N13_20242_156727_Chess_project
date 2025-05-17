import pygame as p
import ChessEngine, AI
import sys
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

OUTER_BORDER = 15
INNER_BORDER = 10
BORDER_OFFSET = OUTER_BORDER + INNER_BORDER  # Tổng offset từ góc trái



def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("../images/" + piece + ".png"), (SQUARE_SIZE*0.75, SQUARE_SIZE*0.75))


def main():
    p.init()
    depth = showDifficultyMenu()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH + 2 * BORDER_OFFSET,
                                 BOARD_HEIGHT + 2 * BORDER_OFFSET))
    clock = p.time.Clock()
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False
    animate = False
    loadImages()
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    player_one = True
    player_two = False

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = (location[0] - BORDER_OFFSET) // SQUARE_SIZE
                    row = (location[1] - BORDER_OFFSET) // SQUARE_SIZE
                    if 0 <= row < 8 and 0 <= col < 8:
                        if square_selected == (row, col) or col >= 8:
                            square_selected = ()
                            player_clicks = []
                        else:
                            square_selected = (row, col)
                            player_clicks.append(square_selected)
                        if len(player_clicks) == 2 and human_turn:
                            move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:
                                    game_state.makeMove(valid_moves[i])
                                    move_made = True
                                    animate = True
                                    square_selected = ()
                                    player_clicks = []
                            if not move_made:
                                player_clicks = [square_selected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == p.K_r:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue()
                move_finder_process = Process(target=AI.findBestMove, args=(game_state, valid_moves, return_queue, depth))
                move_finder_process.start()

            if not move_finder_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = AI.findRandomMove(valid_moves)
                game_state.makeMove(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

        drawGameState(screen, game_state, valid_moves, square_selected)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")
        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, game_state, valid_moves, square_selected):
    drawBoard(screen)
    highlightSquares(screen, game_state, valid_moves, square_selected)
    drawPieces(screen, game_state.board)


def drawBoard(screen):
    global colors
    colors = [(238, 238, 210), (118, 150, 86)]  # RGB cho beige và black

    board_x = BORDER_OFFSET
    board_y = BORDER_OFFSET

    outer_rect = p.Rect(0, 0,
                        BOARD_WIDTH + 2 * BORDER_OFFSET,
                        BOARD_HEIGHT + 2 * BORDER_OFFSET)
    p.draw.rect(screen, (118, 150, 86), outer_rect)  # viền ngoài đen

    inner_rect = p.Rect(OUTER_BORDER, OUTER_BORDER,
                        BOARD_WIDTH + 2 * INNER_BORDER,
                        BOARD_HEIGHT + 2 * INNER_BORDER)
    p.draw.rect(screen, (238, 238, 210), inner_rect)  # viền trong beige

    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[(row + column) % 2]
            square = p.Rect(board_x + column * SQUARE_SIZE,
                            board_y + row * SQUARE_SIZE,
                            SQUARE_SIZE, SQUARE_SIZE)
            p.draw.rect(screen, color, square)

    font = p.font.SysFont("Roboto", 20, True, False)
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    numbers = ['8', '7', '6', '5', '4', '3', '2', '1']

    total_border = INNER_BORDER + OUTER_BORDER

    # Vẽ chữ cái a-h phía dưới viền đen ngoài cùng
    for i in range(DIMENSION):
        text_surface = font.render(letters[i], True, (245, 245, 220))  # chữ màu beige trên nền đen
        x_pos = OUTER_BORDER + INNER_BORDER + i * SQUARE_SIZE + SQUARE_SIZE // 2 - text_surface.get_width() // 2
        y_pos_bottom = BOARD_HEIGHT + total_border + (OUTER_BORDER // 2) + 3
        screen.blit(text_surface, (x_pos, y_pos_bottom))

    # Vẽ số 1-8 ở bên trái viền đen ngoài cùng
    for i in range(DIMENSION):
        text_surface = font.render(numbers[i], True, (245, 245, 220))  # chữ màu beige
        y_pos = OUTER_BORDER + INNER_BORDER + i * SQUARE_SIZE + SQUARE_SIZE // 2 - text_surface.get_height() // 2
        x_pos_left = (OUTER_BORDER // 2) - (text_surface.get_width() // 2)
        screen.blit(text_surface, (x_pos_left, y_pos))



def highlightSquares(screen, game_state, valid_moves, square_selected):
    s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
    s.set_alpha(100)

    if game_state.move_log:
        last_move = game_state.move_log[-1]
        s.fill(p.Color('green'))
        screen.blit(s, (BORDER_OFFSET + last_move.end_col * SQUARE_SIZE,
                        BORDER_OFFSET + last_move.end_row * SQUARE_SIZE))

    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == ('w' if game_state.white_to_move else 'b'):
            s.fill(p.Color('blue'))
            screen.blit(s, (BORDER_OFFSET + col * SQUARE_SIZE,
                            BORDER_OFFSET + row * SQUARE_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (BORDER_OFFSET + move.end_col * SQUARE_SIZE,
                                    BORDER_OFFSET + move.end_row * SQUARE_SIZE))


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                # Tính vị trí căn giữa
                x = OUTER_BORDER + INNER_BORDER + col * SQUARE_SIZE + (SQUARE_SIZE - SQUARE_SIZE*0.75) // 2
                y = OUTER_BORDER + INNER_BORDER + row * SQUARE_SIZE + (SQUARE_SIZE - SQUARE_SIZE*0.75) // 2
                screen.blit(IMAGES[piece], p.Rect(x, y, SQUARE_SIZE*0.75, SQUARE_SIZE*0.75))


def drawMoveLog(screen, game_state, font):
    move_log_rect = p.Rect(BOARD_WIDTH + 2 * BORDER_OFFSET, 0,
                           MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT + 2 * BORDER_OFFSET)
    p.draw.rect(screen, p.Color('gray'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        text_object = font.render(text, True, p.Color('black'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BORDER_OFFSET + BOARD_WIDTH / 2 - text_object.get_width() / 2,
        BORDER_OFFSET + BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


def animateMove(move, screen, board, clock):
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row = move.start_row + d_row * frame / frame_count
        col = move.start_col + d_col * frame / frame_count
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(BORDER_OFFSET + move.end_col * SQUARE_SIZE,
                            BORDER_OFFSET + move.end_row * SQUARE_SIZE,
                            SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(BORDER_OFFSET + move.end_col * SQUARE_SIZE,
                                    BORDER_OFFSET + enpassant_row * SQUARE_SIZE,
                                    SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(
            BORDER_OFFSET + col * SQUARE_SIZE,
            BORDER_OFFSET + row * SQUARE_SIZE,
            SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_button(screen, rect, base_color, text, font, text_color, is_hovered):
    # Làm sáng màu khi hover
    color = [min(255, c + 30) for c in base_color] if is_hovered else base_color
    p.draw.rect(screen, color, rect, border_radius=12)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def showDifficultyMenu():
    p.init()
    screen = p.display.set_mode((400, 300))
    p.display.set_caption("Chọn độ khó")

    font = p.font.SysFont("Arial", 24)
    title_font = p.font.SysFont("Arial", 32, bold=True)

    # Định nghĩa nút
    easy_button = p.Rect(125, 100, 150, 45)
    hard_button = p.Rect(125, 170, 150, 45)

    # Màu sắc
    background_color = (255, 245, 238)
    easy_color = (222, 184, 135)
    hard_color = (139, 115, 85)

    while True:
        screen.fill(background_color)
        mouse_pos = p.mouse.get_pos()

        # Vẽ tiêu đề
        title_surface = title_font.render("Select Difficulty", True, (33, 33, 33))
        screen.blit(title_surface, (200 - title_surface.get_width() // 2, 30))

        # Vẽ các nút với hiệu ứng hover
        draw_button(screen, easy_button, easy_color, "Easy", font, (255, 255, 255), easy_button.collidepoint(mouse_pos))
        draw_button(screen, hard_button, hard_color, "Hard", font, (255, 255, 255), hard_button.collidepoint(mouse_pos))

        # Xử lý sự kiện
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(e.pos):
                    return 2  # độ khó dễ
                elif hard_button.collidepoint(e.pos):
                    return 3  # độ khó khó

        p.display.flip()

if __name__ == "__main__":
    main()
