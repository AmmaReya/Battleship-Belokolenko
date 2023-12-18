from random import randint


class Text:
    red = '\033[91m'
    purple = '\033[95m'
    orange = '\033[93m'
    end_colour = '\033[0m'


# класс координат на игровом поле
class Dot:
    def __init__(self, x, y):  # инициализация координат
        self.x = x
        self.y = y

    def __eq__(self, other):  # проверка уникальности координат
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # текстовое представление координат
        return f'({self.x}, {self.y})'


# класс исключений
class BoardException(Exception):
    pass


# исключение - выстрел вне поля
class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за доску!'


# исключение - повторный выстрел в одну и ту же точку
class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку'


# исключение - корабль выходит за поле, корабль находится в занятой клетке
class BoardWrongShipException(BoardException):
    pass


# класс кораблей
class Ship:
    def __init__(self, bow, l, o):  # параметры корабля
        self.bow = bow  # координата носа корабля
        self.l = l  # длина корабля
        self.o = o  # ориентация корабля (горизонтальная/вертикальная)
        self.lives = l  # количество жизней корабля

    @property
    def dots(self):  # создание списка координат всех точек корабля
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:  # вертикальная ориентация корабля
                cur_x += i

            elif self.o == 1:  # горизонтальная ориентация корабля
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):  # проверка попадания в корабль
        return shot in self.dots


# клас игровой доски
class Board:
    def __init__(self, hid=False, size=6):  # параметры игровой доски
        self.size = size  # размер игрового поля
        self.hid = hid  # игровое поле не скрывается

        self.count = 0  # счетчик пораженных кораблей

        self.field = [['•'] * size for _ in range(size)]  # графическое отображение игрового поля

        self.busy = []  # список занятых точек
        self.ships = []  # список координат кораблей на игровом поле

    def add_ship(self, ship):  # добавление кораблей на игровое поле

        for d in ship.dots:  # проверка расстановки кораблей на поле
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:  # добавление кораблей на поле
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):  # определение соседних точек корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = 'X'  # отражение соседних точек корабля на игровом поле
                    self.busy.append(cur)  # внесение соседних точек корабля в занятые

    def __str__(self):  # визуализация игрового поля
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        if self.hid:  # скрытие кораблей на игровом поле
            res = res.replace('■', '•')
        return res

    def out(self, d):  # точка выходит за пределы поля
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):  # проверка, выходит ли точка за пределы игрового поля
            raise BoardOutException()

        if d in self.busy:  # проверка, является ли точка занятой
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:  # точка принадлежит кораблю
                ship.lives -= 1  # счетчик жизней корабля
                self.field[d.x][d.y] = Text.red + 'Х' + Text.end_colour
                if ship.lives == 0:  # поражение корабля
                    self.count += 1
                    self.contour(ship, verb=True)  # отображение соседних точек корабля
                    print(Text.red + 'Корабль уничтожен!' + Text.end_colour)
                    return False
                else:
                    print(Text.orange + 'Корабль ранен!' + Text.end_colour)
                    return True

        self.field[d.x][d.y] = 'X'  # отражение промаха
        print('Мимо!')
        return False

    def begin(self):  # сброс списка соседних точек кораблей
        self.busy = []


# класс игроков
class Player:
    def __init__(self, board, enemy):
        self.board = board  # игровое поле игрока
        self.enemy = enemy  # игровое поле противника

    def ask(self):  # вызов функции для классов наследников
        raise NotImplementedError()

    def move(self):  # ход игрока
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# ход компьютера
class AI(Player):
    def ask(self):  # случайная генерация хода
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d


# ход игрока
class User(Player):
    def ask(self):
        while True:  # ввод хода игрока и проверка правильности ввода
            cords = input('Ваш ход: ').split()

            if len(cords) != 2:
                print(' Введите 2 координаты! ')
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(' Введите числа! ')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# класс хода игры
class Game:
    def __init__(self, size=6):
        self.size = size  # задание размера доски
        pl = self.random_board()  # создание доски для игрока
        co = self.random_board()  # создание доски для компьютера
        co.hid = True  # скрытие кораблей на доске компьютера

        self.ai = AI(co, pl)  # создание игрока - компьютер
        self.us = User(pl, co)  # создание игрока - пользователь

    def random_board(self):  # генерация игровой доски
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):  # попытка случайной генерации игрового поля
        lens = [3, 2, 2, 1, 1, 1, 1]  # список длин кораблей
        board = Board(size=self.size)  # создание доски
        attempts = 0  # количество попыток поставить корабль на игровое поле
        for l in lens:  # добавление кораблей на игровое поле
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):  # приветствие
        print('-------------------')
        print(Text.purple + '  Приветствуем вас ')
        print('      в игре       ')
        print('    морской бой    ' + Text.end_colour)
        print('-------------------')
        print(' формат ввода: x y ')
        print(' x - номер строки  ')
        print(' y - номер столбца ')

    def loop(self):  # игровой цикл
        num = 0  # номер хода
        while True:
            print('-' * 20)
            print('Доска пользователя:')
            print(self.us.board)
            print('-' * 20)
            print('Доска компьютера:')
            print(self.ai.board)
            if num % 2 == 0:  # номер хода четный - ходит пользователь
                print('-' * 20)
                print('Ходит пользователь!')
                repeat = self.us.move()
            else:
                print('-' * 20)
                print('Ходит компьютер!')
                repeat = self.ai.move()
            if repeat:  # повтор хода после поражения корабля
                num -= 1

            if self.ai.board.count == 7:  # условие победы игрока
                print('-' * 20)
                print(Text.purple + 'Пользователь выиграл!' + Text.end_colour)
                break

            if self.us.board.count == 7:  # условие победы компьютера
                print('-' * 20)
                print(Text.purple + 'Компьютер выиграл!' + Text.end_colour)
                break
            num += 1

    def start(self):  # вызов приветственного сообщение и старт игры
        self.greet()
        self.loop()


g = Game()
g.start()
