import os
import random
from typing import Dict, List, Literal, TypedDict

from apps.blackjack.web3.main import BlackjackDealer


class GameState(TypedDict):
    bet_amount: int
    deck: List[str]
    player_hand: List[str]
    dealer_hand: List[str]


"""
Dict to store the game_state of each player id
"""
game_state_map: Dict[int, GameState] = {}

dealer = BlackjackDealer(
    rpc_url=os.getenv("RPC_URL") or "",
    contract_address=os.getenv("CONTRACT_ADDRESS") or "",
    owner_private_key=os.getenv("PRIVATE_KEY") or "",
)


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


# Deal initial cards
def create_game_session_and_deal_initial_cards(player_id: int, bet_amount: int):
    """
    Creates a new game session using player_id and
    Deals initial cards for Blackjack:
    - Two cards for the player
    - Two cards for the dealer (one face-down).

    Args:
        player_id (int): The ID of the player.

    Returns:
        dict: A dictionary with the initial hands of the player and dealer.
    """
    bal = dealer.get_balance(player_id)

    if bal < bet_amount:
        raise ValueError(f"Not enough balance for player_id: {player_id}")

    game_state = game_state_map.get(player_id)
    if not game_state:
        game_state_map[player_id] = {
            "deck": create_deck(),
            "bet_amount": bet_amount,
            "player_hand": [],
            "dealer_hand": [],
        }
        dealer.place_bet(player_id, bet_amount)
        game_state = game_state_map[player_id]

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
        "dealer_face_up": dealer_hand[1],  # Second card is face-up
    }


tool_create_game_session_and_deal_initial_cards = {
    "name": "create_game_session_and_deal_initial_cards",
    "description": "Creates a new game session using player_id and deals initial cards for Blackjack. Two cards are dealt to the player and two cards to the dealer (one face-down).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "player_id": {
                "type": "INTEGER",
                "description": "The unique ID of the player for whom the game session is being created and initial cards are dealt.",
            },
            "bet_amount": {
                "type": "INTEGER",
                "description": "The amount of the bet placed by the player.",
            },
        },
        "required": ["player_id"],
    },
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


tool_hit = {
    "name": "hit",
    "description": "Draws a card for the specified recipient (PLAYER or DEALER) in a Blackjack game.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "player_id": {
                "type": "INTEGER",
                "description": "The unique ID of the player whose game session is active.",
            },
            "recipient": {
                "type": "STRING",
                "enum": ["player", "dealer"],
                "description": "The recipient of the drawn card. Can be either 'player' or 'dealer'.",
            },
        },
        "required": ["player_id", "recipient"],
    },
}


class HandValue(TypedDict):
    total: int
    soft: bool


# Calculate hand value
def calculate_hand_value(player_id: int, recipient: RecipientType) -> HandValue:
    """
    Calculates the total value of a hand in Blackjack.

    Args:
        hand (list): List of cards in the hand.

    Returns:
        dict: The total value of the hand and whether it is soft or hard.
    """
    value = 0
    aces = 0

    hand = game_state_map[player_id].get("player_hand")
    if recipient == "dealer":
        hand = game_state_map[player_id].get("dealer_hand")

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


tool_calculate_hand_value = {
    "name": "calculate_hand_value",
    "description": "Calculates the total value of a hand in Blackjack, determining whether it is soft or hard.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "player_id": {
                "type": "INTEGER",
                "description": "The unique ID of the player whose game session is active.",
            },
            "recipient": {
                "type": "STRING",
                "enum": ["player", "dealer"],
                "description": "The recipient of the drawn card. Can be either 'player' or 'dealer'.",
            },
        },
        "required": ["player_id", "recipient"],
    },
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
        hand_value = calculate_hand_value(player_id, "dealer")
        if hand_value["total"] >= 17:  # Dealer stands on 17 or higher
            break
        dealer_hand.append(hit(player_id, "dealer"))

    return dealer_hand


tool_dealer_turn = {
    "name": "dealer_turn",
    "description": "Executes the dealer's turn in a Blackjack game by hitting until the dealer stands (17 or higher).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "player_id": {
                "type": "INTEGER",
                "description": "The unique ID of the player whose dealer's turn is being executed.",
            }
        },
        "required": ["player_id"],
    },
}

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


class GameStateResult(TypedDict):
    game_state: GameStateType
    amount: float


def check_game_status(player_id: int) -> GameStateResult:
    """
    Checks the status of the game (win/loss/tie).

    Args:
        player_id (int): The ID of the player.

    Returns:
        str: The current game state : "player_bust",
        "dealer_bust",
        "player_blackjack",
        "dealer_blackjack",
        "player_win",
        "dealer_win",
        "tie",
    """
    game_state = game_state_map.get(player_id)
    if not game_state:
        raise ValueError(f"Game state not found for player_id: {player_id}")

    player_hand = game_state["player_hand"]
    dealer_hand = game_state["dealer_hand"]
    bet_amount = game_state["bet_amount"]

    player_value = calculate_hand_value(player_id, "player")["total"]
    dealer_value = calculate_hand_value(player_id, "dealer")["total"]

    if player_value > 21:
        return {"game_state": "player_bust", "amount": -bet_amount}
    if dealer_value > 21:
        return {"game_state": "dealer_bust", "amount": 2 * bet_amount}
    if player_value == 21 and len(player_hand) == 2:
        return {"game_state": "player_blackjack", "amount": 5 / 2 * bet_amount}
    if dealer_value == 21 and len(dealer_hand) == 2:
        return {"game_state": "dealer_blackjack", "amount": -bet_amount}
    if player_value > dealer_value:
        return {"game_state": "player_win", "amount": 2 * bet_amount}
    if player_value < dealer_value:
        return {"game_state": "dealer_win", "amount": -bet_amount}

    return {"game_state": "dealer_win", "amount": 0}


tool_check_game_status = {
    "name": "check_game_status",
    "description": """Checks the status of the game (win/loss/tie).

    Args:
        player_id (int): The ID of the player.

    Returns:
        str: The current game state : "player_bust",
        "dealer_bust",
        "player_blackjack",
        "dealer_blackjack",
        "player_win",
        "dealer_win",
        "tie",""",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "player_id": {
                "type": "INTEGER",
                "description": "The unique ID of the player whose game status is being checked.",
            }
        },
        "required": ["player_id"],
    },
}

if __name__ == "__main__":
    # Initialize a game
    player_id = 1
    # Deal initial cards
    initial_state = create_game_session_and_deal_initial_cards(player_id, 10)
    print("Player's Hand:", initial_state["player_hand"])
    print("Dealer's Face-Up Card:", initial_state["dealer_face_up"])

    # Player's turn loop
    while True:
        player_choice = input("Enter 'hit' or 'stand': ").strip().lower()
        if player_choice == "hit":
            hit(player_id, "player")
            print("Player's Hand:", game_state_map[player_id]["player_hand"])

            # Check if player busts
            player_value = calculate_hand_value(player_id, "player")["total"]
            if player_value > 21:
                print("Player Busts!")
                break
        elif player_choice == "stand":
            print("Player stands.")
            break
        else:
            print("Invalid choice. Please enter 'hit' or 'stand'.")

    # Check if player busted before continuing
    player_value = calculate_hand_value(player_id, "player")["total"]
    if player_value <= 21:
        # Dealer's turn
        dealer_final_hand = dealer_turn(player_id)
        print("Dealer's Final Hand:", dealer_final_hand)

        # Check game status
        status = check_game_status(player_id)
        game_state = dealer.GameState[status["game_state"]]
        dealer.resolve_game(player_id, game_state)
        print("Game Status:", status)
