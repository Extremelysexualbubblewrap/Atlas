from block import Block
from transaction import Transaction
import random
import asyncio

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 2
        self.validators = {}  # Address -> Stake
        self.p2p_server = None

    def set_p2p_server(self, p2p_server):
        self.p2p_server = p2p_server

    def create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_stake(self, validator_address, amount):
        # Note: In a real system, this would be a transaction and would
        # require a balance check. Simplified for now.
        if validator_address in self.validators:
            self.validators[validator_address] += amount
        else:
            self.validators[validator_address] = amount
        print(f"{validator_address} staked {amount}. Total stake: {self.validators[validator_address]}")

    def mine_block_pow(self, mining_reward_address):
        reward_tx = Transaction(sender="network", recipient=mining_reward_address, amount=100)

        # In this version, we assume pending transactions are valid when added
        transactions_for_block = [reward_tx] + self.pending_transactions

        block = Block(
            len(self.chain),
            [tx.to_dict() for tx in transactions_for_block],
            self.get_latest_block().hash
        )
        block.mine_block(self.difficulty)

        self.add_block(block)
        print("Block successfully mined (PoW).")

    def forge_block_pos(self):
        if not self.validators:
            print("Cannot forge block: No validators with a stake.")
            return
        forger = random.choice(list(self.validators.keys()))
        reward_tx = Transaction("network", forger, 50)

        transactions_for_block = [reward_tx] + self.pending_transactions

        block = Block(
            len(self.chain),
            [tx.to_dict() for tx in transactions_for_block],
            self.get_latest_block().hash
        )
        self.add_block(block)
        print(f"Block successfully forged by {forger} (PoS).")

    def add_transaction(self, transaction: Transaction, broadcast=True):
        if not transaction.is_valid():
            print("Discarding invalid transaction (signature check failed).")
            return

        self.pending_transactions.append(transaction)

        if self.p2p_server and broadcast:
            asyncio.create_task(self.p2p_server.broadcast_new_transaction(transaction.to_dict()))

    def add_block(self, block, broadcast=True):
        """
        Adds a new block to the chain, clears pending transactions, and handles broadcasting.
        """
        self.chain.append(block)

        # Clear pending transactions that are included in the new block
        block_tx_dicts = block.transactions
        self.pending_transactions = [
            pending_tx for pending_tx in self.pending_transactions
            if pending_tx.to_dict() not in block_tx_dicts
        ]

        if self.p2p_server and broadcast:
            asyncio.create_task(self.p2p_server.broadcast_new_block(block))

    def add_block_from_peer(self, block):
        # We should validate the block before adding it.
        # The synchronization logic in p2p.py already does some checks.
        # A full validation would be more robust.
        self.add_block(block, broadcast=False)
        print(f"Added block {block.index} from peer.")

    def replace_chain(self, new_chain_blocks):
        if self.is_chain_valid(new_chain_blocks) and len(new_chain_blocks) > len(self.chain):
            print("Replacing local blockchain with the new longer valid chain.")
            self.chain = new_chain_blocks
            # A simple approach to clearing pending transactions
            self.pending_transactions = []
        else:
            print("Received chain is not valid or not longer. Not replacing.")

    def is_chain_valid(self, chain_to_validate=None):
        chain = chain_to_validate if chain_to_validate else self.chain
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                print(f"Block {current_block.index} hash is invalid.")
                return False
            if current_block.previous_hash != previous_block.hash:
                print(f"Chain link broken at Block {current_block.index}.")
                return False

            # Validate all transactions within the block
            for tx_dict in current_block.transactions:
                tx = Transaction.from_dict(tx_dict)
                if not tx.is_valid():
                    print(f"Invalid transaction found in block {current_block.index}: {tx_dict}")
                    return False
        return True