from blockchain import Blockchain

def print_blockchain(chain):
    for block in chain:
        print("Index:", block.index)
        print("Transactions:", block.transactions)
        print("Timestamp:", block.timestamp)
        print("Hash:", block.hash)
        print("Previous Hash:", block.previous_hash)
        print("Nonce:", block.nonce)
        print("-" * 20)

def main():
    the_final_dollar = Blockchain()
    miner_address = "my-pow-miner-address"

    while True:
        print("\n--- The Final Dollar CLI ---")
        print("1. Add a new transaction")
        print("2. Mine a new block (Proof of Work)")
        print("3. Add stake (for Proof of Stake)")
        print("4. Forge a new block (Proof of Stake)")
        print("5. Display the blockchain")
        print("6. Check blockchain validity")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            sender = input("Enter sender address: ")
            recipient = input("Enter recipient address: ")
            try:
                amount = int(input("Enter amount: "))
                the_final_dollar.add_transaction({
                    "from": sender,
                    "to": recipient,
                    "amount": amount
                })
                print("Transaction added to pending transactions.")
            except ValueError:
                print("Invalid amount. Please enter a number.")

        elif choice == '2':
            print("Mining a new block with PoW...")
            the_final_dollar.mine_block_pow(miner_address)

        elif choice == '3':
            validator = input("Enter your validator address to stake: ")
            try:
                stake_amount = int(input("Enter amount to stake: "))
                the_final_dollar.add_stake(validator, stake_amount)
            except ValueError:
                print("Invalid stake amount. Please enter a number.")

        elif choice == '4':
            the_final_dollar.forge_block_pos()

        elif choice == '5':
            print("\n--- The Final Dollar Blockchain ---")
            print_blockchain(the_final_dollar.chain)

        elif choice == '6':
            is_valid = the_final_dollar.is_chain_valid()
            if is_valid:
                print("\nThe blockchain is valid.")
            else:
                print("\nThe blockchain is NOT valid.")

        elif choice == '7':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()