from core import endpoints
from core.utils import is_blackjack


def test_draw_cards_and_blackjack(client):
    """Check if Deck of Cards API is alive."""
    resp = client.get(endpoints.NEW_DECK)
    assert resp.status_code == 200

    """Simulate drawing cards and checking blackjack."""

    # Step 1: New deck
    deck_resp = client.get(endpoints.NEW_DECK)
    assert deck_resp.status_code == 200
    deck_id = deck_resp.json()["deck_id"]

    # Step 2: Shuffle the deck
    shuffle_resp = client.get(endpoints.SHUFFLE_DECK.format(deck_id=deck_id))
    assert shuffle_resp.status_code == 200
    assert shuffle_resp.json()["shuffled"] is True

    # Step 3: Draw 6 cards (3 each for 2 players)
    draw_resp = client.get(endpoints.DRAW_CARDS.format(deck_id=deck_id, count=6))
    assert draw_resp.status_code == 200
    cards = draw_resp.json()["cards"]

    player1, player2 = cards[:3], cards[3:]

    # Step 4: Verify blackjack logic
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


    assert isinstance(p1_blackjack, bool)
    assert isinstance(p2_blackjack, bool)