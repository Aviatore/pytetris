import os
import copy
import time
import colorama
import win32api
import random


class Game:
    def __init__(self, _screen_height, _screen_width):
        colorama.init()
        os.system('cls')

        self.screen_height = _screen_height
        self.screen_width = _screen_width
        self.screen = [[' ' for x in range(0, self.screen_height)] for y in range(0, self.screen_width)]
        self.screen_2 = copy.deepcopy(self.screen)

        self.brick = Brick(self)

        for y in range(0, self.screen_height):
            for x in range(0, self.screen_width):
                if y == self.screen_height - 1 and 0 < x < self.screen_width - 1:
                    self.screen[y][x] = "#"
                elif x == 0 or x == self.screen_width - 1:
                    self.screen[y][x] = "|"

        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        self.run_loop = True

    def loop(self):
        self.brick.new_brick()
        time_now = time.time()
        time_tmp = time_now

        while self.run_loop:
            cont = 0

            for y in range(len(self.brick.brick)):
                for x in range(len(self.brick.brick[0])):
                    if self.brick.brick[y][x] == '#':
                        self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x] = ' '

            if time.time() - time_tmp >= 0.3 and not win32api.GetAsyncKeyState(ord('S')):
                self.brick.posYX[0] += 1
                time_tmp = time.time()

            if win32api.GetAsyncKeyState(ord('A')) and self.screen[self.brick.posYX[0]][self.brick.posYX[1] - 1] != '|':
                do_not_move = 0
                for y in range(self.brick.posYX[0], self.brick.posYX[0] + len(self.brick.brick) + 1):
                    if self.screen[y][self.brick.posYX[1] - 1] == '#':
                        do_not_move = 1
                        break
                if do_not_move == 0:
                    self.brick.posYX[1] -= 1
            elif win32api.GetAsyncKeyState(ord('D')) and \
                    self.screen[self.brick.posYX[0]][self.brick.posYX[1] + len(self.brick.brick[0])] != '|':
                do_not_move = 0
                for y in range(self.brick.posYX[0], self.brick.posYX[0] + len(self.brick.brick) + 1):
                    if self.screen[y][self.brick.posYX[1] + len(self.brick.brick[0])] == '#':
                        do_not_move = 1
                        break
                if do_not_move == 0:
                    self.brick.posYX[1] += 1
            elif win32api.GetAsyncKeyState(ord('W')):
                len_prev = len(self.brick.brick[0])  # Pobiera szerokość klocka przed obrotem
                self.brick.rotate()
                # Jeżeli szerokość klocka po obrocie jest większa niż przed obrotem oraz klocek przed obrotem znajdował się w bezpośrednim otoczeniu prawej ściany,
                # to kursor jest przesuwany o jedną pozycję w lewo
                if len(self.brick.brick[0]) > len_prev and (
                        self.brick.posYX[1] + len(self.brick.brick[0])) >= self.screen_width - 1:
                    self.brick.posYX[1] -= (self.brick.posYX[1] + len(self.brick.brick[0])) - self.screen_width + 1
            elif win32api.GetAsyncKeyState(ord('S')):
                self.brick.posYX[0] += 1

            for y in range(len(self.brick.brick)):
                for x in range(len(self.brick.brick[0])):
                    if self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x] == '#' and \
                            self.brick.brick[y][x] == '#':
                        self.screen = copy.deepcopy(self.screen_2)
                        self.check()
                        self.brick.new_brick()
                        cont = 1
                        break
                    elif self.brick.brick[y][x] != '.':
                        self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x] = self.brick.brick[y][x]

                else:
                    continue  # only executed if the inner loop did NOT break

                break  # only executed if the inner loop DID break

            if cont == 1: continue

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)
            time.sleep(0.1)

    def printScreen(self):
        for y in range(0, self.screen_height):
            for x in range(0, self.screen_width):
                if self.screen[y][x] != self.screen_2[y][x]:
                    print("\033[{};{}H{}".format(y + 1, x + 1, self.screen[y][x]))

    def check(self):
        sum_ = 0
        y_range_to_remove = []
        for y in range(self.brick.posYX[0], self.screen_height - 1):
            for x in range(1, self.screen_width - 1):
                if self.screen[y][x] == '#': sum_ += 1

            if sum_ == self.screen_width - 2:
                y_range_to_remove.append(y)

            sum_ = 0
        if len(y_range_to_remove) > 0:

            for y in y_range_to_remove:
                for x in range(1, self.screen_width - 1):
                    self.screen[y][x] = ' '

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)

            time.sleep(1)

            for y in range(y_range_to_remove[0] - 1, -1, -1):
                for x in range(1, self.screen_width - 1):
                    self.screen[y + len(y_range_to_remove)][x] = self.screen[y][x]

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)

            time.sleep(1)


class Brick:
    def __init__(self, Game):
        random.seed(time.time())
        self.g = Game
        self.posYX = [-1, self.g.screen_width // 2]
        self.bricks = [
            [['.', '#'], ['.', '#'], ['#', '#']],
            [['#', '.'], ['#', '.'], ['#', '#']],
            [['.', '#', '.'], ['#', '#', '#']],
            [['#', '#'], ['#', '#']],
            [['#'], ['#'], ['#'], ['#']],
            [['#', '.'], ['#', '#'], ['.', '#']]
        ]
        self.brick = self.bricks[random.randint(0, len(self.bricks) - 1)]

    def new_brick(self):
        self.posYX = [-1, self.g.screen_width // 2]
        self.brick = self.bricks[random.randint(0, len(self.bricks) - 1)]
        self.rotate()

    def rotate(self):
        brick_tmp = []
        # Tworzy nowy klocek o szerokości i wysokości równym odpowiednio wysokości oraz szerokości danego klocka
        for y in range(len(self.brick[0])):
            new = []
            for x in range(len(self.brick)):
                new.append('.')
            brick_tmp.append(new)

        for x in range(len(self.brick)):
            for y in range(len(self.brick[0])):
                brick_tmp[y][len(self.brick) - x - 1] = self.brick[x][y]

        self.brick = copy.deepcopy(brick_tmp)


game = Game(20, 20)
game.loop()
