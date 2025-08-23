from helper import (
    check_page_title,
    check_game_is_set_to_default,
    make_first_move,
    handle_third_move,
    handle_later_moves,
)


def test_checkers_make_moves(page):
    """Verify game starts correctly"""
    check_page_title(page) #Validate page load
    total_rows = page.locator("xpath=//div[@id='board']/div").count() #Count the number of rows
    check_game_is_set_to_default(page, total_rows) #Verify game is set to default mode.

    #set the row to make first move
    starting_row = 6

    #make moves
    for move in range(1, 6):
        print(f"\nCurrent move: {move}")

        if move in (1, 2):
            make_first_move(page, total_rows, starting_row)

        elif move == 3:
            handle_third_move(page, total_rows, starting_row)

        elif move in (4, 5):
            handle_later_moves(page, total_rows, starting_row)

    # Restart the game and recheck board
    page.get_by_text("Restart...").click()
    check_game_is_set_to_default(page, total_rows)
    print("All checks passed successfully")
