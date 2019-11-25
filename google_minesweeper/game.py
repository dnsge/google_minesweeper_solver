from functools import partial

import pyautogui

from google_minesweeper.util import get_grid_index, is_interesting_color, is_undiscovered, rgb_close, \
    get_neighbor_indexes, get_neighbors, neighbor_num_to_coord, coord_in_game, rgb_closes


class GameInfo:
    def __init__(self, tl, br, cell_size, game_dim):
        self.tl = tl
        self.br = br
        self.cell_size = cell_size
        self.game_dim = game_dim

        self.flagged = []

    def __str__(self):
        return str(self.__dict__)

    def cell_pos(self, cell_coord, center=True):
        if cell_coord[0] > self.game_dim[0] or cell_coord[0] < 0 or \
                cell_coord[1] > self.game_dim[1] or cell_coord[1] < 0:
            raise ValueError(f'Cell coordinate must be within game dimension of {self.game_dim}')

        across = round((cell_coord[0] + (0.5 if center else 0)) * self.cell_size + self.tl[0])
        down = round((cell_coord[1] + (0.5 if center else 0)) * self.cell_size + self.tl[1])
        return across, down

    def all_cell_pos(self):
        for y in range(self.game_dim[1]):
            for x in range(self.game_dim[0]):
                yield (x, y), self.cell_pos((x, y), center=False)

    @property
    def flag_total(self):
        if self.game_dim == (10, 8):
            return 10
        if self.game_dim == (18, 14):
            return 40
        if self.game_dim == (24, 20):
            return 99


def get_screen():
    return pyautogui.screenshot().resize(pyautogui.size())


def locate_game():
    screen = get_screen()
    tl = None
    c2 = None
    br = None
    for y in range(screen.height):
        for x in range(screen.width):
            p = screen.getpixel((x, y))
            if not tl and p == (180, 212, 101, 255):  # Light green cell
                tl = x, y
            if not c2 and p == (172, 206, 94, 255):  # Dark green cell
                c2 = x, y
            if p == (180, 212, 101, 255):
                br = x, y

    if tl is None or c2 is None or br is None:
        return None

    cell_size = c2[0] - tl[0]
    game_width = round((br[0] - tl[0]) / cell_size)
    game_height = round((br[1] - tl[1]) / cell_size)

    if game_width <= 0 or game_height <= 0:
        return None

    return GameInfo(tl, br, cell_size, (game_width, game_height))


def get_game_state(info: GameInfo):
    pyautogui.moveTo(info.tl[0] - 50, info.tl[1] - 50)
    screen = get_screen()
    if not screen:
        return None

    game_array = []

    for pos, cell_pos in info.all_cell_pos():
        index = get_grid_index(pos, info.game_dim[0])
        area = screen.crop((cell_pos[0], cell_pos[1], cell_pos[0] + info.cell_size, cell_pos[1] + info.cell_size))
        colors = area.getcolors(maxcolors=1024)
        colors = list(filter(partial(is_interesting_color, info), colors))

        number = 0  # Discovered & Empty 0

        if index in info.flagged:
            number = -2
        else:
            for color in map(lambda v: v[1], colors):
                if is_undiscovered(color):  # Undiscovered -1
                    number = -1
                if rgb_close(color, (51, 118, 203, 255)):  # Blue 1
                    number = 1
                elif rgb_closes(color, [(80, 139, 70, 255), (46, 126, 46, 255)]):  # Green 2
                    number = 2
                elif rgb_closes(color, [(195, 62, 56, 255), (199, 40, 45, 255)]):  # Red 3
                    number = 3
                elif rgb_close(color, (112, 44, 156, 255)):  # Purple 4
                    number = 4
                elif rgb_close(color, (241, 148, 54, 255)):  # Orange 5
                    number = 5
                elif rgb_closes(color, [(48, 112, 124, 255), (18, 134, 151, 255)]):  # Aqua 6
                    number = 6

                if number != 0:
                    break

        game_array.append(number)

    return game_array


def flag_if_new(coord, idx, lst, info: GameInfo):
    tup = ('flag', coord)
    if tup not in lst and idx not in info.flagged and coord_in_game(info, coord):
        lst.append(tup)
        info.flagged.append(idx)
        return True

    return False


def find_moves(info: GameInfo, game_array):
    moves = []
    for y in range(info.game_dim[1]):
        for x in range(info.game_dim[0]):
            index = get_grid_index((x, y), info.game_dim[0])
            value = game_array[index]
            if value > 0:
                neighbor_indexes = get_neighbor_indexes((x, y), info.game_dim[0], info.game_dim[1])
                neighbors = get_neighbors(neighbor_indexes, game_array)

                print('--- ' + str((x, y)) + ' ---')
                print('index:', index)
                print('value:', value)
                print('neighbors:', str(neighbors))
                print('flags:', str(info.flagged))

                undiscovered = neighbors.count(-1)
                flagged = neighbors.count(-2)
                added_count = 0
                if undiscovered + flagged == value:
                    for i in range(9):
                        if neighbors[i] == -1 and i != 4:
                            f_coord = neighbor_num_to_coord(i, (x, y))
                            f_index = neighbor_indexes[i]
                            added_count += int(flag_if_new(f_coord, f_index, moves, info))
                            # tup = ('flag', f_coord)
                            # if tup not in moves and f_index not in info.flagged and coord_in_game(info, f_coord):
                            #     moves.append(tup)
                            #     added_count += 1
                            #     info.flagged.append(f_index)

                if True:  # Try pattern recognition
                    if value == 2:
                        if neighbors[3] == neighbors[5] == 1 and \
                                neighbors[0] == neighbors[1] == neighbors[2] == 0 and \
                                neighbors[6] == neighbors[7] == neighbors[8] == -1:
                            coord1 = neighbor_num_to_coord(6, (x, y))
                            coord2 = neighbor_num_to_coord(8, (x, y))
                            flag_if_new(coord1, neighbor_indexes[6], moves, info)
                            flag_if_new(coord2, neighbor_indexes[8], moves, info)
                        elif neighbors[3] == neighbors[5] == 1 and \
                                neighbors[0] == neighbors[1] == neighbors[2] == -1 and \
                                neighbors[6] == neighbors[7] == neighbors[8] == 0:
                            coord1 = neighbor_num_to_coord(0, (x, y))
                            coord2 = neighbor_num_to_coord(2, (x, y))
                            flag_if_new(coord1, neighbor_indexes[0], moves, info)
                            flag_if_new(coord2, neighbor_indexes[2], moves, info)
                        elif neighbors[1] == neighbors[7] == 1 and \
                                neighbors[0] == neighbors[3] == neighbors[6] == -1 and \
                                neighbors[2] == neighbors[5] == neighbors[8] == 0:
                            coord1 = neighbor_num_to_coord(0, (x, y))
                            coord2 = neighbor_num_to_coord(6, (x, y))
                            flag_if_new(coord1, neighbor_indexes[0], moves, info)
                            flag_if_new(coord2, neighbor_indexes[6], moves, info)
                        elif neighbors[1] == neighbors[7] == 1 and \
                                neighbors[0] == neighbors[3] == neighbors[6] == 0 and \
                                neighbors[2] == neighbors[5] == neighbors[8] == -1:
                            coord1 = neighbor_num_to_coord(2, (x, y))
                            coord2 = neighbor_num_to_coord(8, (x, y))
                            flag_if_new(coord1, neighbor_indexes[2], moves, info)
                            flag_if_new(coord2, neighbor_indexes[8], moves, info)

    for y in range(info.game_dim[1]):
        for x in range(info.game_dim[0]):
            index = get_grid_index((x, y), info.game_dim[0])
            value = game_array[index]
            if value > 0:
                neighbor_indexes = get_neighbor_indexes((x, y), info.game_dim[0], info.game_dim[1])
                neighbors = get_neighbors(neighbor_indexes, game_array)
                flagged = neighbors.count(-2)
                if flagged == value:
                    for i in range(9):
                        if neighbors[i] == -1 and i != 4:
                            c_coord = neighbor_num_to_coord(i, (x, y))
                            c_index = neighbor_indexes[i]
                            tup = ('click', c_coord)
                            if tup not in moves and c_index not in info.flagged and coord_in_game(info, c_coord):
                                moves.append(tup)
                                print('clicking ' + str(c_coord))

    return moves
