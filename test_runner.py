from blockchain import Blockchain, Block

def run_tests():
    """
    An automated test suite to verify the hybrid PoW/PoS blockchain's functionality.
    """
    print("--- Running Automated Hybrid Blockchain Tests ---")

    # Initialize blockchain
    the_final_dollar = Blockchain()
    pow_miner_address = "test-pow-miner"
    validator_a = "validator-alice"
    validator_b = "validator-bob"

    # --- Proof of Work (PoW) Tests ---
    print("\n--- Testing Proof of Work (PoW) ---")

    # Test 1: Add transactions
    print("\n[Test 1] Adding transactions for PoW...")
    the_final_dollar.add_transaction({"from": "User1", "to": "User2", "amount": 50})
    assert len(the_final_dollar.pending_transactions) == 1, "PoW Test 1 Failed: Transaction not added."
    print("  - PASSED: Transaction added.")

    # Test 2: Mine a block with PoW
    print("\n[Test 2] Mining a new block with PoW...")
    the_final_dollar.mine_block_pow(pow_miner_address)
    assert len(the_final_dollar.chain) == 2, "PoW Test 2 Failed: PoW block not mined."
    assert len(the_final_dollar.pending_transactions) == 0, "PoW Test 2 Failed: Pending transactions not cleared."
    print("  - PASSED: PoW block mined and transactions cleared.")

    # --- Proof of Stake (PoS) Tests ---
    print("\n--- Testing Proof of Stake (PoS) ---")

    # Test 3: Add stake for validators
    print("\n[Test 3] Staking currency for PoS...")
    the_final_dollar.add_stake(validator_a, 10)
    the_final_dollar.add_stake(validator_b, 20)
    assert the_final_dollar.validators[validator_a] == 10, "PoS Test 3 Failed: Validator A stake incorrect."
    assert the_final_dollar.validators[validator_b] == 20, "PoS Test 3 Failed: Validator B stake incorrect."
    print("  - PASSED: Stakes correctly added for validators.")

    # Test 4: Forge a block with PoS
    print("\n[Test 4] Forging a new block with PoS...")
    the_final_dollar.add_transaction({"from": "User3", "to": "User4", "amount": 30})
    the_final_dollar.forge_block_pos()
    assert len(the_final_dollar.chain) == 3, "PoS Test 4 Failed: PoS block not forged."
    assert len(the_final_dollar.pending_transactions) == 0, "PoS Test 4 Failed: Pending transactions not cleared after forging."
    print("  - PASSED: PoS block forged and transactions cleared.")

    # --- Hybrid Model and Validity Tests ---
    print("\n--- Testing Hybrid Model & Validity ---")

    # Test 5: Check blockchain validity after hybrid operations
    print("\n[Test 5] Checking blockchain validity...")
    is_valid = the_final_dollar.is_chain_valid()
    assert is_valid, "Hybrid Test 5 Failed: Blockchain is invalid after PoW and PoS blocks."
    print("  - PASSED: Blockchain is valid.")

    # Test 6: Test validity after tampering
    print("\n[Test 6] Tampering with the blockchain and checking validity...")
    # Tamper with the data in a PoW block
    the_final_dollar.chain[1].transactions = [{"from": "Eve", "to": "Mallory", "amount": 999}]
    is_valid_after_tamper = not the_final_dollar.is_chain_valid()
    assert is_valid_after_tamper, "Hybrid Test 6 Failed: Tampering not detected."
    print("  - PASSED: Blockchain correctly detected tampering.")

    # Restore the chain for a clean final state
    the_final_dollar.chain[1].transactions = [{'from': 'User1', 'to': 'User2', 'amount': 50}, {'from': 'network', 'to': 'test-pow-miner', 'amount': 100}]
    the_final_dollar.chain[1].hash = the_final_dollar.chain[1].calculate_hash() # Recalculate hash to restore validity

    print("\n--- All Hybrid Tests Passed Successfully! ---")

if __name__ == "__main__":
    run_tests()