# These are the tool calls for the Agent to use on behalf of the dealer in the Blackjack game.

import random
from typing import Dict, List

deckMap: Dict[int, List[str]] = {}


# Define the card deck
def create_deck() -> List[str]:
    """Creates a standard deck of 52 cards."""
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["hearts", "diamonds", "clubs", "spades"]
    return [f"{rank} of {suit}" for rank in ranks for suit in suits]


# Shuffle the deck
def shuffle_deck(deck):
    """Shuffles the deck of cards."""
    random.shuffle(deck)
    return deck


# Deal initial cards
def deal_initial_cards(deck):
    """
    Deals initial cards for Blackjack:
    - Two cards for the player
    - Two cards for the dealer (one face-down)

    Args:
        deck (list): The shuffled deck of cards.

    Returns:
        dict: A dictionary with the initial hands of the player and dealer.
    """
    # Ensure there are enough cards in the deck
    if len(deck) < 4:
        raise ValueError("Not enough cards in the deck to deal initial hands.")

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


# Example usage
if __name__ == "__main__":
    # Create and shuffle the deck
    deck = create_deck()
    deck = shuffle_deck(deck)

    # Deal initial cards
    game_state = deal_initial_cards(deck)

    # Display results
    print("Player's Hand:", game_state["player_hand"])
    print("Dealer's Face-Up Card:", game_state["dealer_face_up"])
    print("Cards remaining in deck:", len(game_state["deck"]))
