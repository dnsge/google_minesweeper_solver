import time

import pyautogui

from google_minesweeper.game import GameInfo, locate_game, get_game_state, find_moves


def flag_coord(info: GameInfo, coord):
    position = info.cell_pos(coord)
    pyautogui.click(position, duration=0.1, button='right')


def click_coord(info: GameInfo, coord):
    position = info.cell_pos(coord)
    pyautogui.click(position, duration=0, button='left')


def main():
    game = locate_game()
    if not game:
        print('Could not locate game')
        return

    middle = game.game_dim[0] // 2, game.game_dim[1] // 2
    pyautogui.click(*game.cell_pos(middle), duration=0)

    while 1:
        time.sleep(0.6)  # Let animations finish
        state = get_game_state(game)
        moves = find_moves(game, state)

        if len(moves) == 0:
            print('\nNo more moves')
            r = input('\nUpdate and continue? (y/n) ')
            if r.lower()[0] == 'y':
                input('Press enter when ready. ')
                continue
            else:
                return

        for move in moves:
            if move[0] == 'flag':
                flag_coord(game, move[1])
            elif move[0] == 'click':
                click_coord(game, move[1])


if __name__ == '__main__':
    time.sleep(1)
    main()
