from utils import load_transactions, mine_block

if __name__ == "__main__":
    mempool_path = 'mempool/'
    valid_transactions = load_transactions(mempool_path)
    print(f"Loaded \033[0m\033[92m{len(valid_transactions)}\033[0m valid tx.")

    previous_block_hash = '0000000000000000'  # Simplified previous block hash
    difficulty_target = '0000ffff00000000000000000000000000000000000000000000000000000000'
    # Placeholder for the Bitcoin wallet address
    bitcoin_wallet_address = "bitcoin_wallet_address"

    # Start mining with adjusted difficulty target
    mine_block(valid_transactions, bitcoin_wallet_address,
               previous_block_hash, difficulty_target)
