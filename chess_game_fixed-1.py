import pygame
from pygame import *
import pygame as pg
import math
import copy

pygame.init()
font.init()

# Окно
wind = pygame.display.set_mode((840, 640))
pygame.display.set_caption('Chess')
clock = pygame.time.Clock()

# Игровые переменные
Turn = 0
PromoteChoice = None
History = []
MoveList = []
Variants = []
select_move_ind = None
last_move = None
game_over = False  # Флаг окончания игры
time_left = [5 * 60, 5 * 60]
last_time_update = [pygame.time.get_ticks(), pygame.time.get_ticks()]

# Флаги первого хода для рокировки
FirstMove = {
    'K0': True, 'R0l': True, 'R0r': True,
    'K1': True, 'R1l': True, 'R1r': True
}

pieces = ['Q', 'R', 'B', 'H']

# Доска
RectList = []
for i in range(8):
    for n in range(4):
        RectList.append(pygame.Rect((n * 160 + (i % 2) * 80, i * 80, 80, 80)))

Board = [
    ['R1', 'H1', 'B1', 'Q1', 'K1', 'B1', 'H1', 'R1'],
    ['p1', 'p1', 'p1', 'p1', 'p1', 'p1', 'p1', 'p1'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P0', 'P0', 'P0', 'P0', 'P0', 'P0', 'P0', 'P0'],
    ['R0', 'H0', 'B0', 'Q0', 'K0', 'B0', 'H0', 'R0']
]

AttackDict = {
    'R': [[0, 1], [1, 0], [0, -1], [-1, 0], 1],
    'B': [[1, 1], [-1, -1], [1, -1], [-1, 1], 1],
    'Q': [[1, 1], [-1, -1], [1, -1], [-1, 1], [0, 1], [1, 0], [0, -1], [-1, 0], 1],
    'H': [[1, 2], [2, 1], [-1, -2], [-2, -1], [-1, 2], [-2, 1], [1, -2], [2, -1], 0],
    'P': [[-1, -1], [1, -1], 0],
    'p': [[-1, 1], [1, 1], 0],
    'K': [[1, 1], [-1, -1], [1, -1], [-1, 1], [0, 1], [1, 0], [0, -1], [-1, 0], 0]
}

def DRawBag():
    pygame.draw.rect(wind, (124, 153, 99), (0, 0, 640, 640))
    for R in RectList:
        pygame.draw.rect(wind, ((250, 246, 225)), R)

def DrawPieces():
    global last_move
    y = 0
    current_board = Board
    for Brd in current_board:
        x = 0
        for B in Brd:
            if last_move and ((x == last_move[0] and y == last_move[1]) or (x == last_move[2] and y == last_move[3])):
                pygame.draw.rect(wind, (196, 194, 181, 50), (x * 80, y * 80, 80, 80))
            if B != '.':
                try:
                    img = pygame.image.load(B + '.png')
                    img = pygame.transform.scale(img, (70, 70))
                    wind.blit(img, (5 + x * 80, 5 + y * 80))
                except:
                    pass
            x += 1
        y += 1

def DrawMoves():
    pygame.draw.rect(wind, (149, 196, 151), (640, 0, 200, 640))
    font_ = pygame.font.SysFont('Small capital', 24)
    start_index = max(0, len(MoveList) - 26)
    for i, move in enumerate(MoveList[start_index:]):
        y_pos = i * 24
        if y_pos > 640:
            break
        if start_index + i == select_move_ind:
            pygame.draw.rect(wind, (100, 150, 255), (640, y_pos, 200, 24))
        else:
            pygame.draw.rect(wind, (50, 50, 50), (640, y_pos, 200, 24))
        move_num = (start_index + i) // 2 + 1
        if i % 2 == 0:
            text = font_.render(f"{move_num}. {move}", True, (222, 222, 222))
        else:
            text = font_.render(f"{move}", True, (220, 220, 220))
        wind.blit(text, (645, y_pos))

def DrawTimer():
    font = pygame.font.SysFont('Small capital', 30)
    white_time = f'{time_left[0] // 60:02}:{time_left[0] % 60:02}'
    black_time = f'{time_left[1] // 60:02}:{time_left[1] % 60:02}'

    # Белый таймер
    pygame.draw.rect(wind, (255, 255, 255), (750, 600, 90, 30))
    pygame.draw.rect(wind, (0, 0, 0), (750, 600, 90, 30), 2)
    text_white = font.render(white_time, True, (0, 0, 0))
    wind.blit(text_white, (760, 605))

    # Черный таймер
    pygame.draw.rect(wind, (0, 0, 0), (650, 600, 90, 30))
    pygame.draw.rect(wind, (255, 255, 255), (650, 600, 90, 30), 2)
    text_black = font.render(black_time, True, (255, 255, 255))
    wind.blit(text_black, (660, 605))

def CheckShah(B_W):
    y = 0
    for Brd in Board:
        x = 0
        for B in Brd:
            if B != '.' and B[1] != B_W:
                for shift in AttackDict[B[0]][:-1]:
                    pos = [x, y]
                    for _ in range(AttackDict[B[0]][-1] * 6 + 1):
                        pos[0] += shift[0]
                        pos[1] += shift[1]
                        if not (0 <= pos[0] <= 7 and 0 <= pos[1] <= 7):
                            break
                        target = Board[pos[1]][pos[0]]
                        if target != '.':
                            if target == 'K' + B_W:
                                return True
                            else:
                                break
                    if AttackDict[B[0]][-1] == 0:
                        break
            x += 1
        y += 1
    return False

def ShowVariants(x, y):
    global Variants
    Variants = []
    B = Board[y][x]
    for shift in AttackDict[B[0]][:-1]:
        pos = [x, y]
        for _ in range(AttackDict[B[0]][-1] * 6 + 1):
            pos[0] += shift[0]
            pos[1] += shift[1]
            if not (0 <= pos[0] <= 7 and 0 <= pos[1] <= 7):
                break
            if Board[pos[1]][pos[0]] != '.':
                if Board[pos[1]][pos[0]][1] != B[1]:
                    Variants.append([pos[0], pos[1]])
                break
            elif B[0] not in ['p', 'P']:
                Variants.append([pos[0], pos[1]])

    # Пешки
    if B[0] == 'p':
        if y + 1 <= 7 and Board[y + 1][x] == '.':
            Variants.append([x, y + 1])
            if y == 1 and Board[y + 2][x] == '.':
                Variants.append([x, y + 2])
        for dx in [-1, 1]:
            nx, ny = x + dx, y + 1
            if 0 <= nx <= 7 and 0 <= ny <= 7 and Board[ny][nx] != '.' and Board[ny][nx][1] != B[1]:
                Variants.append([nx, ny])
    elif B[0] == 'P':
        if y - 1 >= 0 and Board[y - 1][x] == '.':
            Variants.append([x, y - 1])
            if y == 6 and Board[y - 2][x] == '.':
                Variants.append([x, y - 2])
        for dx in [-1, 1]:
            nx, ny = x + dx, y - 1
            if 0 <= nx <= 7 and 0 <= ny <= 7 and Board[ny][nx] != '.' and Board[ny][nx][1] != B[1]:
                Variants.append([nx, ny])

    # Рокировка
    if B[1] == '0' and y == 7 and x == 4:
        if FirstMove['K0'] and FirstMove['R0r']:
            if Board[7][5] == '.' and Board[7][6] == '.':
                safe = True
                for t in [(5, 7), (6, 7)]:
                    Board[t[1]][t[0]] = B
                    if CheckShah('0'): safe = False
                    Board[t[1]][t[0]] = '.'
                if safe:
                    Variants.append([6, 7])
        if FirstMove['K0'] and FirstMove['R0l']:
            if Board[7][1] == '.' and Board[7][2] == '.' and Board[7][3] == '.':
                safe = True
                for t in [(3, 7), (2, 7)]:
                    Board[t[1]][t[0]] = B
                    if CheckShah('0'): safe = False
                    Board[t[1]][t[0]] = '.'
                if safe:
                    Variants.append([2, 7])
    elif B[1] == '1' and y == 0 and x == 4:
        if FirstMove['K1'] and FirstMove['R1r']:
            if Board[0][5] == '.' and Board[0][6] == '.':
                safe = True
                for t in [(5, 0), (6, 0)]:
                    Board[t[1]][t[0]] = B
                    if CheckShah('1'): safe = False
                    Board[t[1]][t[0]] = '.'
                if safe:
                    Variants.append([6, 0])
        if FirstMove['K1'] and FirstMove['R1l']:
            if Board[0][1] == '.' and Board[0][2] == '.' and Board[0][3] == '.':
                safe = True
                for t in [(3, 0), (2, 0)]:
                    Board[t[1]][t[0]] = B
                    if CheckShah('1'): safe = False
                    Board[t[1]][t[0]] = '.'
                if safe:
                    Variants.append([2, 0])

    # Проверка на шах после хода
    ForDeletion = []
    Board[y][x] = '.'
    for V in Variants:
        remember = Board[V[1]][V[0]]
        Board[V[1]][V[0]] = B
        if CheckShah(B[1]):
            ForDeletion.append(V)
        Board[V[1]][V[0]] = remember
    Board[y][x] = B
    for Del in ForDeletion:
        Variants.remove(Del)

def CheckCheckMate(B_W):
    global game_over
    y = 0
    for Brd in Board:
        x = 0
        for B in Brd:
            if B != '.' and B[1] == B_W:
                ShowVariants(x, y)
                if len(Variants) > 0:
                    return 0
            x += 1
        y += 1
    if CheckShah(B_W):
        game_over = True
        return 1
    game_over = False
    return 2

def to_chess_notation(x, y):
    columns = 'abcdefgh'
    rows = '87654321'
    return columns[x] + rows[y]

# Основной цикл игры
DRawBag()
DrawPieces()
DrawMoves()
DrawTimer()


while True:
    if not game_over:
        current_time = pygame.time.get_ticks()
        delta = (current_time - last_time_update[Turn]) / 1000
        if delta >= 1:
            time_left[Turn] -= 1
            last_time_update[Turn] = current_time
            if time_left[Turn] < 0:
                time_left[Turn] = 0
                game_over = True
                msg = 'TIME OUT! WHITE WON' if Turn == 1 else 'TIME OUT! BLACK WON'
                text = pygame.font.SysFont('Arial', 36, bold=True).render(msg, True, (255, 0, 0))
                rect = text.get_rect(center=(320, 300))
                pygame.draw.rect(wind, (0, 0, 0), (rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10))
                wind.blit(text, rect.topleft)
                pygame.display.update()
        DrawTimer()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            exit()

        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos

            # Клик по истории ходов
            if 640 <= mx < 840 and 0 <= my < 640:
                if game_over:
                    index = my // 24
                    if index < len(History):
                        select_move_ind = index
                        Board = copy.deepcopy(History[index])
                        DRawBag()
                        DrawPieces()
                        DrawMoves()
                        pygame.display.update()
                continue

            if e.button == 1:
                if PromoteChoice:
                    px, py = PromoteChoice
                    color = Board[py][px][1]
                    for i, p in enumerate(pieces):
                        if 100 + i*70 <= mx <= 160 + i*70 and 270 <= my <= 330:
                            Board[py][px] = p + color
                            PromoteChoice = None
                            Turn = 1 - Turn
                            MoveList.append(f'{p}{color}: {to_chess_notation(remember[0], remember[1])} -> {to_chess_notation(px, py)}')
                            History.append(copy.deepcopy(Board))
                            check = CheckCheckMate(str(Turn))
                            DRawBag()
                            DrawPieces()
                            DrawMoves()
                            if check == 1:
                                msg = 'MAT! WHITE WON' if Turn == 1 else 'MAT! BLACK WON'
                                text = pygame.font.SysFont('Arial', 36, bold=True).render(msg, True, (255, 215, 0))
                                rect = text.get_rect(center=(320, 300))
                                pygame.draw.rect(wind, (0, 0, 0), (rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10))
                                wind.blit(text, rect.topleft)
                            elif check == 2:
                                text = pygame.font.SysFont('Arial', 36, bold=True).render("PAT! DRAW", True, (255, 255, 255))
                                rect = text.get_rect(center=(320, 300))
                                pygame.draw.rect(wind, (0, 0, 0), (rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10))
                                wind.blit(text, rect.topleft)
                            pygame.display.update()
                            break
                    continue

            if game_over:
                continue

            if e.button == 1:
                x, y = math.floor(mx / 80), math.floor(my / 80)
                if Board[y][x] != '.' and Board[y][x][1] == str(Turn):
                    ShowVariants(x, y)
                    remember = [x, y]
                    DRawBag()
                    DrawPieces()
                    for V in Variants:
                        pygame.draw.circle(wind, (200, 200, 200), (V[0]*80 + 40, V[1]*80 + 40), 10)
                    pygame.display.update()

        if e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:
                mx, my = e.pos
                x, y = math.floor(mx / 80), math.floor(my / 80)
                if [x, y] in Variants:
                    Board[y][x] = Board[remember[1]][remember[0]]
                    piece = Board[y][x][0]
                    color = Board[y][x][1]
                    MoveList.append(f'{piece}{color}: {to_chess_notation(remember[0], remember[1])} -> {to_chess_notation(x, y)}')
                    History.append(copy.deepcopy(Board))
                    last_move = [remember[0], remember[1], x, y]

                    # Рокировка
                    B = Board[y][x]
                    if B[0] == 'K':
                        if B[1] == '0':
                            if remember == [4, 7] and [x, y] == [6, 7] and FirstMove['K0'] and FirstMove['R0r']:
                                Board[7][6] = Board[7][4]
                                Board[7][4] = '.'
                                Board[7][5] = Board[7][7]
                                Board[7][7] = '.'
                                FirstMove['K0'] = False
                                FirstMove['R0r'] = False
                            elif remember == [4, 7] and [x, y] == [2, 7] and FirstMove['K0'] and FirstMove['R0l']:
                                Board[7][2] = Board[7][4]
                                Board[7][4] = '.'
                                Board[7][3] = Board[7][0]
                                Board[7][0] = '.'
                                FirstMove['K0'] = False
                                FirstMove['R0l'] = False
                        elif B[1] == '1':
                            if remember == [4, 0] and [x, y] == [6, 0] and FirstMove['K1'] and FirstMove['R1r']:
                                Board[0][6] = Board[0][4]
                                Board[0][4] = '.'
                                Board[0][5] = Board[0][7]
                                Board[0][7] = '.'
                                FirstMove['K1'] = False
                                FirstMove['R1r'] = False
                            elif remember == [4, 0] and [x, y] == [2, 0] and FirstMove['K1'] and FirstMove['R1l']:
                                Board[0][2] = Board[0][4]
                                Board[0][4] = '.'
                                Board[0][3] = Board[0][0]
                                Board[0][0] = '.'
                                FirstMove['K1'] = False
                                FirstMove['R1l'] = False

                    # Обновление флагов
                    if Board[remember[1]][remember[0]][0] == 'K0':
                        FirstMove['K0'] = False
                    elif Board[remember[1]][remember[0]][0] == 'K1':
                        FirstMove['K1'] = False
                    elif remember == [0, 7]:
                        FirstMove['R0l'] = False
                    elif remember == [7, 7]:
                        FirstMove['R0r'] = False
                    elif remember == [0, 0]:
                        FirstMove['R1l'] = False
                    elif remember == [7, 0]:
                        FirstMove['R1r'] = False

                    Board[remember[1]][remember[0]] = '.'
                    if Board[y][x][0] in ['P', 'p'] and (y == 0 or y == 7):
                        PromoteChoice = [x, y]
                    else:
                        Turn = 1 - Turn
                        check = CheckCheckMate(str(Turn))
                        DRawBag()
                        DrawPieces()
                        DrawMoves()
                        if check == 1:
                            msg = 'MAT! WHITE WON' if Turn == 1 else 'MAT! BLACK WON'
                            text = pygame.font.SysFont('Arial', 36, bold=True).render(msg, True, (255, 215, 0))
                            rect = text.get_rect(center=(320, 300))
                            pygame.draw.rect(wind, (0, 0, 0), (rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10))
                            wind.blit(text, rect.topleft)
                        elif check == 2:
                            text = pygame.font.SysFont('Arial', 36, bold=True).render("PAT! DRAW", True, (255, 255, 255))
                            rect = text.get_rect(center=(320, 300))
                            pygame.draw.rect(wind, (0, 0, 0), (rect.x - 5, rect.y - 5, rect.width + 10, rect.height + 10))
                            wind.blit(text, rect.topleft)
                        pygame.display.update()
                else:
                    DRawBag()
                    DrawPieces()
                    DrawMoves()
                    Variants = []
                pygame.display.update()

    if PromoteChoice:
        x, y = PromoteChoice
        color = Board[y][x][1]
        pygame.draw.rect(wind, (200, 200, 200), (90, 260, 300, 100))
        pygame.draw.rect(wind, (0, 0, 0), (90, 260, 300, 100), 2)
        for i, p in enumerate(pieces):
            try:
                img = pygame.image.load(p + color + '.png')
                img = pygame.transform.scale(img, (60, 60))
                wind.blit(img, (100 + i*70, 270))
            except:
                font = pygame.font.SysFont('Arial', 40)
                text_color = (0, 0, 0) if color == '0' else (255, 255, 255)
                text = font.render(p, True, text_color)
                wind.blit(text, (120 + i * 70, 280))
            pygame.draw.rect(wind, (0, 0, 0), (100 + i * 70, 270, 60, 60), 2)

    pygame.display.update()
    clock.tick(60)