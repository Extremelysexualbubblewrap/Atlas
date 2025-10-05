import asyncio
import sys
import threading
from blockchain import Blockchain
from p2p import P2PServer

def print_blockchain(chain):
    for block in chain:
        print(f"  Index: {block.index}, Hash: {block.hash[:10]}..., Prev. Hash: {block.previous_hash[:10] if block.previous_hash else '0'}, Nonce: {block.nonce}")
        for tx in block.transactions:
            print(f"    - {tx}")
        print("-" * 20)

def cli_loop(blockchain, p2p_server):
    """ The main interactive loop for the command-line interface. """
    miner_address = "my-pow-miner-address"
    while True:
        print("\n--- The Final Dollar CLI ---")
        print("1. Add a new transaction")
        print("2. Mine a new block (Proof of Work)")
        print("3. Add stake (for Proof of Stake)")
        print("4. Forge a new block (Proof of Stake)")
        print("5. Display the blockchain")
        print("6. Check blockchain validity")
        print("7. List connected peers")
        print("8. Exit")

        try:
            choice = input("Enter your choice: ")
            if choice == '1':
                sender = input("Enter sender address: ")
                recipient = input("Enter recipient address: ")
                amount = int(input("Enter amount: "))
                blockchain.add_transaction({"from": sender, "to": recipient, "amount": amount})
                print("Transaction added and broadcasted.")
            elif choice == '2':
                print("Mining a new block with PoW...")
                blockchain.mine_block_pow(miner_address)
            elif choice == '3':
                validator = input("Enter your validator address to stake: ")
                stake_amount = int(input("Enter amount to stake: "))
                blockchain.add_stake(validator, stake_amount)
            elif choice == '4':
                blockchain.forge_block_pos()
            elif choice == '5':
                print("\n--- Blockchain ---")
                print_blockchain(blockchain.chain)
            elif choice == '6':
                is_valid = blockchain.is_chain_valid()
                print(f"\nThe blockchain is {'valid' if is_valid else 'NOT valid'}.")
            elif choice == '7':
                print(f"\nConnected Peers ({len(p2p_server.peers)}):")
                for i, peer in enumerate(p2p_server.peers):
                    print(f"  - Peer {i+1}: {peer.remote_address}")
            elif choice == '8':
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
    print("Starting CLI in a separate thread...")

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