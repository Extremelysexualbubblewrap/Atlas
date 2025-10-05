from block import Block
import random
import asyncio

class Blockchain:
    def __init__(self, consensus_mechanism='pow'):
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
        if validator_address in self.validators:
            self.validators[validator_address] += amount
        else:
            self.validators[validator_address] = amount
        print(f"{validator_address} staked {amount}. Total stake: {self.validators[validator_address]}")

    def mine_block_pow(self, mining_reward_address):
        reward_tx = {"from": "network", "to": mining_reward_address, "amount": 100}
        self.pending_transactions.append(reward_tx)
        block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        self.add_block(block)

    def forge_block_pos(self):
        if not self.validators:
            print("Cannot forge block: No validators with a stake.")
            return
        forger = random.choice(list(self.validators.keys()))
        reward_tx = {"from": "network", "to": forger, "amount": 50}
        self.pending_transactions.append(reward_tx)
        block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
        self.add_block(block)
        print(f"Block successfully forged by {forger} (PoS).")

    def add_transaction(self, transaction, broadcast=True):
        self.pending_transactions.append(transaction)
        if self.p2p_server and broadcast:
            asyncio.create_task(self.p2p_server.broadcast_new_transaction(transaction))

    def add_block(self, block, broadcast=True):
        """
        Adds a new block to the chain and handles broadcasting.
        """
        self.chain.append(block)
        self.pending_transactions = []
        if self.p2p_server and broadcast:
            asyncio.create_task(self.p2p_server.broadcast_new_block(block))

    def add_block_from_peer(self, block):
        """
        Adds a block received from a peer without re-broadcasting.
        """
        self.chain.append(block)
        # Clear pending transactions that are now in the new block
        self.pending_transactions = [
            tx for tx in self.pending_transactions
            if tx not in block.transactions
        ]
        print(f"Added block {block.index} from peer.")

    def replace_chain(self, new_chain_blocks):
        """
        Replaces the local chain with a new, longer, and valid chain.
        """
        if self.is_chain_valid(new_chain_blocks) and len(new_chain_blocks) > len(self.chain):
            print("Replacing local blockchain with the new longer valid chain.")
            self.chain = new_chain_blocks
            # Clear pending transactions that are now in the new chain
            all_txs = [tx for block in new_chain_blocks for tx in block.transactions]
            self.pending_transactions = [
                tx for tx in self.pending_transactions
                if tx not in all_txs
            ]
        else:
            print("Received chain is not valid or not longer. Not replacing.")

    def is_chain_valid(self, chain_to_validate=None):
        chain = chain_to_validate if chain_to_validate else self.chain
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True