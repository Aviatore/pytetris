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
        self.screen = [[[' ', 0] for x in range(0, self.screen_width + 15)] for y in range(0, self.screen_height)]
        self.screen_2 = copy.deepcopy(self.screen)
        self.score = 0
        self.combo = 0
        self.bricksNo = 0
        self.bricksNo_total = 0
        self.speed = 0.8

        self.brick = Brick(self)
        self.brick.new_brick()

        for y in range(0, self.screen_height):
            for x in range(0, self.screen_width):
                if y == self.screen_height - 1 and 0 < x < self.screen_width - 1:
                    self.screen[y][x][0] = "="
                elif x == 0 or x == self.screen_width - 1:
                    self.screen[y][x][0] = "|"


        self.input_text([2, self.screen_width + 2], "next")
        self.input_text([8, self.screen_width + 2], "score:")
        self.print_next_brick()
        self.print_score()
        self.set_speed()

        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        self.run_loop = True

    def set_speed(self):
        avail_speeds = {
            0: 0.8,
            20: 0.7,
            40: 0.6,
            60: 0.5,
            80: 0.4,
            100: 0.5,
            120: 0.4,
            140: 0.3,
            160: 0.2,
        }
        isSet = False
        lvl = 0
        for i in sorted(avail_speeds.keys()):
            if self.bricksNo >= i:
                self.speed = avail_speeds[i]
                isSet = True
                lvl += 1

        if not isSet:
            self.bricksNo = 0
            self.speed = 0.8

        print("\033[23;1H\r\033[0K\033[33mBricks No: {}\n\
Level: {}\n\
Speed {} sec\033[0m".format(self.bricksNo_total, lvl, self.speed))

    def input_text(self, pos, text):
        for x in range(0, len(text)):
            self.screen[pos[0]][pos[1] + x][0] = text[x]
#            self.screen[pos[0]][pos[1] + x][1] = 0

    def print_combo(self):
        msg = 'COMBO ' + str(self.combo) + 'x'
        for x in range(len(msg)):
            self.screen[10][self.screen_width + 2 + x][0] = msg[x]
            self.screen[10][self.screen_width + 2 + x][1] = 31

    def clear_combo(self):
        for x in range(9):
            self.screen[10][self.screen_width + 2 + x][0] = ' '
            self.screen[10][self.screen_width + 2 + x][1] = 0

    def print_score(self):
        for x in range(self.screen_width + 9, self.screen_width + 15):
            self.screen[8][x][0] = ' '

        score_str = '0' * (6 - len(str(self.score))) + str(self.score)
        score_index = 0
        for x in range(self.screen_width + 9, self.screen_width + 15):
            self.screen[8][x][0] = score_str[score_index]
            score_index += 1

    def print_next_brick(self):
        for y in range(len(self.brick.brick[0])):
            for x in range(len(self.brick.brick[0][0])):
                self.screen[1 + y][self.screen_width + 8 + x][0] = ' '
                self.screen[1 + y][self.screen_width + 8 + x][1] = 33

        for y in range(len(self.brick.next_brick[0])):
            for x in range(len(self.brick.next_brick[0][0])):
                self.screen[1 + y][self.screen_width + 8 + x][0] = self.brick.next_brick[0][y][x]
                self.screen[1 + y][self.screen_width + 8 + x][1] = self.brick.next_brick[1]


    def loop(self):
#        self.brick.new_brick()
        time_now = time.time()
        time_tmp = time_now

        while self.run_loop:
            cont = 0
            for y in range(len(self.brick.brick[0])):
                for x in range(len(self.brick.brick[0][0])):
                    if self.brick.brick[0][y][x] == '#':
                        self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x][0] = ' '
                        self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x][1] = 0

            if time.time() - time_tmp >= self.speed and not win32api.GetAsyncKeyState(ord('S')):
                self.brick.posYX[0] += 1
                time_tmp = time.time()

            if win32api.GetAsyncKeyState(ord('A')) and self.screen[self.brick.posYX[0]][self.brick.posYX[1] - 1][0] != '|':
                do_not_move = 0
                for y in range(len(self.brick.brick[0])):
                    if self.brick.brick[0][y][0] == '#' and self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] - 1][0] == '#':
                        do_not_move = 1
                        break

                if do_not_move == 0:
                    self.brick.posYX[1] -= 1
            elif win32api.GetAsyncKeyState(ord('D')) and \
                    self.screen[self.brick.posYX[0]][self.brick.posYX[1] + len(self.brick.brick[0][0])][0] != '|':
                do_not_move = 0
                for y in range(len(self.brick.brick[0])):
                    if self.brick.brick[0][y][0] == '#' and self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + len(self.brick.brick[0][0])][0] == '#':
                        do_not_move = 1
                        break

                if do_not_move == 0:
                    self.brick.posYX[1] += 1
            elif win32api.GetAsyncKeyState(ord('W')):
                len_prev = len(self.brick.brick[0][0])  # Pobiera szerokość klocka przed obrotem
                self.brick.rotate('current')
                # Jeżeli szerokość klocka po obrocie jest większa niż przed obrotem oraz klocek przed obrotem znajdował się w bezpośrednim otoczeniu prawej ściany,
                # to kursor jest przesuwany o jedną pozycję w lewo
                if len(self.brick.brick[0][0]) > len_prev and (
                        self.brick.posYX[1] + len(self.brick.brick[0][0])) >= self.screen_width - 1:
                    self.brick.posYX[1] -= (self.brick.posYX[1] + len(self.brick.brick[0][0])) - self.screen_width + 1
            elif win32api.GetAsyncKeyState(ord('S')):
                self.brick.posYX[0] += 1

            for y in range(len(self.brick.brick[0])):
                for x in range(len(self.brick.brick[0][0])):
                    if self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x][0] in ['#', '='] and \
                            self.brick.brick[0][y][x] == '#':
                        self.screen = copy.deepcopy(self.screen_2)
                        self.check()
                        self.brick.new_brick()
                        self.bricksNo += 1
                        self.bricksNo_total += 1
                        self.set_speed()
                        self.print_next_brick()
                        cont = 1
                        break
                    elif self.brick.brick[0][y][x] != ' ':
                        self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x][0] = self.brick.brick[0][y][x]
                        self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] + x][1] = self.brick.brick[1]
                else:
                    continue  # only executed if the inner loop did NOT break

                break  # only executed if the inner loop DID break

            if cont == 1: continue

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)
            time.sleep(0.1)

        self.brick.new_brick()

    def printScreen(self):
        for y in range(0, self.screen_height):
            for x in range(0, self.screen_width + 15):
                if self.screen[y][x][0] != self.screen_2[y][x][0] or self.screen[y][x][1] != self.screen_2[y][x][1]:
       #             print(len(self.screen[y][x]))
                    print("\033[{};{}H\033[{}m{}".format(y + 1, x + 1, self.screen[y][x][1], self.screen[y][x][0]))
 #                  print("\033[{};{}H\033[{}m{}".format(y + 1, x + 1, 0, self.screen[y][x][0]))

    def check(self):
        sum_ = 0
        y_range_to_remove = []
        for y in range(self.brick.posYX[0], self.screen_height - 1):
            for x in range(1, self.screen_width - 1):
                if self.screen[y][x][0] == '#': sum_ += 1

            if sum_ == self.screen_width - 2:
                y_range_to_remove.append(y)

            sum_ = 0
        if len(y_range_to_remove) > 0:

            for y in y_range_to_remove:
                for x in range(1, self.screen_width - 1):
                    self.screen[y][x][0] = ' '

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)

            time.sleep(1)

            for y in range(y_range_to_remove[0] - 1, -1, -1):
                for x in range(1, self.screen_width - 1):
                    self.screen[y + len(y_range_to_remove)][x][0] = self.screen[y][x][0]

            self.score += len(y_range_to_remove) * ((self.combo + 1) * 10)
            self.combo += 1
            if self.combo > 1: self.print_combo()
            self.print_score()

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)

            time.sleep(1)
        else:
            self.combo = 0
            self.clear_combo()


class Brick:
    def __init__(self, Game):
        random.seed(time.time())
#        self.brick_index = 0
        self.next_brick_index = 0
        self.g = Game
        self.posYX = [-1, self.g.screen_width // 2]
        self.bricks = [
            [[[' ', '#'], [' ', '#'], ['#', '#']], 0],
            [[['#', ' '], ['#', ' '], ['#', '#']], 31],
            [[[' ', '#', ' '], ['#', '#', '#']], 32],
            [[['#', '#'], ['#', '#']], 33],
            [[['#'], ['#'], ['#'], ['#']], 35],
            [[['#', ' '], ['#', '#'], [' ', '#']], 36]
        ]
        self.brick = None
        self.next_brick = None

    def new_brick(self):
        self.posYX = [-1, self.g.screen_width // 2]
#        self.brick_index = self.next_brick_index
        if self.next_brick is None:
            self.brick = copy.deepcopy(self.bricks[random.randint(0, len(self.bricks) - 1)])
        else:
            self.brick = copy.deepcopy(self.next_brick)

        self.next_brick = copy.deepcopy(self.bricks[random.randint(0, len(self.bricks) - 1)])

#        self.next_brick_index = random.randint(0, len(self.bricks) - 1)

        for i in range(0, random.randint(0, 4)):
            self.rotate('next')

    def rotate(self, brick_type):
        brick_tmp = [ [], [] ]
        # Tworzy nowy klocek o szerokości i wysokości równym odpowiednio wysokości oraz szerokości danego klocka

        if brick_type == 'current':
            for y in range(len(self.brick[0][0])):
                new = []
                for x in range(len(self.brick[0])):
                    new.append('.')
                brick_tmp[0].append(new)

            for x in range(len(self.brick[0])):
                for y in range(len(self.brick[0][0])):
                    brick_tmp[0][y][len(self.brick[0]) - x - 1] = self.brick[0][x][y]

            brick_tmp[1] = self.brick[1]
            self.brick = copy.deepcopy(brick_tmp)
        elif brick_type == 'next':
            for y in range(len(self.next_brick[0][0])):
                new = []
                for x in range(len(self.next_brick[0])):
                    new.append('.')
                brick_tmp[0].append(new)

            for x in range(len(self.next_brick[0])):
                for y in range(len(self.next_brick[0][0])):
                    brick_tmp[0][y][len(self.next_brick[0]) - x - 1] = self.next_brick[0][x][y]

            brick_tmp[1] = self.next_brick[1]
            self.next_brick = copy.deepcopy(brick_tmp)

game = Game(20, 15)
game.loop()
