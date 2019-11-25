from functools import partial


def rgb_close(first, second, threshold=10):
    r = abs(first[0] - second[0])
    g = abs(first[1] - second[1])
    b = abs(first[2] - second[2])
    a = abs(first[3] - second[3])

    return r <= threshold and g <= threshold and b <= threshold and a <= threshold


def rgb_closes(first, others, threshold=10):
    return any(rgb_close(first, item, threshold=threshold) for item in others)


def is_undiscovered(color_tup):
    if rgb_close(color_tup, (180, 212, 101, 255)):  # Light green cell
        return True
    if rgb_close(color_tup, (172, 206, 94, 255)):  # Dark green cell
        return True
    if rgb_close(color_tup, (146, 202, 57, 255)):  # Other light green
        return True

    return False


def is_interesting_color(info, color_tup):
    if rgb_close(color_tup[1], (224, 195, 163, 255)):  # Light tan
        return False
    if rgb_close(color_tup[1], (211, 185, 157, 255)):  # Dark tan
        return False
    if rgb_close(color_tup[1], (206, 170, 135, 255)):  # Other dark tan
        return False
    if rgb_close(color_tup[1], (144, 173, 77, 255)):  # Light green cell border
        return False
    if color_tup[0] <= (info.cell_size ** 2 * 0.01):
        return False

    return True


def get_grid_index(coord, width):
    return coord[1] * width + coord[0]


def default_access(lst, index, default=0):
    try:
        if index < 0:
            return default

        return lst[index]
    except IndexError:
        return default


def get_neighbor_indexes(coord, width, height):
    index = coord[1] * width + coord[0]
    on_top = coord[1] == 0
    on_bottom = coord[1] == height - 1
    on_left = coord[0] == 0
    on_right = coord[0] == width - 1
    return [
        -99 if on_top or on_left else index - width - 1,
        -99 if on_top else index - width,
        -99 if on_top or on_right else index - width + 1,
        -99 if on_left else index - 1,
        index,
        -99 if on_right else index + 1,
        -99 if on_bottom or on_left else index + width - 1,
        -99 if on_bottom else index + width,
        -99 if on_bottom or on_right else index + width + 1,
    ]


def get_neighbors(indexes, grid):
    return list(map(partial(default_access, grid, default=99), indexes))


def neighbor_num_to_coord(index, reference):
    x, y = reference
    if index == 0:
        return x - 1, y - 1
    elif index == 1:
        return x, y - 1
    elif index == 2:
        return x + 1, y - 1
    elif index == 3:
        return x - 1, y
    elif index == 4:
        return x, y
    elif index == 5:
        return x + 1, y
    elif index == 6:
        return x - 1, y + 1
    elif index == 7:
        return x, y + 1
    elif index == 8:
        return x + 1, y + 1


def coord_in_game(info, coord):
    return 0 <= coord[0] < info.game_dim[0] and 0 <= coord[1] < info.game_dim[1]
