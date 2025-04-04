import pygame as p

from Chess import ChessEngine

WIDTH = HEIGHT = 512 # tong chieu dai va chieu rong cua ca cai bang
DIMENSION = 8 # so o can thiet cho moi hang
SQ_SIZE = HEIGHT // DIMENSION # chieu dai va chieu rong o vuong
MAX_FPS = 15 # dung cho animation , so buc hinh/ giay
IMAGES = {} # dictionary cho images

'''
khoi tao images
'''
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    # vong lap load images
    for piece in pieces:
        IMAGES[piece] =p.transform.scale(p.image.load("images/" + piece + ".png"),(SQ_SIZE,SQ_SIZE))



'''
handle user input va update graphics
'''

def main():
    p.init() # khoi tao cac module cua thu vien pygame
    screen = p.display.set_mode((WIDTH,HEIGHT)) # tao screen
    clock = p.time.Clock() # khởi tạo đồng hồ để theo dõi thời gian giữa các khung hình
    screen.fill(p.Color("white")) #Tô nền cho man hinh
    gs = ChessEngine.GameState() # khoi tao class GameState va gan vao bien 'gs'
    loadImages() #khoi tao load image
    running = True

    #keep track of the last click of the user (tuple: (rpw,col))
    sqSelected = ()
    #keep track of the player clicks (two tuple)
    playerClicks = []

    # all valid move variable
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move id made

    while running: #hàm chạy trong suốt quá trình game chạy
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) location of mouse

                # lay vi tri o vuong (so nguyen)
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                #check location selected
                if sqSelected == (row,col): #vi tri cu => undo select
                    # reset player click
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected)

                # check the second click
                if len(playerClicks) == 2:
                    #call move class
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())


                    # #*print all valid move to debug
                    # for i in validMoves:
                    #     print(i.startRow,i.startCol , i.endRow,i.endCol)

                    # check valid moves to make moves
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()  # reset user clicks
                            playerClicks = []  # reset array for next move choice
                    if not moveMade:
                        #reset select piece
                        playerClicks = [sqSelected]


            # key handlers
            elif e.type == p.KEYDOWN: #check a key button
                if e.key == p.K_b and len(gs.moveLog) != 0:
                    gs.undoMove()
                    moveMade = True

        #if a move is made then regenerate all the validmoves for the next move
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs) #goi ham drawgamestate
        clock.tick(MAX_FPS)
        p.display.flip() #cập nhật lại màn hình khi có sự thay đổi


'''
khoi tao graphics and GameState
'''
def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)



'''
ve cac o vuong tren bang:

WIDTH = HEIGHT = 512 # tong chieu dai va chieu rong cua ca cai bang
DIMENSION = 8 # so o can thiet cho moi hang
SQ_SIZE = HEIGHT // DIMENSION # chieu dai va chieu rong o vuong
'''
def drawBoard(screen):
    for row in range(8):
        for col in range(8):
            if ((row + col)%2) == 0: #tạo đan xen 2 màu theo hàng và cột
                p.draw.rect(screen,"white", (col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, "gray", (col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
draw cac quan co

IMAGES = {} # dictionary cho images
'''
def drawPieces(screen,board):

    ## code drawPieces o buoc khoi tao
    # Whitepieces = ['wR', 'wN', 'wB', 'wK', 'wQ','wB', 'wN', 'wR']
    # Blackpieces = ['bR', 'bN', 'bB', 'bK', 'bQ', 'bB', 'bN', 'bR']
    #
    # for row in range(8):
    #     screen.blit(IMAGES[Whitepieces[row]],(row*SQ_SIZE, SQ_SIZE))
    #     screen.blit(IMAGES['wp'], (row*SQ_SIZE, 2*SQ_SIZE))
    #
    #     screen.blit(IMAGES['bp'], (row*SQ_SIZE, 7*SQ_SIZE))
    #     screen.blit(IMAGES[Blackpieces[row]], (row*SQ_SIZE, 8*SQ_SIZE))

    ##code drawPieces o buoc khoi tao + cac trang thai khi running
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": #not empty place
                screen.blit(IMAGES[piece],p.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE,SQ_SIZE))


if __name__ == "__main__":
    main()



