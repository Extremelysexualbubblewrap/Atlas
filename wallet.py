import ecdsa
import os
import hashlib

class Wallet:
    def __init__(self, wallet_file='wallet.pem'):
        self.wallet_file = wallet_file
        self.private_key = None
        self.public_key = None
        self.address = None
        self.load_wallet()

    def generate_keys(self):
        """
        Generates a new private/public key pair using ECDSA.
        """
        # SECP256k1 is the curve used by Bitcoin
        self.private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        self.address = self.public_key.to_string().hex()
        self.save_wallet()
        print(f"New wallet generated and saved to {self.wallet_file}")
        print(f"Your new address is: {self.address}")

    def save_wallet(self):
        """
        Saves the private key to a file.
        """
        if self.private_key:
            with open(self.wallet_file, "wb") as f:
                f.write(self.private_key.to_pem())
            print(f"Wallet saved to {self.wallet_file}")

    def load_wallet(self):
        """
        Loads a private key from a file. If the file doesn't exist,
        a new wallet is generated.
        """
        if os.path.exists(self.wallet_file):
            with open(self.wallet_file, "rb") as f:
                self.private_key = ecdsa.SigningKey.from_pem(f.read())
            self.public_key = self.private_key.get_verifying_key()
            self.address = self.public_key.to_string().hex()
            print(f"Wallet loaded from {self.wallet_file}")
            print(f"Your address is: {self.address}")
        else:
            print("No wallet file found. Generating a new wallet...")
            self.generate_keys()

    def sign_transaction(self, transaction_hash):
        """
        Signs a transaction hash with the private key.
        """
        if self.private_key:
            return self.private_key.sign(transaction_hash).hex()
        else:
            raise Exception("Wallet is not loaded. Cannot sign transaction.")

    @staticmethod
    def verify_signature(public_key_hex, signature_hex, transaction_hash):
        """
        Verifies a signature against a public key and transaction hash.
        """
        try:
            public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1)
            return public_key.verify(bytes.fromhex(signature_hex), transaction_hash)
        except (ecdsa.BadSignatureError, ValueError):
            return False