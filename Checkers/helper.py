from time import sleep


def make_first_move(page, total_rows, starting_row):
    """Handle moves 1 & 2"""
    _move_rows_first_coin(page, total_rows, starting_row)
    _wait_for_system(page)


def handle_third_move(page, total_rows, starting_row):
    """Handle move 3 with capture if possible"""
    row = starting_row - 1
    blue_coins = page.locator(
        f"xpath=//div[@id='board']/div[{row}]/*[contains(@src,'me1')]"
    )

    if blue_coins.count() > 0:
        _take_out_blue_coin(page, row, blue_coins)
    else:
        _move_rows_first_coin(page, total_rows, starting_row)

    _wait_for_system(page)


def handle_later_moves(page, total_rows, starting_row):
    """Handle moves 4 & 5 with capture if possible"""
    row = starting_row
    blue_coins = page.locator(
        f"xpath=//div[@id='board']/div[{row}]/*[contains(@src,'me1')]"
    )

    if blue_coins.count() > 0:
        _take_out_blue_coin(page, row, blue_coins)
    else:
        _move_rows_first_coin(page, total_rows, starting_row - 1)

    _wait_for_system(page)


""""Private helpers"""

def _wait_for_system(page):
    """Encapsulate system move check"""
    if _wait_system_move(page) == "Make a move":
        print("System responded with a move")
    else:
        raise RuntimeError("System did not respond in time")


def check_page_title(page):
    """Verify the page title is correct"""
    assert "Checkers" in page.title()
    print("Page title is valid")


def check_game_is_set_to_default(page, total_rows):
    """Verify that the game board is set to default starting position."""
    you_coins = page.locator("//div[@id='board']/div/*[contains(@src,'you1')]")
    me_coins = page.locator("//div[@id='board']/div/*[contains(@src,'me1')]")

    assert total_rows == 8, "Invalid number of rows"
    assert you_coins.count() == 12, "User coins are less than 12"
    assert me_coins.count() == 12, "System coins are less than 12"

    for i in range(1, total_rows + 1):
        if i in [1, 2, 3]:
            _assert_row_count(page, i, "me", 4)
        elif i in [6, 7, 8]:
            _assert_row_count(page, i, "you", 4)

    print("Game is set to default correctly")


def _assert_row_count(page, row, player, expected):
    """Helper to check number of pieces in a row"""
    count = page.locator(
        f"//div[@id='board']/div[{row}]/*[contains(@src,'{player}')]"
    ).count()
    assert count == expected, f"Row {row} expected {expected}, found {count}"


def _move_coin(page, piece, total_rows, row, col):
    """Move a piece to one of the possible positions"""
    possible_moves = [
        f"//div[@id='board']/div[{total_rows - (row + 1)}]/*[contains(@onclick,'{col + 1}, {row + 1}') and contains(@src,'gray')]",
        f"//div[@id='board']/div[{total_rows - (row + 1)}]/*[contains(@onclick,'{col - 1}, {row + 1}') and contains(@src,'gray')]",
    ]

    for xpath in possible_moves:
        next_move = page.locator(f"xpath={xpath}")
        if next_move.count() > 0:
            piece.click()
            next_move.click()
            break  # Only one move at a time


def _wait_system_move(page):
    """Wait for the system to make a move"""
    sleep(5)
    total = page.locator("//div[@id='board']/div/*[contains(@src,'me1')]").count()
    row1 = page.locator("//div[@id='board']/div[1]/*[contains(@src,'me1')]").count()
    row2 = page.locator("//div[@id='board']/div[2]/*[contains(@src,'me1')]").count()
    row3 = page.locator("//div[@id='board']/div[3]/*[contains(@src,'me1')]").count()

    if total != 12:
        print(f"System lost {12 - total} coins")

    system_move = (4 - row1) + (4 - row2) + (4 - row3)
    system_move -= (12 - total)

    # Count coins in rows 4-8
    coins_other_rows = sum(
        page.locator(f"//div[@id='board']/div[{i}]/*[contains(@src,'me1')]").count()
        for i in range(4, 9)
    )

    return "Make a move" if system_move == coins_other_rows else ""


def _move_rows_first_coin(page, total_rows, starting_row):
    """Move the first coin in a given row"""
    pieces = page.locator(f"//div[@id='board']/div[{starting_row}]/*[contains(@src,'you1')]")
    print(f"Coins in row {starting_row}: {pieces.count()}")

    piece = pieces.first
    pos = piece.get_attribute("onclick").removeprefix("didClick(").removesuffix(")")
    col, row = map(int, pos.split(","))

    _move_coin(page, piece, total_rows, row, col)
    return col, row


def _take_out_blue_coin(page, row, blue_coins):
    """Attempt to capture a blue coin if possible"""
    for i in range(blue_coins.count()):
        system_position = (
            blue_coins.nth(i).get_attribute("onclick")
            .removeprefix("didClick(").removesuffix(")")
        )
        col, row_val = map(int, system_position.split(","))

        xpath = ("//div[@id='board']/div[{row}]"
                 "/*[contains(@src,'{src}') and contains(@onclick,'{pos}')]")

        right_target = xpath.format(
            row=row - 1, src="gray", pos=f"{col - 1}, {row_val + 1}"
        )
        left_target = xpath.format(
            row=row - 1, src="gray", pos=f"{col + 1}, {row_val + 1}"
        )

        _try_capture(page, row, col, row_val, right_target, left_target, xpath)


def _try_capture(page, row, col, row_val, right_target, left_target, xpath):
    """Check if a capture is possible on either side"""
    if page.locator(f"xpath={right_target}").count() > 0:
        orange_coin = xpath.format(
            row=row + 1, src="you1", pos=f"{col + 1}, {row_val - 1}"
        )
        if page.locator(f"xpath={orange_coin}").count() > 0:
            page.locator(f"xpath={orange_coin}").click()
            page.locator(f"xpath={right_target}").click()

    elif page.locator(f"xpath={left_target}").count() > 0:
        orange_coin = xpath.format(
            row=row + 1, src="you1", pos=f"{col - 1}, {row_val - 1}"
        )
        if page.locator(f"xpath={orange_coin}").count() > 0:
            page.locator(f"xpath={orange_coin}").click()
            page.locator(f"xpath={left_target}").click()