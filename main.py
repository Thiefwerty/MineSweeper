import random
import dill as pickle
'''
сохранение/загрузка
добавить UI/UX
'''


class Cell:

    def __init__(self, has_mine, get_num_neighbor_mines):
        self.__has_mine = has_mine
        self.__status = 0
        self.__get_num_neighbor_mines = get_num_neighbor_mines

    def num_neighbor_mines(self):
        return self.__get_num_neighbor_mines()

    def has_mine(self):
        return self.__has_mine

    def is_opened(self):
        return self.__status == 2

    def change_state(self, action):
        if action == "Open":
            self.__status = 2
            return not self.__has_mine
        elif action == "Flag":
            self.__status ^= 1
            return True

    def __str__(self):
        str_rep = ''

        if self.__status == 0:
            str_rep = '.'
        elif self.__status == 1:
            str_rep = '⚑'
        elif self.__status == 2:
            if self.__has_mine:
                str_rep = '💣'
            else:
                str_rep = str(self.__get_num_neighbor_mines())

        return str_rep


class Board:

    def __init__(self, row, col, num_mines):
        self.__row = row
        self.__col = col
        self.__num_mines = num_mines
        self.__num_current_moves = 0
        self.__board = self.make_board()

    def is_move_possible(self):
        return (self.__col * self.__row - self.__num_mines) - self.__num_current_moves != 0

    def make_board(self):
        board = [[None for _ in range(self.__col)] for _ in range(self.__row)]
        mines = 0

        while mines < self.__num_mines:
            row = random.randint(0, self.__row - 1)
            col = random.randint(0, self.__col - 1)

            if board[row][col] is not None:
                continue

            board[row][col] = Cell(True, lambda: self.__num_neighbor_mines(row, col))
            mines += 1

        for r in range(self.__row):
            for c in range(self.__col):
                if board[r][c] is None:
                    board[r][c] = Cell(False, lambda r=r, c=c: self.__num_neighbor_mines(r, c))

        return board

    def __num_neighbor_mines(self, row, col):
        mines = 0

        for r in range(max(0, row - 1), min(self.__row - 1, row + 1) + 1):
            for c in range(max(0, col - 1), min(self.__col - 1, col + 1) + 1):
                if r == row and c == col:
                    continue
                if self.__board[r][c].has_mine():
                    mines += 1

        return mines

    def __dfs(self, row, col):
        if not self.__open_cell(row, col):
            return False

        for r in range(max(0, row - 1), min(self.__row - 1, row + 1) + 1):
            for c in range(max(0, col - 1), min(self.__col - 1, col + 1) + 1):
                if not self.__board[r][c].is_opened():
                    if self.__board[r][c].num_neighbor_mines() == 0:
                        self.__dfs(r, c)
                    else:
                        self.__open_cell(r, c)

        return True

    def make_move(self, row, col, action):
        if action == 'Open':
            if self.__board[row][col].num_neighbor_mines() == 0:
                return self.__dfs(row, col)
            else:
                return self.__open_cell(row, col)
        else:
            return self.__board[row][col].change_state(action)

    def __open_cell(self, row, col):
        if self.__board[row][col].is_opened():
            return True
        else:
            self.__num_current_moves += 1
            return self.__board[row][col].change_state('Open')

    def print(self, need_open_cells):
        for r in range(self.__row):
            for c in range(self.__col):
                if need_open_cells:
                    self.__open_cell(r, c)
                print(self.__board[r][c], end='')
            print()


class MineSweeper:

    def __init__(self, board_factory):
        self.__board_factory = board_factory

    def start_game(self):
        while True:
            self.__play()

    def save_board(self, board):
        board_to_save = open('save_board.pickle', 'wb')
        pickle.dump(board, board_to_save)
        board_to_save.close()

    def load_board(self):
        board_to_load = open('save_board.pickle', 'rb')
        board = pickle.load(board_to_load)
        board_to_load.close()

        return board

    def __play(self):
        print('Введите N для новой игры. L для загрузки последней игры')
        user_input = input()

        if user_input == 'N':
            print('Введите размер поля и количество мин в формате '
                  '[количество строк,количество столбцов,количество мин]')
            row, col, mines = map(int, input().split(','))
            board = self.__board_factory(row, col, mines)

        elif user_input == 'L':
            board = self.load_board()

        is_playing = True

        while is_playing:
            if not board.is_move_possible():
                print('Поздравляем, вы выиграли!')
                break
            board.print(False)
            print('Введите координаты клетки с которой хотите взаимодействовать в формате [X,Y], '
                  'и действие:Open для открытия клетки,Flag для флага')
            print('Если вы хотите сохранить текущую игру - введите S')
            user_input = input()
            if user_input == 'S':
                self.save_board(board)
                print('Игра сохранена')
            else:
                user_input = user_input.split(',')
                col, row, action = int(user_input[0]), int(user_input[1]), user_input[2]
                is_playing = board.make_move(row, col, action)
                if not is_playing:
                    print('Вы проиграли!')

        board.print(True)


if __name__ == '__main__':
    MineSweeper(lambda r, c, m: Board(r, c, m)).start_game()
