# These are the tool calls for the Agent to use on behalf of the dealer in the Blackjack game.

import random
from typing import Dict, List

"""
Dict to store the card decks by player_id.
"""
deckMap: Dict[int, List[str]] = {}


# Define the card deck
def create_deck() -> List[str]:
    """Creates a standard deck of 52 cards."""
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["hearts", "diamonds", "clubs", "spades"]
    deck = [f"{rank} of {suit}" for rank in ranks for suit in suits]
    shuffle_deck(deck)
    return deck


# Shuffle the deck
def shuffle_deck(deck):
    """Shuffles the deck of cards."""
    random.shuffle(deck)
    return deck


# Deal initial cards
def deal_initial_cards(player_id: int):
    """
    Deals initial cards for Blackjack:
    - Two cards for the player
    - Two cards for the dealer (one face-down)

    Args:
        deck (list): The shuffled deck of cards.

    Returns:
        dict: A dictionary with the initial hands of the player and dealer.
    """

    # Get the deck for the player
    deck = deckMap.get(player_id)
    if deck is None:
        raise ValueError(f"Deck not found for player_id: {player_id}")

    # Ensure there are enough cards in the deck
    if len(deck) < 4:
        raise ValueError(
            f"Not enough cards in the deck to deal initial hands for player_id: {player_id}"
        )

    # Deal cards
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    # Return hands
    return {
        "player_hand": player_hand,
        "dealer_hand": dealer_hand,
        "dealer_face_up": dealer_hand[1],  # Second card is face-up
        "deck": deck,  # Return the modified deck
    }


# Hit (draw a card)
def hit(player_id: int, recipient: str) -> str:
    """
    Draws a card for the player or dealer.

    Args:
        player_id (int): The ID of the player.
        recipient (str): Either "player" or "dealer".

    Returns:
        str: The drawn card.
    """
    deck = deckMap.get(player_id)
    if deck is None or not deck:
        raise ValueError(f"Deck not found or is empty for player_id: {player_id}")

    # Draw a card
    card = deck.pop()
    return card


# Calculate hand value
def calculate_hand_value(hand: List[str]) -> Dict[str, int]:
    """
    Calculates the total value of a hand in Blackjack.

    Args:
        hand (list): List of cards in the hand.

    Returns:
        dict: The total value of the hand and whether it is soft or hard.
    """
    value = 0
    aces = 0

    for card in hand:
        rank = card.split(" ")[0]
        if rank in ["J", "Q", "K"]:
            value += 10
        elif rank == "A":
            value += 11
            aces += 1
        else:
            value += int(rank)

    # Adjust for aces if the hand is over 21
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1

    return {
        "total": value,
        "soft": aces > 0,  # True if the hand has a soft ace
    }


# Dealer's turn
def dealer_turn(player_id: int, dealer_hand: List[str]) -> List[str]:
    """
    Executes the dealer's turn by hitting until the dealer stands (17 or higher).

    Args:
        player_id (int): The ID of the player.
        dealer_hand (list): Dealer's initial hand.

    Returns:
        list: Final dealer hand after the turn.
    """
    while True:
        hand_value = calculate_hand_value(dealer_hand)
        if hand_value["total"] >= 17:  # Dealer stands on 17 or higher
            break
        dealer_hand.append(hit(player_id, "dealer"))

    return dealer_hand


# Check game status
def check_game_status(player_hand: List[str], dealer_hand: List[str]) -> str:
    """
    Checks the status of the game (win/loss/tie).

    Args:
        player_hand (list): The player's hand.
        dealer_hand (list): The dealer's hand.

    Returns:
        str: The game status ("player_blackjack", "dealer_blackjack", "player_bust",
             "dealer_bust", "player_win", "dealer_win", "tie").
    """
    player_value = calculate_hand_value(player_hand)["total"]
    dealer_value = calculate_hand_value(dealer_hand)["total"]

    if player_value > 21:
        return "player_bust"
    if dealer_value > 21:
        return "dealer_bust"
    if player_value == 21 and len(player_hand) == 2:
        return "player_blackjack"
    if dealer_value == 21 and len(dealer_hand) == 2:
        return "dealer_blackjack"
    if player_value > dealer_value:
        return "player_win"
    if player_value < dealer_value:
        return "dealer_win"
    return "tie"


# Reset the game
def reset_game(player_id: int):
    """
    Resets the game for the specified player, shuffling a new deck.

    Args:
        player_id (int): The ID of the player.
    """
    deckMap[player_id] = create_deck()


# Example usage
if __name__ == "__main__":
    # Initialize a game
    player_id = 1
    reset_game(player_id)

    # Deal initial cards
    game_state = deal_initial_cards(player_id)
    print("Player's Hand:", game_state["player_hand"])
    print("Dealer's Face-Up Card:", game_state["dealer_face_up"])

    # Simulate dealer's turn
    dealer_final_hand = dealer_turn(player_id, game_state["dealer_hand"])
    print("Dealer's Final Hand:", dealer_final_hand)

    # Check game status
    status = check_game_status(game_state["player_hand"], dealer_final_hand)
    print("Game Status:", status)
