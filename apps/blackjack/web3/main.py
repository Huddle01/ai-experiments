from web3 import Web3
from eth_account import Account
import json

class BlackjackDealer:
    """
    A Python class to interact with the Blackjack smart contract.
    """

    # Mirror of the GameState enum in the contract for convenience:
    # enum GameState {
    #   PLAYER_BUST,
    #   DEALER_BUST,
    #   PLAYER_BLACKJACK,
    #   DEALER_BLACKJACK,
    #   PLAYER_WIN,
    #   DEALER_WIN,
    #   TIE
    # }

    GameState = {
        'PLAYER_BUST': 0,
        'DEALER_BUST': 1,
        'PLAYER_BLACKJACK': 2,
        'DEALER_BLACKJACK': 3,
        'PLAYER_WIN': 4,
        'DEALER_WIN': 5,
        'TIE': 6
    }

    def __init__(self, 
                 rpc_url: str, 
                 contract_address: str,
                 owner_private_key: str
                 ):
        """
        :param rpc_url: The HTTP/S RPC URL for the Ethereum network.
        :param contract_address: Deployed address of the Blackjack contract.
        :param contract_abi: ABI of the Blackjack contract.
        :param owner_private_key: Private key of the contract owner (dealer).
        """
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

        with open("./abi/Blackjack.json") as f:
            contract_abi = json.load(f)

        self.contract = self.web3.eth.contract(
            address=self.web3.toChecksumAddress(contract_address),
            abi=contract_abi
        )
        
        self.owner_account = Account.from_key(owner_private_key)

    def get_balance(self, player_id: int) -> int:
        """
        Returns the balance of the given player_id (in wei).
        """
        return self.contract.functions.getBalance(player_id).call()

    def place_bet(self, player_private_key: str, player_id: int, bet_amount_wei: int):
        """
        Player places a bet of bet_amount_wei for the given player_id.
        """
        player_account = Account.from_key(player_private_key)
        tx = self.contract.functions.placeBet(player_id, bet_amount_wei).build_transaction({
            'from': player_account.address,
            'nonce': self.web3.eth.get_transaction_count(player_account.address),
            'gas': 300000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=player_private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def resolve_game(self, player_id: int, game_state: int):
        """
        Dealer/owner resolves the game by passing the result (game_state).
        Only the owner can call this in the contract.
        """
        tx = self.contract.functions.resolveGame(player_id, game_state).build_transaction({
            'from': self.owner_account.address,
            'nonce': self.web3.eth.get_transaction_count(self.owner_account.address),
            'gas': 300000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.owner_account.key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def withdraw_funds(self, player_private_key: str, player_id: int, amount_wei: int):
        """
        Player withdraws 'amount_wei' from their balance.
        """
        player_account = Account.from_key(player_private_key)
        tx = self.contract.functions.withdraw(player_id, amount_wei).build_transaction({
            'from': player_account.address,
            'nonce': self.web3.eth.get_transaction_count(player_account.address),
            'gas': 300000,
            'gasPrice': self.web3.eth.gas_price
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=player_private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt
