import os
import copy
import time
import colorama
import win32api
import random
import sqlite3
import msvcrt
import signal


class Game:
    def __init__(self, _screen_height, _screen_width):
        os.system('mode con: cols=60 lines=30')
        colorama.init()
        os.system('cls')
#        win32api.ShowCursor(False)
        signal.signal(signal.SIGINT, self.signal_interruption_handler)

        self.screen_height = _screen_height
        self.screen_width = _screen_width
        self.infoScreenWidth = 30
        self.screen = [[[' ', 0] for x in range(0, self.screen_width + self.infoScreenWidth)] for y in range(0, self.screen_height)]
        self.screen_2 = copy.deepcopy(self.screen)
        self.name = ''
        self.score = 0
        self.highScore = 0
        self.combo = 0
        self.bricksNo = 0
        self.bricksNo_total = 0
        self.speed = 0.8
        self.gameOverCheck = 0
        self.lvl = 0
        self.lvl_tmp = 0
        self.scores = {
            'name': [],
            'score': []
        }


        self.brick = Brick(self)
        self.brick.new_brick()

        for y in range(0, self.screen_height):
            for x in range(0, self.screen_width):
                if y == self.screen_height - 1 and 0 < x < self.screen_width - 1:
                    self.screen[y][x][0] = "="
                    self.screen[y][x][1] = 0
                elif x == 0 or x == self.screen_width - 1:
                    self.screen[y][x][0] = "|"
                    self.screen[y][x][1] = 0

        self.input_text([2, self.screen_width + 2], "next", 0)
        self.input_text([8, self.screen_width + 2], "score:", 0)
        self.print_next_brick()
        self.print_score()
        self.set_speed()

        self.getHighScores()

        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        self.run_loop = True

    @staticmethod
    def keyboard_flush():
        # Flush the keyboard buffer
        while msvcrt.kbhit():
            msvcrt.getch()

    @staticmethod
    def signal_interruption_handler(signal, frame):
        print("\033[27;1H\033[0mKeyboard interrupt has been caught. Bye!")

        Game.keyboard_flush()
        exit(0)

    def get_user_data(self):
        self.input_text([15, self.screen_width + 2], "Your name: ", 0)
        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        Game.keyboard_flush()

        print("\033[16;{}H".format(self.screen_width + 2 + len("Your name:  ")), end="")
        self.name = input("")
        print("\033[16;{}H{}".format(self.screen_width + 2 + len("Your name:  "), ' ' * len(self.name)), end="")

    def getHighScores(self):
        conn = sqlite3.connect("score.db")
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM scores")
        except sqlite3.Error as e:
            try:
                c.execute("CREATE TABLE scores (\
                       name text,\
                       score int)")
                conn.commit()
            except sqlite3.Error as e:
                print("\033[23;1HSqlite3 error 2: {}".format(e))
                conn.close()
                Game.keyboard_flush()
                exit(1)

        try:
            c.execute("SELECT * FROM scores")
        except sqlite3.Error as e:
            print("\033[23;1HSqlite3 error 3: {}".format(e))
            conn.close()
            Game.keyboard_flush()
            exit(1)

        for row in c.fetchall():
            self.scores['name'].append(row[0])
            self.scores['score'].append(row[1])

        conn.close()

        sorted_indexes = []
        for i in sorted(enumerate(self.scores['score']), key=lambda x: x[1], reverse=True):
            sorted_indexes.append(i[0])
        if len(sorted_indexes) > 0:
            self.highScore = self.scores['score'][sorted_indexes[0]]

    def gameOver(self):
        self.input_text([11, self.screen_width + 2], ' ' * len("Best score!"), 0)
        self.input_text([11, self.screen_width + 2], "Game over", 31)
        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)
        self.get_user_data()

        conn = sqlite3.connect("score.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO scores VALUES (?, ?)", (self.name, self.score))
            conn.commit()
        except sqlite3.Error as e:
            print("\033[23;1HSqlite3 error 4: {}".format(e))
            conn.close()
            Game.keyboard_flush()
            exit(1)

        conn.close()

        self.scores['name'].append(self.name)
        self.scores['score'].append(self.score)
        sorted_indexes = []
        for i in sorted(enumerate(self.scores['score']), key=lambda x: x[1], reverse=True):
            sorted_indexes.append(i[0])

        for y in range(self.screen_height):
            for x in range(self.infoScreenWidth):
                self.screen[y][self.screen_width + x][0] = ' '
                self.screen[y][self.screen_width + x][1] = 0
        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        self.input_text([2, self.screen_width + 2], "High score:", 0)
#        print("\033[2;{}HHigh score:".format(self.screen_width + 2))

        if len(sorted_indexes) > 5:
            high_score_to_print = 5
        else:
            high_score_to_print = len(sorted_indexes)

        for i in range(high_score_to_print):
            msg = str(i + 1) + '. ' + self.scores['name'][sorted_indexes[i]] + ' ' + str(self.scores['score'][sorted_indexes[i]])
            self.input_text([4 + (i * 2), self.screen_width + 2], msg, 0)
        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)
#        for i in range(high_score_to_print):
#            print("\033[{};{}H\033[0m{}. {} {}".format(4 + (i * 2),\
#                                                 self.screen_width + 2,\
#                                                 i + 1,\
#                                                 scores['name'][sorted_indexes[i]],\
#                                                 scores['score'][sorted_indexes[i]]))


        self.menu()
#        print("\033[26;1H")
#        exit(1)

    def menu(self):
        self.keyboard_flush()
        menu_items_selection = {
            'new_game': 32,
            'quit': 0
        }

        self.input_text([17, self.screen_width + 2], "New Game", menu_items_selection['new_game'])
#        print("\033[18;{}H\033[{}mNew Game\033[0m".format(self.screen_width + 2, menu_items_selection['new_game']))
        self.input_text([19, self.screen_width + 2], "Quit", menu_items_selection['quit'])
#        print("\033[20;{}H\033[{}mQuit\033[0m".format(self.screen_width + 2, menu_items_selection['quit']))
        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        while True:
            if win32api.GetAsyncKeyState(ord('W')) and menu_items_selection['new_game'] == 0:
                menu_items_selection['new_game'] = 32
                menu_items_selection['quit'] = 0
                self.input_text([17, self.screen_width + 2], "New Game", menu_items_selection['new_game'])
#                print("\033[18;{}H\033[{}mNew Game\033[0m".format(self.screen_width + 2, menu_items_selection['new_game']))
                self.input_text([19, self.screen_width + 2], "Quit", menu_items_selection['quit'])
#                print("\033[20;{}H\033[{}mQuit\033[0m".format(self.screen_width + 2, menu_items_selection['quit']))
            elif win32api.GetAsyncKeyState(ord('S')) and menu_items_selection['quit'] == 0:
                menu_items_selection['quit'] = 32
                menu_items_selection['new_game'] = 0
                self.input_text([17, self.screen_width + 2], "New Game", menu_items_selection['new_game'])
#                print("\033[18;{}H\033[{}mNew Game\033[0m".format(self.screen_width + 2,
#                      menu_items_selection['new_game']))
                self.input_text([19, self.screen_width + 2], "Quit", menu_items_selection['quit'])
#                print("\033[20;{}H\033[{}mQuit\033[0m".format(self.screen_width + 2, menu_items_selection['quit']))
            elif win32api.GetAsyncKeyState(ord('A')) or win32api.GetAsyncKeyState(ord('D')):
                if menu_items_selection['new_game'] > 0:
                    self.prepare_new_game()
                else:
                    print("\033[26;1H")
                    Game.keyboard_flush()
                    exit(1)
            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)
            time.sleep(0.1)

    def prepare_new_game(self):
        # Clear the 'menu' screen
        for y in range(self.screen_height):
            for x in range(self.infoScreenWidth):
                self.screen[y][self.screen_width + x][0] = ' '
                self.screen[y][self.screen_width + x][1] = 0
        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        for y in range(self.screen_height - 2, -1, -1):
            for x in range(1, self.screen_width - 1):
                if self.screen[y][x][0] != '#':
                    self.screen[y][x][0] = '#'
                    self.screen[y][x][1] = 0
            self.printScreen()
            time.sleep(0.005)
        self.screen_2 = copy.deepcopy(self.screen)

        for y in range(self.screen_height - 1):
            for x in range(1, self.screen_width - 1):
                self.screen[y][x][0] = ' '
                self.screen[y][x][1] = 0
            self.printScreen()
            time.sleep(0.005)
        self.screen_2 = copy.deepcopy(self.screen)

        self.input_text([2, self.screen_width + 2], "next", 0)
        self.input_text([8, self.screen_width + 2], "score:", 0)
        self.brick.new_brick()
        self.print_next_brick()
        self.print_score()
        self.set_speed()
        self.bricksNo = 0
        self.bricksNo_total = 0
        self.lvl = 0
        self.scores = {
            'name': [],
            'score': []
        }
        self.printScreen()
        self.screen_2 = copy.deepcopy(self.screen)

        self.run_loop = True

        self.loop()

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

        lvl = 0

        for i in sorted(avail_speeds.keys()):
            if i <= self.bricksNo < 180:
                self.speed = avail_speeds[i]
                lvl += 1
            elif self.bricksNo >= 180:
                self.bricksNo = 0
                self.speed = 0.8
                lvl = 0

        if self.lvl_tmp != lvl:
            self.lvl_tmp = lvl
            self.lvl += 1

        print("\033[23;1H\r\033[0K\033[33mBricks No: {}\n\
Level: {}\n\
Speed {} sec\033[0m".format(self.bricksNo_total, self.lvl, self.speed))

    def input_text(self, pos, text, col = 0):
        for x in range(0, len(text)):
            self.screen[pos[0]][pos[1] + x][0] = text[x]
            self.screen[pos[0]][pos[1] + x][1] = col

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
                    if self.brick.brick[0][y][len(self.brick.brick[0][0]) - 1] == '#' and \
                            self.screen[self.brick.posYX[0] + y + 1][self.brick.posYX[1] +
                                                                     len(self.brick.brick[0][0])][0] == '#':
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

            # Compares the current score with the highest score in the database
            if self.score > 0:
                self.input_text([11, self.screen_width + 2], "Best score!", 32)

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)
            time.sleep(0.1)

        self.brick.new_brick()

    def printScreen(self, force=False):
        if force:
            for y in range(0, self.screen_height):
                for x in range(0, self.screen_width + self.infoScreenWidth):
                    print("\033[{};{}H\033[{}m{}".format(y + 1, x + 1, self.screen[y][x][1], self.screen[y][x][0]))
        else:
            for y in range(0, self.screen_height):
                for x in range(0, self.screen_width + self.infoScreenWidth):
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
                    self.screen[y][x][1] = 0

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)

            time.sleep(0.5)

            for y in range(y_range_to_remove[0] - 1, -1, -1):
                for x in range(1, self.screen_width - 1):
                    self.screen[y + len(y_range_to_remove)][x][0] = self.screen[y][x][0]
                    self.screen[y + len(y_range_to_remove)][x][1] = self.screen[y][x][1]

            self.score += len(y_range_to_remove) * ((self.combo + 1) * 10)
            self.combo += 1
            if self.combo > 1: self.print_combo()
            self.print_score()

            self.printScreen()
            self.screen_2 = copy.deepcopy(self.screen)

            time.sleep(0.5)
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

        for y in range(len(self.g.brick.brick[0])):
            for x in range(len(self.g.brick.brick[0][0])):
                if self.g.screen[self.g.brick.posYX[0] + y + 1][self.g.brick.posYX[1] + x][0] in ['#', '='] and \
                        self.g.brick.brick[0][y][x] == '#':
                    self.g.gameOver()

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
