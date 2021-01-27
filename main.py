import os
import sys
from random import choice

import pygame

SCORES = open("data/scores.txt").read().split()
pygame.init()
size = WIDTH, HEIGHT = 700, 650
SCREEN = pygame.display.set_mode(size)
SCREEN.fill('black')
FPS = 50
clock = pygame.time.Clock()
c1 = pygame.Color((0, 0, 0))  # у меня вообще дальтонизм не судите строга
c2 = pygame.Color((255, 255, 255))
c3 = pygame.Color((140, 255, 251))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_text(screen, text, text_coord, font, text_BACK_on_screen=True):
    coords = []
    for i in range(len(text)):
        coords.append(text_coord)
        string_rendered = font.render(text[i], True, c3, c1)
        screen.blit(string_rendered, (10, text_coord))
        if text_BACK_on_screen and i == len(text) - 2:
            text_coord += 20
        text_coord += 9
        text_coord += string_rendered.get_rect().height
    return coords


def select_text(screen, font, text, selected, coords, m):
    screen.blit(font.render(text[selected], True, c3, c1), (10, coords[selected]))
    selected = (selected + m) % len(text)
    screen.blit(font.render(text[selected], True, c2, c1), (10, coords[selected]))
    return selected


def terminate():
    s = open('data/scores.txt', mode='w')
    s.write(' '.join(SCORES))  # перед выходом из программы заносим изменения в файл с рекордами
    pygame.quit()
    sys.exit()


def start_screen():
    screen = pygame.Surface(size)
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text = "Нажмите любую клавишу чтобы продолжить"
    string = font.render(text, True, pygame.Color('orange'))
    rect = string.get_rect()
    rect.left = WIDTH // 2 - rect.width // 2
    rect.top = HEIGHT * 2 // 3
    screen.blit(string, rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        SCREEN.blit(screen, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


ALL_FIGURES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']


class Field:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[''] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        self.score = 0
        self.difficulty = 1
        self.upd_level()
        self.end = False
        self.coords_y = []
        self.coords_x = []

    def upd_level(self):
        self.level = self.score // 1500 + self.difficulty
        self.speed = self.speed = 1.5 * 1.4 ** self.level

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(4):
            self.board[self.coords_y[i]][self.coords_x[i]] = self.color
        s = self.cell_size
        screen.fill('white', (self.left, self.top, s * self.width, s * self.height))
        for i in range(self.width):
            for j in range(self.height):
                if not self.board[j][i]:
                    screen.fill('black', (self.left + i * s + 1, self.top + j * s + 1, s - 2, s - 2))
                else:
                    screen.fill(self.board[j][i], (self.left + i * s + 1, self.top + j * s + 1, s - 2, s - 2))
        for i in range(4):
            self.board[self.coords_y[i]][self.coords_x[i]] = ''

    def figure(self, type):
        if 0 in self.coords_y or 1 in self.coords_y or 2 in self.coords_y or 3 in self.coords_y:
            self.end = True
        if type == 'I':
            self.coords_x = [self.width // 2, self.width // 2, self.width // 2, self.width // 2]
            self.coords_y = [0, 1, 2, 3]
            self.color = (0, 255, 255)
        elif type == 'J':
            self.coords_x = [self.width // 2, self.width // 2, self.width // 2, self.width // 2 - 1]
            self.coords_y = [0, 1, 2, 2]
            self.color = 'blue'
        elif type == 'L':
            self.coords_x = [self.width // 2, self.width // 2, self.width // 2, self.width // 2 + 1]
            self.coords_y = [0, 1, 2, 2]
            self.color = 'orange'
        elif type == 'O':
            self.coords_x = [self.width // 2, self.width // 2, self.width // 2 - 1, self.width // 2 - 1]
            self.coords_y = [0, 1, 1, 0]
            self.color = 'yellow'
        elif type == 'S':
            self.coords_x = [self.width // 2 + 1, self.width // 2, self.width // 2, self.width // 2 - 1]
            self.coords_y = [0, 0, 1, 1]
            self.color = 'green'
        elif type == 'T':
            self.coords_x = [self.width // 2, self.width // 2, self.width // 2 + 1, self.width // 2 - 1]
            self.coords_y = [0, 1, 1, 1]
            self.color = 'purple'
        else:
            self.coords_x = [self.width // 2 - 1, self.width // 2, self.width // 2, self.width // 2 + 1]
            self.coords_y = [0, 0, 1, 1]
            self.color = 'red'
        self.next_figure = choice(ALL_FIGURES)

    def update(self):
        for i in range(4):
            self.coords_y[i] += 1
        for i in range(4):
            if self.coords_y[i] == self.height or self.board[self.coords_y[i]][self.coords_x[i]]:
                for i in range(4):
                    self.board[self.coords_y[i] - 1][self.coords_x[i]] = self.color
                self.figure(self.next_figure)
                return

    def rotate(self, r):
        x, y = self.coords_x[1], self.coords_y[1]  # координаты центра фигуры
        tx = self.coords_x[:]  # временные переменные, чтобы не делать заранее ненужные действия
        ty = self.coords_y[:]
        for i in range(4):
            if i == 1:  # координаты центра менять не надо
                continue
            x1, y1 = tx[i] - x, ty[i] - y
            tx[i] += (y1 * r - x1)  # если r==1 то фигура поворачивается вправо, если r==-1 - влево
            ty[i] -= (x1 * r + y1)
            if not 0 <= tx[i] < self.width or ty[i] > self.height or self.board[ty[i]][tx[i]]:  # если нельзя повернуть
                return  # то не прододжаем работу метода (временнные переменные пригодились)
            if x1 * r == -2:
                if self.board[self.coords_y[0] + 1][self.coords_x[0]]:  # специальная проверка для палки
                    return
                for i in range(4):  # если фигура - палка, расположенная горизонтально, то ее надо подвинуть вниз
                    ty[i] -= 1

        self.coords_x = tx  # сохраняем новые координаты
        self.coords_y = ty

    def move(self, side):
        tx = self.coords_x[:]  # временная переменная, чтобы не делать заранее ненужные действия
        for i in range(4):
            tx[i] += side
            if not -1 < tx[i] < self.width or self.board[self.coords_y[i]][tx[i]]:
                return
        self.coords_x = tx

    def check_rows(self):
        x = 0
        self.deleted = []
        for i in range(self.height):
            if all(self.board[i]):
                self.board = [[''] * 10] + self.board[:i] + self.board[i + 1:]
                x += 1
                self.deleted = [i]
        if not x:
            return False
        self.deleted.append(x)
        if x == 1:
            self.score += 100
        elif x == 2:
            self.score += 300
        elif x == 3:
            self.score += 700
        elif x == 4:
            self.score += 1500
        self.upd_level()
        return True


FIELD_WIDTH = 10
FIELD_HEIGHT = 20
pygame.display.set_caption("Tetris")


def frame(screen, x, y, w, h):  # рамка для текста or smth
    screen.fill('white', (x - 1, y - 1, w + 2, h + 2))
    screen.fill(c1, (x, y, w, h))


field = Field(FIELD_WIDTH, FIELD_HEIGHT)


def main_screen():
    screen = pygame.Surface(size)
    screen.fill('black')
    fon = pygame.transform.scale(load_image('fon1.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    global field
    field = Field(FIELD_WIDTH, FIELD_HEIGHT)
    field.set_view(200, 25, 30)
    field.figure(choice(ALL_FIGURES))
    field.render(screen)
    frame(screen, 510, field.top + 1, 180, 200)
    frame(screen, 10, field.top + 60, 180, 70)
    frame(screen, 10, field.top + 1, 180, 27)
    next_figure = pygame.transform.scale(load_image(field.next_figure + '.png'), (180, 180))
    screen.blit(next_figure, (510, field.top + 20))
    font = pygame.font.Font(None, 35)
    string1, string2 = font.render("SCORE:", True, pygame.Color('white')), font.render(str(field.score), True,
                                                                                       pygame.Color('white'))
    rect = pygame.Rect(10, field.top + 3 + 60, 180, 35)
    screen.blit(string1, rect)
    screen.blit(string2, rect.move(0, 35))
    screen.blit(font.render("NEXT:", True, pygame.Color('white')), (511, field.top))
    screen.blit(font.render("LEVEL", True, pygame.Color('white')), (11, field.top + 3))
    screen.blit(font.render(str(field.level), True, pygame.Color('white'), pygame.Color('black')), (100, field.top + 3))
    x = 0
    mod = 1
    SCREEN.blit(screen, (0, 0))
    pygame.display.flip()
    while not field.end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_LEFT:
                    field.rotate(-1)
                elif key == pygame.K_RIGHT:
                    field.rotate(1)
                elif key == pygame.K_a:
                    field.move(-1)
                elif key == pygame.K_d:
                    field.move(1)
                elif key == pygame.K_s:
                    mod = 8
                elif key == pygame.K_ESCAPE:
                    if not pause():
                        return True
                    screen.blit(font.render(str(field.level), True, pygame.Color('white'), pygame.Color('black')),
                                (100, field.top + 3))
                field.render(screen)
                SCREEN.blit(screen, (0, 0))
                pygame.display.flip()
            if event.type == pygame.KEYUP and event.key == pygame.K_s:
                mod = 1
        x += clock.tick()
        if x > 1000 // (field.speed * mod):
            x = 0
            field.update()
            next_figure = pygame.transform.scale(load_image(field.next_figure + '.png'), (180, 180))
            screen.blit(next_figure, (510, field.top + 20))
            if field.check_rows():  #изменение очков
                string = font.render(str(field.score), True, pygame.Color('white'), pygame.Color('black'))
                screen.blit(string, rect.move(0, 35))
                screen.blit(font.render(str(field.level), True, pygame.Color('white'), pygame.Color('black')),
                            (100, field.top + 3))
            field.render(screen)
        SCREEN.blit(screen, (0, 0))
        pygame.display.flip()
    global SCORES
    SCORES.append(str(field.score))
    SCORES = sorted(SCORES, reverse=True, key=lambda x: int(x))[:5]
    game_over(screen, 1000 // field.speed)
    return True


def pause():
    c1 = pygame.Color((0, 0, 0))  # у меня вообще дальтонизм не судите строга
    c2 = pygame.Color((255, 255, 255))
    c3 = pygame.Color((140, 255, 251))
    screen = pygame.Surface((210, 250))
    text = ["Resume", "Restart", "Controls", "Change difficulty", "Main menu", "Exit"]
    frame(screen, 1, 1, 208, 248)
    selected = 0
    font = pygame.font.Font(None, 30)
    text_coord = 30
    coords = load_text(screen, text, text_coord, font)
    screen.blit(font.render(text[selected], True, c2), (10, coords[selected]))
    screen.blit(pygame.transform.scale(load_image('pause.png'), (50, 50)), (150, 10))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = select_text(screen, font, text, selected, coords, 1)
                elif event.key == pygame.K_UP:
                    selected = select_text(screen, font, text, selected, coords, -1)
                elif event.key == pygame.K_ESCAPE:
                    return True
                elif event.key == 13:  # у меня не работает K_ENTER, и K_enter, и ENTER тожe
                    if selected == 5:
                        terminate()
                    elif selected == 4:
                        main_menu()
                        return False
                    elif selected == 3:
                        global field
                        field = change_difficulty(field)
                    elif selected == 2:
                        controls()
                    elif selected == 1:
                        return False
                    elif selected == 0:
                        return True
        SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
        pygame.display.flip()
        clock.tick(FPS)


def game_over(screen, speed):
    pic = pygame.transform.scale(load_image("game over.jpg"), (298, 148))
    t = 0
    for i in range(8):
        SCREEN.blit(screen, (0, 0))
        SCREEN.blit(pic, (WIDTH // 2 - 149, 26 + 30 * i))  # со скоростью падения фигурок летит типа прекольно
        pygame.display.flip()
        while t < speed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN:
                    main_menu()
                    return
            t += clock.tick()
        t = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.K_DOWN:
                main_menu()
                return


def main_menu():
    screen = pygame.Surface((210, 250))
    text = ['New game', 'Records', 'Controls', 'Exit']
    frame(screen, 1, 1, 208, 248)
    selected = 0
    font = pygame.font.Font(None, 30)
    text_coord = 30
    coords = load_text(screen, text, text_coord, font)
    screen.blit(font.render(text[selected], True, c2), (10, coords[selected]))
    SCREEN.blit(pygame.transform.scale(load_image('fon1.jpeg'), (WIDTH, HEIGHT)), (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = select_text(screen, font, text, selected, coords, 1)
                elif event.key == pygame.K_UP:
                    selected = select_text(screen, font, text, selected, coords, -1)
                elif event.key == 13:  # у меня не работает K_ENTER, и K_enter, и ENTER тожe
                    if selected == 3:
                        terminate()
                    elif selected == 2:
                        controls()
                    elif selected == 1:
                        records()
                    elif selected == 0:
                        return True
        SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
        pygame.display.flip()
        clock.tick(FPS)


def controls():
    screen = pygame.transform.scale(load_image("controls.png"), (210, 250))
    SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and (event.key == 13 or event.key == pygame.K_ESCAPE):
                return
        clock.tick(10)


def records():
    screen = pygame.Surface((210, 250))
    frame(screen, 1, 1, 208, 248)
    font = pygame.font.Font(None, 30)
    text = []
    for i in range(len(SCORES)):
        text.append(str(i + 1) + ') ' + SCORES[i])
    text.append('Back')
    text_coord = load_text(screen, text, 30, font)[-1]
    screen.blit(font.render('Back', True, c2), (10, text_coord))
    SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and (event.key == 13 or event.key == pygame.K_ESCAPE):
                return
        clock.tick(10)  # насколько я понимаю, это должно немного уменьшать затраты энергии компьютера


def change_difficulty(field):
    difficulty = field.difficulty
    level = field.level
    screen = pygame.Surface((210, 250))
    frame(screen, 1, 1, 208, 248)
    font = pygame.font.Font(None, 30)
    text = ['Press D to increase', 'lvl; A - to decrease',' ', 'Current level: ' + str(level), ' ',
            'Confirm changes', 'Cancel changes']
    coords = load_text(screen, text, 30, font, False)[-2:]
    selected = select_text(screen, font, text[-2:], 0, coords, 1)
    SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    if level > field.level:
                        difficulty -= 1
                        level -= 1
                    else:
                        pass
                elif event.key == pygame.K_d:
                    if level < 5:  # 5 уровень это уже очень сложно
                        difficulty += 1
                        level += 1
                    else:
                        pass
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected = select_text(screen, font, text[-2:], selected, coords, 1)
                elif event.key == 13:
                    if selected == 0:
                        field.difficulty = difficulty
                        field.level = level
                        field.upd_level()
                    return field
        text[3] = text[3][:-1] + str(level)
        load_text(screen, text[:-2], 30, font, False)
        SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
        pygame.display.flip()


start_screen()
main_menu()
x = main_screen()
while x:
    x = main_screen()
