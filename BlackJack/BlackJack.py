import requests

BASE_URL = "https://deckofcardsapi.com/api/deck"

def get_new_deck():
    """Get and shuffle a new deck"""
    url = f"{BASE_URL}/new/shuffle/?deck_count=1"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["deck_id"]

def draw_cards(deck_id, count=1):
    """Draw cards from deck"""
    url = f"{BASE_URL}/{deck_id}/draw/?count={count}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["cards"]

def card_value(card):
    """Return numeric value of a card for blackjack"""
    value = card["value"]
    if value in ["JACK", "QUEEN", "KING"]:
        return 10
    elif value == "ACE":
        return 11  # in blackjack, ACE can be 1 or 11, but for blackjack check we count 11
    else:
        return int(value)

def is_blackjack(cards):
    """Check if the first 2 cards form a blackjack"""
    if len(cards) < 2:
        return False
    values = [card["value"] for card in cards[:2]]
    if "ACE" in values and any(v in values for v in ["10", "JACK", "QUEEN", "KING"]):
        return True
    return False

if __name__ == "__main__":
    # Step 1: Confirm site up
    try:
        r = requests.get(f"{BASE_URL}/new/shuffle/?deck_count=1")
        if r.status_code == 200:
            print("Deck of Cards API is up!")
        else:
            print("API might be down.")
    except Exception as e:
        print("Could not reach API:", e)
        exit(1)

    # Step 2: Get new deck
    deck_id = get_new_deck()
    print(f"New shuffled deck created: {deck_id}")

    # Step 3: Deal 3 cards each
    cards = draw_cards(deck_id, 6)
    player1 = cards[:3]
    player2 = cards[3:]

    print("\nPlayer 1 cards:", [f"{c['value']} of {c['suit']}" for c in player1])
    print("Player 2 cards:", [f"{c['value']} of {c['suit']}" for c in player2])

    # Step 4: Check blackjack
    p1_blackjack = is_blackjack(player1)
    p2_blackjack = is_blackjack(player2)

    if p1_blackjack and p2_blackjack:
        print("\nBoth players have blackjack!")
    elif p1_blackjack:
        print("\nPlayer 1 has blackjack!")
    elif p2_blackjack:
        print("\nPlayer 2 has blackjack!")
    else:
        print("\nNo blackjack this round.")
