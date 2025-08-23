def card_value(card):
    """Return numeric value of a card for blackjack."""
    value = card["value"]
    if value in ["JACK", "QUEEN", "KING"]:
        return 10
    elif value == "ACE":
        return 11  # In blackjack, ACE can be 1 or 11; simplified as 11
    else:
        return int(value)

def is_blackjack(cards):
    """Check if the first 2 cards form a blackjack."""
    if len(cards) < 2:
        return False
    values = [card["value"] for card in cards[:2]]
    return "ACE" in values and any(v in values for v in ["10", "JACK", "QUEEN", "KING"])
