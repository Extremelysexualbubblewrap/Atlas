import asyncio
import sys
import threading
from blockchain import Blockchain
from p2p import P2PServer
from wallet import Wallet
from transaction import Transaction

def print_blockchain(chain):
    print("\n" + "="*30 + " Blockchain " + "="*30)
    for block in chain:
        print(f"Index: {block.index} | Hash: {block.hash[:15]}... | Prev. Hash: {block.previous_hash[:15] if block.previous_hash else '0'}")
        print("Transactions:")
        for tx_dict in block.transactions:
            tx = Transaction.from_dict(tx_dict)
            if tx.sender == "network":
                print(f"  - REWARD -> {tx.recipient[:15]}... | Amount: {tx.amount}")
            else:
                print(f"  - From: {tx.sender[:15]}... -> To: {tx.recipient[:15]}... | Amount: {tx.amount} | Sig: {tx.signature[:10]}...")
        print("-" * 72)

def cli_loop(blockchain, p2p_server):
    """ The main interactive loop for the command-line interface. """
    wallet_filename = f"wallet_{port}.pem"
    wallet = Wallet(wallet_file=wallet_filename)

    while True:
        print("\n--- The Final Dollar CLI ---")
        print("1. Create New Wallet")
        print("2. View Wallet Address")
        print("3. Send Funds (Signed Transaction)")
        print("-" * 15)
        print("4. Mine a new block (Proof of Work)")
        print("5. Add stake (for Proof of Stake)")
        print("6. Forge a new block (Proof of Stake)")
        print("-" * 15)
        print("7. Display the blockchain")
        print("8. Check blockchain validity")
        print("9. List connected peers")
        print("10. Exit")

        try:
            choice = input("Enter your choice: ")
            if choice == '1':
                wallet.generate_keys()
            elif choice == '2':
                print(f"\nYour wallet address is: {wallet.address}")
            elif choice == '3':
                recipient = input("Enter recipient address: ")
                amount = int(input("Enter amount: "))
                tx = Transaction(sender=wallet.address, recipient=recipient, amount=amount)
                tx.sign(wallet)
                blockchain.add_transaction(tx)
                print("Signed transaction created and broadcasted.")
            elif choice == '4':
                # The miner reward can be sent to the current wallet's address
                blockchain.mine_block_pow(wallet.address)
            elif choice == '5':
                stake_amount = int(input("Enter amount to stake: "))
                blockchain.add_stake(wallet.address, stake_amount)
            elif choice == '6':
                blockchain.forge_block_pos()
            elif choice == '7':
                print_blockchain(blockchain.chain)
            elif choice == '8':
                is_valid = blockchain.is_chain_valid()
                print(f"\nThe blockchain is {'valid' if is_valid else 'NOT valid'}.")
            elif choice == '9':
                print(f"\nConnected Peers ({len(p2p_server.peers)}):")
                for i, peer in enumerate(p2p_server.peers):
                    print(f"  - Peer {i+1}: {peer.remote_address}")
            elif choice == '10':
                print("Exiting CLI... (The P2P server will continue to run)")
                break
            else:
                print("Invalid choice. Please try again.")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\nInvalid input or exiting. Please try again.")
        except Exception as e:
            print(f"An error occurred in CLI: {e}")

async def main(port, peers):
    """
    Initializes the blockchain, starts the P2P server, and runs the CLI.
    """
    the_final_dollar = Blockchain()
    p2p_server = P2PServer(blockchain=the_final_dollar)
    the_final_dollar.set_p2p_server(p2p_server)

    server_task = asyncio.create_task(p2p_server.start_server('0.0.0.0', port))

    for peer_uri in peers:
        asyncio.create_task(p2p_server.connect_to_peer(peer_uri))

    print("\n--- The Final Dollar Node is Running ---")

    # Run the blocking CLI in a separate thread
    cli_thread = threading.Thread(target=cli_loop, args=(the_final_dollar, p2p_server), daemon=True)
    cli_thread.start()

    await server_task

if __name__ == "__main__":
    try:
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
        peers = [f"ws://localhost:{p}" for p in sys.argv[2:]]
        asyncio.run(main(port, peers))
    except KeyboardInterrupt:
        print("\nShutting down node.")
    except Exception as e:
        print(f"An error occurred: {e}")