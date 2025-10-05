from block import Block
import random

class Blockchain:
    def __init__(self, consensus_mechanism='pow'):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 2
        self.validators = {} # Address -> Stake
        self.consensus_mechanism = consensus_mechanism

    def create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_stake(self, validator_address, amount):
        if validator_address in self.validators:
            self.validators[validator_address] += amount
        else:
            self.validators[validator_address] = amount
        print(f"{validator_address} staked {amount}. Total stake: {self.validators[validator_address]}")

    def mine_block_pow(self, mining_reward_address):
        """
        Mines a new block using Proof of Work.
        """
        reward_tx = {
            "from": "network",
            "to": mining_reward_address,
            "amount": 100 # PoW reward
        }
        self.pending_transactions.append(reward_tx)

        block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
        block.mine_block(self.difficulty)

        print("Block successfully mined (PoW).")
        self.chain.append(block)
        self.pending_transactions = []

    def forge_block_pos(self):
        """
        Forges a new block using Proof of Stake.
        A validator is chosen to forge the block based on their stake.
        """
        if not self.validators:
            print("Cannot forge block: No validators with a stake.")
            return

        # Create a pool of validators weighted by their stake
        validator_pool = []
        for validator, stake in self.validators.items():
            # The higher the stake, the more entries in the pool, the higher the chance to be chosen
            validator_pool.extend([validator] * stake)

        if not validator_pool:
            print("Cannot forge block: No stakes available.")
            return

        # Choose a forger from the weighted pool
        forger = random.choice(validator_pool)
        print(f"Validator {forger} selected to forge the next block.")

        reward_tx = {
            "from": "network",
            "to": forger,
            "amount": 50  # PoS reward
        }
        self.pending_transactions.append(reward_tx)

        block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
        # In PoS, no intensive mining is required. The block is created and added.
        # The security comes from the validator's economic stake in the network.

        self.chain.append(block)
        self.pending_transactions = []
        print(f"Block successfully forged by {forger} (PoS).")


    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                print(f"Validation Error: Block {current_block.index} hash is invalid.")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"Validation Error: Chain link broken at Block {current_block.index}.")
                return False
        return True