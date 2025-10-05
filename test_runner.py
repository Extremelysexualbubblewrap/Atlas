import os
from blockchain import Blockchain
from wallet import Wallet
from transaction import Transaction

def run_tests():
    """
    An automated test suite for the cryptocurrency, focusing on the
    wallet, signed transactions, and blockchain integration.
    """
    print("--- Running Full Automated Test Suite ---")

    # --- Wallet Tests ---
    print("\n--- Testing Wallet Functionality ---")

    # Create test wallets
    wallet1_file = "test_wallet1.pem"
    wallet2_file = "test_wallet2.pem"
    if os.path.exists(wallet1_file): os.remove(wallet1_file)
    if os.path.exists(wallet2_file): os.remove(wallet2_file)

    wallet1 = Wallet(wallet_file=wallet1_file)
    wallet2 = Wallet(wallet_file=wallet2_file)

    print("\n[Test 1] Wallet Generation")
    assert wallet1.private_key is not None and wallet1.public_key is not None
    assert wallet1.address is not None
    print("  - PASSED: Wallet 1 generated successfully.")
    assert wallet2.private_key is not None and wallet2.public_key is not None
    print("  - PASSED: Wallet 2 generated successfully.")

    # --- Transaction Tests ---
    print("\n--- Testing Transaction Signing and Verification ---")

    # Test 2: Create and sign a valid transaction
    print("\n[Test 2] Transaction Signing")
    tx = Transaction(sender=wallet1.address, recipient=wallet2.address, amount=50)
    tx.sign(wallet1)
    assert tx.signature is not None
    print("  - PASSED: Transaction signed successfully.")

    # Test 3: Verify a valid transaction
    print("\n[Test 3] Transaction Verification (Valid)")
    assert tx.is_valid()
    print("  - PASSED: Valid transaction verified successfully.")

    # Test 4: Fail to verify a tampered transaction
    print("\n[Test 4] Transaction Verification (Tampered)")
    tampered_tx = Transaction(sender=wallet1.address, recipient=wallet2.address, amount=51)
    tampered_tx.signature = tx.signature # Use the signature from the original transaction
    assert not tampered_tx.is_valid()
    print("  - PASSED: Tampered transaction correctly identified as invalid.")

    # Test 5: Fail to verify with wrong key
    print("\n[Test 5] Transaction Signing (Wrong Key)")
    try:
        tx_from_w2_signed_by_w1 = Transaction(sender=wallet2.address, recipient=wallet1.address, amount=10)
        tx_from_w2_signed_by_w1.sign(wallet1)
        # This should raise an exception
        assert False, "Should have failed to sign with the wrong wallet."
    except Exception as e:
        print(f"  - PASSED: Correctly threw exception when signing with wrong wallet: {e}")

    # --- Blockchain Integration Tests ---
    print("\n--- Testing Blockchain Integration with Secure Transactions ---")

    blockchain = Blockchain()

    # Test 6: Add a valid transaction to pending
    print("\n[Test 6] Add Valid Transaction to Blockchain")
    blockchain.add_transaction(tx)
    assert len(blockchain.pending_transactions) == 1
    assert blockchain.pending_transactions[0].signature == tx.signature
    print("  - PASSED: Valid signed transaction added to pending transactions.")

    # Test 7: Attempt to add an invalid transaction
    print("\n[Test 7] Add Invalid Transaction to Blockchain")
    blockchain.add_transaction(tampered_tx)
    assert len(blockchain.pending_transactions) == 1 # Should not have been added
    print("  - PASSED: Invalid transaction was not added to pending transactions.")

    # Test 8: Mine a block and check validity
    print("\n[Test 8] Mine Block and Validate Chain")
    blockchain.mine_block_pow(wallet2.address) # Miner reward to wallet 2
    assert len(blockchain.chain) == 2
    assert len(blockchain.pending_transactions) == 0
    print("  - PASSED: Block mined successfully.")

    # The is_chain_valid() method now checks transaction signatures inside blocks
    assert blockchain.is_chain_valid()
    print("  - PASSED: Blockchain is valid after mining a block with a signed transaction.")

    # Cleanup test wallet files
    if os.path.exists(wallet1_file): os.remove(wallet1_file)
    if os.path.exists(wallet2_file): os.remove(wallet2_file)

    print("\n--- All Wallet and Transaction Tests Passed Successfully! ---")

if __name__ == "__main__":
    run_tests()