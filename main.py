import os
import sys
from random import choice

import pygame

pygame.init()
size = WIDTH, HEIGHT = 700, 650
SCREEN = pygame.display.set_mode(size)
SCREEN.fill('black')
FPS = 50
clock = pygame.time.Clock()


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


def terminate():
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
        self.speed = 1.5
        self.score = 1400
        self.level = self.score // 1500 + 1
        self.end = False
        self.coords_y = []
        self.coords_x = []

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
        if self.level != self.score // 1500 + 1:
            self.level = self.score // 1500 + 1
            self.speed *= 1.4
        return True


FIELD_WIDTH = 10
FIELD_HEIGHT = 20
pygame.display.set_caption("Tetris")


def main_screen():
    screen = pygame.Surface(size)
    screen.fill('black')
    fon = pygame.transform.scale(load_image('fon1.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    field = Field(FIELD_WIDTH, FIELD_HEIGHT)
    field.set_view(200, 25, 30)
    field.figure(choice(ALL_FIGURES))
    field.render(screen)

    def frame(x, y, w, h):  # рамка для текста or smth
        screen.fill('white', (x - 1, y - 1, w + 2, h + 2))
        screen.fill('black', (x, y, w, h))

    frame(510, field.top + 1, 180, 200)
    frame(10, field.top + 60, 180, 70)
    frame(10, field.top + 1, 180, 27)
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
            if field.check_rows():  # анимация удаления ряда и изменение очков
                string = font.render(str(field.score), True, pygame.Color('white'), pygame.Color('black'))
                screen.blit(string, rect.move(0, 35))
                screen.blit(font.render(str(field.level), True, pygame.Color('white'), pygame.Color('black')),
                            (100, field.top + 3))
            field.render(screen)
        SCREEN.blit(screen, (0, 0))
        pygame.display.flip()


def pause():
    c1 = pygame.Color((200, 150, 0))  # у меня вообще дальтонизм не судите строга
    c2 = pygame.Color((255, 255, 255))
    c3 = pygame.Color((0, 0, 0))
    screen = pygame.Surface((210, 210))
    text = ["Resume", "Restart", "Controls", "Change difficulty", "Exit"]
    screen.fill(c1)
    selected = 0
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    text_coord = 30
    coords = []
    for line in text:
        coords.append(text_coord)
        string_rendered = font.render(line, True, c3)
        screen.blit(string_rendered, (10, text_coord))
        text_coord += 10
        text_coord += string_rendered.get_rect().height
    screen.blit(font.render(text[selected], True, c2), (10, coords[selected]))
    screen.blit(pygame.transform.scale(load_image('pause.png'), (50, 50)), (150, 10))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    screen.blit(font.render(text[selected], True, c3), (10, coords[selected]))
                    selected = (selected + 1) % 5
                    screen.blit(font.render(text[selected], True, c2), (10, coords[selected]))
                elif event.key == pygame.K_UP:
                    screen.blit(font.render(text[selected], True, c3), (10, coords[selected]))
                    selected = (selected - 1) % 5
                    screen.blit(font.render(text[selected], True, c2), (10, coords[selected]))
                elif event.key == pygame.K_ESCAPE:
                    return True
                elif event.key == 13:  # у меня не работает K_ENTER, и K_enter, и ENTER тожe
                    if selected == 4:
                        terminate()
                    elif selected == 3:
                        pass
                    elif selected == 2:
                        pass
                    elif selected == 1:
                        return False

                    return True
        SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 105))
        pygame.display.flip()
        clock.tick(30)


start_screen()
x = main_screen()
while x:
    x = main_screen()
