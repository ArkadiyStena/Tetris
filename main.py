import os
import sys
from random import choice

import pygame

pygame.init()
SCORES = open("data/scores.txt").read().split('/')  # Открываем текстовый файл с результатами
if not SCORES[0] or SCORES[0]=='\n':
    SCORES = []
size = WIDTH, HEIGHT = 700, 650  # задаем размеры экрана
SCREEN = pygame.display.set_mode(size)
pygame.display.set_caption("Tetris")
SCREEN.fill('black')
pygame.mouse.set_visible(False) # убираем курсор мышки, он не нужен (и был бы неудобен) для управления
FPS = 50
clock = pygame.time.Clock()
# задаем одну цветовую гамму для всех окон
c1 = pygame.Color((0, 0, 0))  # цвет фона (черный)
c2 = pygame.Color((255, 255, 255))  # цвет выбранного пункта (белый)
c3 = pygame.Color((140, 255, 251))  # обычный цвет текта (небесно(?) голубой из пеинт 3д)
sound1 = pygame.mixer.Sound('data/sound1.mp3')  # звук, обозначающий отклик на нажатие клавиши
sound_clear = pygame.mixer.Sound('data/stage clear.wav')  # звук при удалении ряда из тетриса на денди(?)
sound_clear.set_volume(0.8)  # уменьшаем громкость последнего звука
sound_gameover = pygame.mixer.Sound('data/08-game-over.mp3')  # звук при проигрыше, тоже из тетриса на денди(?)
sound_win = pygame.mixer.Sound('data/Win-sound.mp3')  # звук победы (прохождения 10 уровней)
pygame.mixer.music.load('data/tetris_original.ogg')  # оригинальная музыка из тетриса
SOUND_ON = True


def load_image(name, colorkey=None):  # функция загрузки из изображения
    fullname = os.path.join('data', name)
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


def load_text(screen, text, text_coord, font, BACK_on_screen=True):  # функция загрузки нескольких строк текста
    # переменная BACK_on_screen означает "есть ли надпись back/exit в данный момент", можно было бы обойтись без этой
    # некрасивой переменной, но я думал, что у меня всегда будет эта строка, перед которой стоит сделать отступ, и
    # только в самом конце сделал раздел, где надписи "back" нет, поэтому, чтобы не переписывать код, решил ввести этот
    # "костыль", не влияющий на количество строк в программе (если не счиать эти 4 на комментарий)
    coords = []  # список координат по y каждой строчки
    for i in range(len(text)):
        string_rendered = font.render(text[i], True, c3, c1)  # загружаем строчку цвета c3 с фоном c1
        screen.blit(string_rendered, (10, text_coord))
        coords.append(text_coord)  # сохраняем координаты строчки в список
        if BACK_on_screen and i == len(text) - 2:  # перед последней строчкой делаем отступ
            text_coord += 20
        text_coord += 9  # делаем отступ между строчками, равный 9
        text_coord += string_rendered.get_rect().height  # увеличиваем координаты для новой строчки на высоту предыдущей
    return coords


def select_text(screen, font, text, selected, coords, m):  # функция выбора какого-то пункта в меню
    # у меня довольно много экранов, на которых эта функция пригодилась бы, поэтому ее введение значительно уменьшает
    # количество строк в программе
    screen.blit(font.render(text[selected], True, c3, c1), (10, coords[selected]))
    selected = (selected + m) % len(text)  # изменяем номер выбранной строки в списке строк
    screen.blit(font.render(text[selected], True, c2, c1), (10, coords[selected]))
    # предыдущий выбранный текст сделали стандартного цвета, а новый - цвета c2
    sound1.play()
    return selected  # возвращаем новый номер выбранного пункта


def frame(screen, x, y, w, h):  # рамка для текста или окна
    screen.fill('white', (x - 1, y - 1, w + 2, h + 2))  # края обведенной области белые
    screen.fill(c1, (x, y, w, h))  # а сама область цвета c1


def turn_off_on_sound():  # функция вкл/выкл аудио
    global SOUND_ON
    SOUND_ON = not SOUND_ON  # изменяем состояния звука на противоположное (True (1) на False (0), False (0) на True(1))
    # устанавливаем новое значение звука (0 или 1):
    sound1.set_volume(SOUND_ON)
    sound_clear.set_volume(SOUND_ON * 0.8)  # в данном случае не 1, а 0.8, потому что 1 очень громко
    sound_gameover.set_volume(SOUND_ON)
    sound_win.set_volume(SOUND_ON)
    pygame.mixer.music.set_volume(SOUND_ON)


def terminate():  # функция закрытия программы
    s = open('data/scores.txt', mode='w')
    s.write('/'.join(SCORES))  # перед выходом из программы заносим изменения в файл с рекордами
    pygame.quit()
    sys.exit()  # завершаем работу


ALL_FIGURES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']  # все типы тетромино
FIELD_WIDTH = 10  # ширина игрового поля
FIELD_HEIGHT = 20  # высота игрового поля
CELL_SIZE = 30  # размер клетки
LEFT = 200  # положение поля относительно левого края экрана
TOP = 25  # положение поля относительно верхнего края


class Field:  # класс отвечающий за игровое поля
    def __init__(self, left, top, width, height, cell_size):
        self.width = width
        self.height = height
        self.board = [[''] * width for _ in range(height)]
        # в self.board хранится информация о цвете каждой клетки. если клетка пустая, то записывается в спиок как ''
        self.left = left
        self.top = top
        self.cell_size = cell_size
        self.score = 0
        self.difficulty = 1  # сложность, задаваемая пользователем в настройках
        self.upd_level()
        self.end = False  # если игра закончилась, то self.end = True
        self.coords_y = []
        self.coords_x = []

    def upd_level(self):  # обновление значения уровня и скорости падения фигур
        self.level = self.score // 1500 + self.difficulty
        # изначально уровень изменяется только в зависимости от количества очков, но пользователь может увеличить
        # уровень самостоятельно с помощью изменения self.difficulty
        self.speed = self.speed = 1.5 * 1.4 ** self.level  # скорость падения тетромино зависит от уровня

    def render(self, screen, board):  # загрузка поля на экран
        for i in range(4):
            board[self.coords_y[i]][self.coords_x[i]] = self.color  # придаем фигурке цвет на доске
        screen.fill('white', (self.left, self.top, self.cell_size * self.width, self.cell_size * self.height))
        for i in range(self.width):
            for j in range(self.height):
                if not board[j][i]:  # пустые клетки заполняем черным
                    screen.fill('black', (self.left + i * self.cell_size + 1, self.top + j * self.cell_size + 1,
                                          self.cell_size - 2, self.cell_size - 2))
                else:  # а не пустые - соответствующим цветом
                    screen.fill(board[j][i], (self.left + i * self.cell_size + 1, self.top + j * self.cell_size + 1,
                                              self.cell_size - 2, self.cell_size - 2))
        for i in range(4):
            board[self.coords_y[i]][self.coords_x[i]] = ''  # снова убираем цвет падающей фигурки с доски
            # делаем это, чтобы не считывалось пересечение фигуры с самой собой

    def figure(self, type):  # создание фигуры
        if 0 in self.coords_y or 1 in self.coords_y or 2 in self.coords_y or 3 in self.coords_y:
            self.end = True  # если предыдущая фигура остановилась слишком высоко, то заканчиваем игру
        # self.coords_y = []  - координаты текущей фигуры по у
        # self.coords_x = []  - координаты текущей фигуры по х
        # self.color - цвет падающей фигуры
        if type == 'I':
            self.coords_x = [self.width // 2, self.width // 2, self.width // 2, self.width // 2]
            self.coords_y = [0, 1, 2, 3]
            self.color = (0, 255, 255)  # sky_blue or smth
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
        self.next_figure = choice(ALL_FIGURES)  # выбираем сразу  тип следующей фигуруы случайным образом

    def update(self):  # перемещение падающей фигуры на 1 клетку вниз
        for i in range(4):
            self.coords_y[i] += 1  # перемещаем каждую клетку фигуры на 1 вниз
        for i in range(4):
            if self.coords_y[i] == self.height or self.board[self.coords_y[i]][self.coords_x[i]]:  # если падать некуда
                for i in range(4):  # то не меняем положение фигуры (возвращаем назад положение клеток)
                    self.board[self.coords_y[i] - 1][self.coords_x[i]] = self.color
                self.figure(self.next_figure)  # создаем новую фигуру
                return

    def rotate(self, r):  # поворот фигуры
        x, y = self.coords_x[1], self.coords_y[1]  # координаты центра (оси вращения) фигуры
        tx = self.coords_x[:]  # временные переменные, чтобы не изменять зарание координаты фигуры (если это невозможно)
        ty = self.coords_y[:]
        for i in range(4):
            if i == 1:  # координаты центра (оси) менять не надо
                continue
            x1, y1 = tx[i] - x, ty[i] - y  # положение клетки относительно центра фигуры
            tx[i] += (y1 * r - x1)  # если r==1 то фигура поворачивается вправо, если r==-1 - влево
            ty[i] -= (x1 * r + y1)
            if not 0 <= tx[i] < self.width or not 0 <= ty[i] < self.height or self.board[ty[i]][tx[i]]:
                return  # если нельзя повернуть, то остонавливаем работу метода (временнные переменные пригодились)
        self.coords_x = tx  # сохраняем новые координаты по х
        self.coords_y = ty  # и по y

    def move(self, side):  # движение фигуры влево или вправо
        tx = self.coords_x[:]  # временная переменная, чтобы ничего не менять, если фигура с краю
        for i in range(4):
            tx[i] += side  # если движение влево, то уменьшаем координату на 1, иначе - увеличиваем
            if not -1 < tx[i] < self.width or self.board[self.coords_y[i]][tx[i]]:
                # если передвижение невозможно (фигура с краю или упирается в другие блоки), то завершаем работу метода
                return
        self.coords_x = tx  # сохраняем новые координаты

    def check_rows(self):  # проверяем наличие заполненных рядов
        filled_rows = 0  # количество заполненных рядов
        board1 = self.board  # копия доски, нужна для "анимации" удаления
        for i in range(self.height):
            if all(self.board[i]):  # проверяем, полностью ли заполнен ряд
                self.board = [[''] * self.width] + self.board[:i] + self.board[i + 1:]
                board1[i] = [''] * self.width
                # на основной доске убираем ряд и перемещаем все, что выше него вниз, а на board1 просто убираем ряд
                filled_rows += 1  # увеличиваем количество заполненных рядов
        if not filled_rows:  # если нет заполненых рядов, то заканчиваем работу метода
            return False
        # увеличиваем количество очков в зависимости от количества уничтоженных за 1 раз рядов
        if filled_rows == 1:
            self.score += 100
        elif filled_rows == 2:
            self.score += 300
        elif filled_rows == 3:
            self.score += 700
        elif filled_rows == 4:
            self.score += 1500
        self.upd_level()  # обновляем значение уровня
        return board1  # возвращаем поле, на котором вместо полных рядов - пустые


def start_screen():  # вступительный экран
    screen = load_image('fon.jpg')  # загружаем картинку фона
    screen = pygame.transform.scale(screen, (WIDTH, HEIGHT))  # форматируем экран
    font = pygame.font.Font(None, 30)  # определяем шрифт
    text = "Нажмите любую клавишу чтобы продолжить"
    string = font.render(text, True, pygame.Color('orange'))
    rect = string.get_rect()  # прямоугольник ограничивающий текст
    rect.left = WIDTH // 2 - rect.width // 2  # размещаем текст по центру горизонтально
    rect.top = HEIGHT * 2 // 3  # и на 1/6 сдвинуто вниз относительно центра вертикально
    screen.blit(string, rect)  # отображаем текст на локальном экране
    SCREEN.blit(screen, (0, 0))  # отображаем локальный экран на глобальном
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        clock.tick(FPS)


field = Field(LEFT, TOP, FIELD_WIDTH, FIELD_HEIGHT, CELL_SIZE)


# мне понадобится глобальная переменная, отвечающая за поле


def main_screen():
    pygame.mixer.music.play(loops=-1)  # запускаем музыку
    screen = load_image('fon1.jpeg')
    screen = pygame.transform.scale(screen, (WIDTH, HEIGHT))
    global field
    field = Field(LEFT, TOP, FIELD_WIDTH, FIELD_HEIGHT, CELL_SIZE)  # очищаем поле
    field.figure(choice(ALL_FIGURES))  # выбираем первую фигуру
    field.render(screen, field.board)  # рендерим поле на локальный экран
    frame(screen, 510, field.top + 1, 180, 200)  # рамка для отображения текста с уровнем
    frame(screen, 10, field.top + 60, 180, 70)  # рамка для отображения текста с очками
    frame(screen, 10, field.top + 1, 180, 27)  # рамка для отображения следующей фигуры
    next_figure = load_image(field.next_figure + '.png')  # картинка следующей фигуры
    next_figure = pygame.transform.scale(next_figure, (180, 180))
    screen.blit(next_figure, (510, field.top + 20))  # отображаем картинку на локальном экране
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
    SCREEN.blit(screen, (0, 0))  # отображаем локальный экран на основном
    pygame.display.flip()
    while not field.end:  # пока игра не закончилась..
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                key = event.key  # нажатая клавиша
                if key == pygame.K_LEFT:
                    field.rotate(-1)  # поворачиваем фигуру влево
                    sound1.play()  # и сообщаем пользователю об отклике на нажатие клавиши
                elif key == pygame.K_RIGHT:
                    field.rotate(1)  # поворачиваем фигуру вправо
                    sound1.play()  # и сообщаем пользователю об отклике на нажатие клавиши
                elif key == pygame.K_a:
                    field.move(-1)  # двигаем фигуру влево
                    sound1.play()  # и сообщаем пользователю об отклике на нажатие клавиши
                elif key == pygame.K_d:
                    field.move(1)  # двигаем фигуру вправо
                    sound1.play()  # и сообщаем пользователю об отклике на нажатие клавиши
                elif key == pygame.K_s:
                    mod = 8  # Ускоряем падение фигуры
                elif key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()  # выключаем музыку
                    sound1.play()
                    if not pause():  # запускаем меню паузы, если она вернула False, то надо начать новую игру
                        return True
                    # если пауза вернула True, то продолжаем эту игру
                    pygame.mixer.music.play(loops=-1)  # снова запускаем музыку
                    screen.blit(font.render(str(field.level), True, pygame.Color('white'), pygame.Color('black')),
                                (100, field.top + 3))  # отображаем значение уровня (оно могло измениться пользователем)
                field.render(screen, field.board)  # загружаем обновленное поле
                SCREEN.blit(screen, (0, 0))
                pygame.display.flip()
            if event.type == pygame.KEYUP and event.key == pygame.K_s:  # если пользователь отпустил S
                mod = 1  # то возвращаем стандартную скорость
        x += clock.tick()  # время
        if x > 1000 // (field.speed * mod):  # если пришло время двигать фигуру
            x = 0  # обнуляем время
            field.update()  # обновляем все и загружаем новые значения
            next_figure = load_image(field.next_figure + '.png')
            next_figure = pygame.transform.scale(next_figure, (180, 180))
            screen.blit(next_figure, (510, field.top + 20))
            board1 = field.check_rows()
            if board1:  # изменение очков, если были удалены ряды
                field.render(screen, board1)  # загружаем доску с пустыми клетками вместо заполненных рядов
                SCREEN.blit(screen, (0, 0))
                pygame.display.flip()
                clock.tick()
                sound_clear.play()  # проигрываем звук при удалении ряда
                t = 0  # время которое прошло с начала проигрывания звука
                while t < sound_clear.get_length() * 1000:  # пока прошедшее время меньше продолжительности звука
                    t += clock.tick()  # увеличиваем время
                # как только закончилось проигрывание звука, загружаем все новые данные field
                string = font.render(str(field.score), True, pygame.Color('white'), pygame.Color('black'))
                screen.blit(string, rect.move(0, 35))
                screen.blit(font.render(str(field.level), True, pygame.Color('white'), pygame.Color('black')),
                            (100, field.top + 3))
                if field.level == 11:  # если пройдено 10 уровней (ну то есть никогда), то сообщаем о победе.
                    pygame.mixer.music.stop()
                    return win_screen()
        field.render(screen, field.board)
        SCREEN.blit(screen, (0, 0))
        pygame.display.flip()
    # когда игра закончилась, меняем значение SCORES (рекордов), выключаем музыку, запускаем экран game_over
    global SCORES
    SCORES.append(str(field.score) + ' lvl ' + str(field.level))
    SCORES = sorted(SCORES, reverse=True, key=lambda x: (int(x.split()[0]), int(x.split()[-1])))[:5]
    pygame.mixer.music.stop()
    game_over(screen, 1000 // field.speed)
    return True


def pause():  # экран паузы
    screen = pygame.Surface((210, 250))
    text = ["Resume", "Restart", "Controls", "Change difficulty", 'Sound on/off', "Main menu", "Exit"]
    frame(screen, 1, 1, 208, 248)
    selected = 0
    font = pygame.font.Font(None, 30)
    text_coord = 20
    coords = load_text(screen, text, text_coord, font)  # координаты строчек
    screen.blit(font.render(text[selected], True, c2), (10, coords[selected]))
    screen.blit(pygame.transform.scale(load_image('pause.png'), (50, 50)), (150, 10))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = select_text(screen, font, text, selected, coords, 1)  # меняем выбранный текст
                elif event.key == pygame.K_UP:
                    selected = select_text(screen, font, text, selected, coords, -1)  # меняем выбранный текст
                elif event.key == pygame.K_ESCAPE:  # закрываем меню паузы, если нажат ескейп
                    sound1.play()
                    return True
                elif event.key == 13:  # 13 - код ентера. у меня не работает K_ENTER, и K_enter, и ENTER тожe
                    sound1.play()
                    if selected == 6:  # если выбран ексит
                        terminate()
                    elif selected == 5:  # если выбрано главное меню
                        return not main_menu()
                    elif selected == 4:  # если выбрано выключение звука
                        turn_off_on_sound()
                    elif selected == 3:  # если выбрано изменение сложности
                        global field
                        field = change_difficulty(field)
                    elif selected == 2:  # если выбрано просмотр элементов управления
                        controls()
                    elif selected == 1:  # если выбрано restart
                        return False
                    elif selected == 0:  # если выбрано Resume (продолжить игру)
                        return True
        SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
        pygame.display.flip()
        clock.tick(FPS)


def game_over(screen, speed):  # экран с картинкой при проигрыше
    sound_gameover.play()
    pic = load_image("game over.jpg")
    pic = pygame.transform.scale(pic, (298, 148))
    for i in range(8):
        t = 0
        SCREEN.blit(screen, (0, 0))
        SCREEN.blit(pic, (WIDTH // 2 - 149, 26 + 30 * i))  # надпись гейм овер летит со скоростью падения фигурок
        pygame.display.flip()
        while t < speed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN: # нажатие любой клавиши переводит в главное меню
                    sound_gameover.stop()
                    sound1.play()
                    main_menu()
                    return
            t += clock.tick()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:  # нажатие любой клавиши переводит в главное меню
                sound1.play()
                main_menu()
                return


def main_menu():  # главное меню
    screen = pygame.Surface((210, 250))
    text = ['New game', 'Records', 'Controls', 'Sound on/off', 'Exit']
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
                elif event.key == 13:  # 13 - код enter
                    sound1.play()
                    if selected == 4: # выбрано Exit
                        terminate()
                    elif selected == 3: # выбрано Sound on/off
                        turn_off_on_sound()
                    elif selected == 2: #выбрано Controls
                        controls()
                    elif selected == 1: #выбрано Records
                        records()
                    elif selected == 0: #выбрано New Game
                        return True
        SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
        pygame.display.flip()
        clock.tick(FPS)


def controls():
    picture = load_image("controls.png")
    pygame.transform.scale(picture, (210, 250))
    SCREEN.blit(picture, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN and (event.key == 13 or event.key == pygame.K_ESCAPE):
                sound1.play()
                return
        clock.tick(FPS)


def records():
    screen = pygame.Surface((210, 250))
    frame(screen, 1, 1, 208, 248)
    font = pygame.font.Font(None, 30)
    text = []
    if SCORES[0]:
        for i in range(len(SCORES)):
            text.append(str(i + 1) + ') ' + SCORES[i])
    else:
        text = ["You haven't played", "yet"]
    for i in range(5 - len(text)):
        text.append('')
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
                sound1.play()
                return
        clock.tick(FPS)


def change_difficulty(field):
    difficulty = field.difficulty
    level = field.level
    screen = pygame.Surface((210, 250))
    frame(screen, 1, 1, 208, 248)
    font = pygame.font.Font(None, 30)
    text = ['Press D to increase', 'lvl; A - to decrease', ' ', 'Current level: ' + str(level), ' ',
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
                    sound1.play()
                    if level > field.level: # если новый уровень больше уровня, который был до захода в меню
                        difficulty -= 1 # то уменьшаем сложность
                        level -= 1 # и уровень
                elif event.key == pygame.K_d:
                    sound1.play()
                    if level < 9:  # 9 уровень это уже очень сложно, по крайней мере для меня
                        difficulty += 1
                        level += 1
                    else:
                        pass
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected = select_text(screen, font, text[-2:], selected, coords, 1)
                elif event.key == 13:
                    sound1.play()
                    if selected == 0:
                        field.difficulty = difficulty
                        field.level = level
                        field.upd_level()
                    return field
        text[3] = text[3][:-1] + str(level)
        load_text(screen, text[:-2], 30, font, False)
        SCREEN.blit(screen, (WIDTH // 2 - 105, HEIGHT // 2 - 125))
        pygame.display.flip()


def win_screen():
    screen = load_image('WIN.jpg')
    screen = pygame.transform.scale(screen, (WIDTH, HEIGHT))
    SCREEN.blit(screen, (0, 0))
    sound_win.play()
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:  # нажатие любой клавиши переводит в главное меню
                sound1.play()
                return main_menu()
        clock.tick(FPS)


start_screen()
main_menu()
x = main_screen()
while x:
    x = main_screen()

# примерно 509 строк вышло без комментариев и пустых (ну вообще, код можно было бы уменьшить на строк 20, а то и больше)
