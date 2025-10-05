import time
import hashlib
from wallet import Wallet

class Transaction:
    def __init__(self, sender, recipient, amount, signature=None):
        self.sender = sender  # Sender's public key (address)
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
        self.signature = signature

    def to_dict(self):
        """
        Returns a dictionary representation of the transaction.
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature,
        }

    @classmethod
    def from_dict(cls, tx_dict):
        """
        Creates a Transaction object from a dictionary.
        """
        tx = cls(
            sender=tx_dict['sender'],
            recipient=tx_dict['recipient'],
            amount=tx_dict['amount'],
            signature=tx_dict.get('signature')
        )
        # Manually set the timestamp from the dictionary to avoid a new one being generated
        tx.timestamp = tx_dict['timestamp']
        return tx

    def calculate_hash(self):
        """
        Calculates the hash of the transaction, which is what gets signed.
        The signature itself is not included in the hash.
        """
        tx_string = f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"
        return hashlib.sha256(tx_string.encode()).digest()

    def sign(self, wallet):
        """
        Signs the transaction with the provided wallet's private key.
        """
        if wallet.address != self.sender:
            raise Exception("You can only sign transactions from your own wallet.")

        tx_hash = self.calculate_hash()
        self.signature = wallet.sign_transaction(tx_hash)

    def is_valid(self):
        """
        Validates the transaction.
        Checks if the signature is valid and the transaction is well-formed.
        """
        if self.sender == "network":  # Reward transaction
            return True
        if not self.signature:
            print("Transaction validation failed: No signature.")
            return False

        tx_hash = self.calculate_hash()
        is_signature_valid = Wallet.verify_signature(self.sender, self.signature, tx_hash)
        if not is_signature_valid:
            print("Transaction validation failed: Invalid signature.")
            return False

        if self.amount <= 0:
            print("Transaction validation failed: Amount must be positive.")
            return False

        return True