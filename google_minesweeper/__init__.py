import time

import pyautogui

from google_minesweeper.game import GameInfo, locate_game, get_game_state, find_moves
from google_minesweeper.util import get_grid_coord


def flag_coord(info: GameInfo, coord):
    position = info.cell_pos(coord)
    pyautogui.click(position, duration=0.1, button='right')


def click_coord(info: GameInfo, coord):
    position = info.cell_pos(coord)
    pyautogui.click(position, duration=0, button='left')


def check_win(game: GameInfo, state):
    return state.count(-1) == game.flag_total - len(game.flagged)


def fail_game(game: GameInfo):
    if len(game.flagged) == 0:
        return False

    index = game.flagged[0]
    coord = get_grid_coord(index, game.game_dim[0])
    flag_coord(game, coord)  # Remove flag
    click_coord(game, coord)  # Click mine on purpose
    game.flagged.pop(0)
    time.sleep(2)
    click_coord(game, coord)  # Click again to end animation
    return True


def click_game_button(game: GameInfo):
    pyautogui.click((game.br[0] + game.tl[0]) // 2, (2 * game.br[1] + game.tl[1]) // 3)


def main():
    running = True
    while running:
        game = locate_game()
        if not game:
            print('Could not locate game')
            return

        middle = game.game_dim[0] // 2, game.game_dim[1] // 2
        pyautogui.click(*game.cell_pos(middle), duration=0)
        tries = 0
        while 1:
            time.sleep(0.8)  # Let animations finish
            state = get_game_state(game)

            if not state:
                if tries >= 3:
                    print('Lost focus of game')
                    return

                tries += 1
                time.sleep(1)
                continue
            else:
                tries = 0

            moves = find_moves(game, state)

            if len(moves) == 0:
                if check_win(game, state):
                    print('\nGame won')
                    click_coord(game, (0, 0))
                    break

                fail_game(game)
                break

            for move in moves:
                if move[0] == 'flag':
                    flag_coord(game, move[1])
                elif move[0] == 'click':
                    click_coord(game, move[1])

            if check_win(game, state):
                print('\nGame won')
                click_coord(game, (0, 0))
                break

        time.sleep(1)
        click_game_button(game)
        time.sleep(2)


if __name__ == '__main__':
    time.sleep(1)
    main()
