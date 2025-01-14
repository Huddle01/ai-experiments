import random
from typing import Dict, List, Literal, TypedDict


class GameState(TypedDict):
    deck: List[str]
    player_hand: List[str]
    dealer_hand: List[str]


"""
Dict to store the game_state of each player id
"""
game_state_map: Dict[int, GameState] = {}


# Define the card deck
def create_deck() -> List[str]:
    """Creates a standard deck of 52 cards."""
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["hearts", "diamonds", "clubs", "spades"]
    deck = [f"{rank} of {suit}" for rank in ranks for suit in suits]
    shuffle_deck(deck)
    return deck


# Shuffle the deck
def shuffle_deck(deck: List[str]) -> List[str]:
    """Shuffles the deck of cards."""
    random.shuffle(deck)
    return deck


# Reset the game
def reset_game(player_id: int):
    """
    Resets the game for the specified player, shuffling a new deck and resetting hands.

    Args:
        player_id (int): The ID of the player.
    """
    game_state_map[player_id] = {
        "deck": create_deck(),
        "player_hand": [],
        "dealer_hand": [],
    }


# Deal initial cards
def deal_initial_cards(player_id: int):
    """
    Deals initial cards for Blackjack:
    - Two cards for the player
    - Two cards for the dealer (one face-down).

    Args:
        player_id (int): The ID of the player.

    Returns:
        dict: A dictionary with the initial hands of the player and dealer.
    """
    game_state = game_state_map.get(player_id)
    if not game_state:
        raise ValueError(f"Game state not found for player_id: {player_id}")

    deck = game_state["deck"]

    # Ensure there are enough cards in the deck
    if len(deck) < 4:
        raise ValueError(
            f"Not enough cards in the deck to deal initial hands for player_id: {player_id}"
        )

    # Deal cards
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand: List[str] = [deck.pop(), deck.pop()]

    game_state["player_hand"] = player_hand
    game_state["dealer_hand"] = dealer_hand

    return {
        "player_hand": player_hand,
        "dealer_hand": dealer_hand,
        "dealer_face_up": dealer_hand[1],  # Second card is face-up
    }


RecipientType = Literal["player", "dealer"]


# Hit (draw a card)
def hit(player_id: int, recipient: RecipientType) -> str:
    """
    Draws a card for the player or dealer.

    Args:
        player_id (int): The ID of the player.
        recipient (str): Either "player" or "dealer".

    Returns:
        str: The drawn card.
    """
    game_state = game_state_map.get(player_id)
    if not game_state or not game_state["deck"]:
        raise ValueError(
            f"Game state not found or deck is empty for player_id: {player_id}"
        )

    card = game_state["deck"].pop()

    if recipient == "player":
        game_state["player_hand"].append(card)
    elif recipient == "dealer":
        game_state["dealer_hand"].append(card)
    else:
        raise ValueError(f"Invalid recipient: {recipient}")

    return card


class HandValue(TypedDict):
    total: int
    soft: bool


# Calculate hand value
def calculate_hand_value(hand: List[str]) -> HandValue:
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
def dealer_turn(player_id: int) -> List[str]:
    """
    Executes the dealer's turn by hitting until the dealer stands (17 or higher).

    Args:
        player_id (int): The ID of the player.

    Returns:
        list: Final dealer hand after the turn.
    """
    game_state = game_state_map.get(player_id)
    if not game_state:
        raise ValueError(f"Game state not found for player_id: {player_id}")

    dealer_hand = game_state["dealer_hand"]

    while True:
        hand_value = calculate_hand_value(dealer_hand)
        if hand_value["total"] >= 17:  # Dealer stands on 17 or higher
            break
        dealer_hand.append(hit(player_id, "dealer"))

    return dealer_hand


GameStateType = Literal[
    "player_bust",
    "dealer_bust",
    "player_blackjack",
    "dealer_blackjack",
    "player_win",
    "dealer_win",
    "tie",
]


# Check game status
def check_game_status(player_id: int) -> GameStateType:
    """
    Checks the status of the game (win/loss/tie).

    Args:
        player_id (int): The ID of the player.

    Returns:
        str: The game status.
    """
    game_state = game_state_map.get(player_id)
    if not game_state:
        raise ValueError(f"Game state not found for player_id: {player_id}")

    player_hand = game_state["player_hand"]
    dealer_hand = game_state["dealer_hand"]

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


if __name__ == "__main__":
    # Initialize a game
    player_id = 1
    reset_game(player_id)

    # Deal initial cards
    initial_state = deal_initial_cards(player_id)
    print("Player's Hand:", initial_state["player_hand"])
    print("Dealer's Face-Up Card:", initial_state["dealer_face_up"])

    # Player's turn loop
    while True:
        player_choice = input("Enter 'hit' or 'stand': ").strip().lower()
        if player_choice == "hit":
            hit(player_id, "player")
            print("Player's Hand:", game_state_map[player_id]["player_hand"])

            # Check if player busts
            player_value = calculate_hand_value(
                game_state_map[player_id]["player_hand"]
            )["total"]
            if player_value > 21:
                print("Player Busts!")
                break
        elif player_choice == "stand":
            print("Player stands.")
            break
        else:
            print("Invalid choice. Please enter 'hit' or 'stand'.")

    # Check if player busted before continuing
    player_value = calculate_hand_value(game_state_map[player_id]["player_hand"])[
        "total"
    ]
    if player_value <= 21:
        # Dealer's turn
        dealer_final_hand = dealer_turn(player_id)
        print("Dealer's Final Hand:", dealer_final_hand)

        # Check game status
        status = check_game_status(player_id)
        print("Game Status:", status)
