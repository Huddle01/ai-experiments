from eth_account import Account
from web3 import AsyncWeb3, WebSocketProvider
from web3.middleware import


class Web3WalletHandler:

    def __init__(self):
        """
        Initializes the Web3 Wallet Handler with a WebSocket provider.

        Args:
            websocket_url (str): The WebSocket URL of the Ethereum node.
        """

        websocket_url="wss://huddle-testnet.rpc.caldera.xyz/ws"
        self.w3 = AsyncWeb3(WebSocketProvider(websocket_url))

        # Add the POA middleware for compatibility with networks like BSC or Polygon
        self.w3.middleware_onion.add()

        if not self.w3.is_connected():
            raise ConnectionError(
                "Failed to connect to the Ethereum WebSocket provider."
            )
        print("Connected to Ethereum WebSocket provider.")

    def create_wallet(self):
        """
        Creates a new Ethereum wallet.

        Returns:
            dict: A dictionary containing the address and private key.
        """
        account = Account.create()
        wallet = {
            "address": account.address,
            "private_key": account.key.hex(),
        }
        print(f"New wallet created: {wallet['address']}")
        return wallet

    def get_balance(self, address: str):
        """
        Gets the Ether balance of an Ethereum address.

        Args:
            address (str): The Ethereum address to query.

        Returns:
            float: The balance in Ether.
        """
        balance_wei = self.w3.eth.get_balance(address)
        balance_eth = self.w3.fromWei(balance_wei, "ether")
        print(f"Balance for {address}: {balance_eth} ETH")
        return balance_eth

    def send_transaction(
        self,
        private_key: str,
        to_address: str,
        value_eth: float,
        gas: int = 21000,
        gas_price_gwei: int = 50,
    ):
        """
        Sends a transaction from one address to another.

        Args:
            private_key (str): The private key of the sender's wallet.
            to_address (str): The recipient's Ethereum address.
            value_eth (float): The amount to send in Ether.
            gas (int): The gas limit for the transaction.
            gas_price_gwei (int): The gas price in Gwei.

        Returns:
            str: The transaction hash.
        """
        from_account = Account.from_key(private_key)
        nonce = self.w3.eth.get_transaction_count(from_account.address)

        # Prepare transaction
        tx = {
            "nonce": nonce,
            "to": to_address,
            "value": self.w3.toWei(value_eth, "ether"),
            "gas": gas,
            "gasPrice": self.w3.toWei(gas_price_gwei, "gwei"),
        }

        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)

        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction sent with hash: {tx_hash.hex()}")
        return tx_hash.hex()

    def get_transaction_receipt(self, tx_hash: str):
        """
        Fetches the receipt of a transaction.

        Args:
            tx_hash (str): The hash of the transaction.

        Returns:
            dict: The transaction receipt.
        """
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction receipt: {receipt}")
        return receipt


# Example Usage
if __name__ == "__main__":
    # Initialize Web3WalletHandler with a WebSocket provider
    wallet_handler = Web3WalletHandler()

    # Create a new wallet
    wallet = wallet_handler.create_wallet()

    # Check the balance of the wallet
    wallet_handler.get_balance(wallet["address"])

    # Send a transaction (example, replace with actual values)
    # Replace `TO_ADDRESS` with the recipient's address
    # wallet_handler.send_transaction(wallet["private_key"], "TO_ADDRESS", 0.01)
