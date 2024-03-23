import os
import json
import hashlib
import time
from transaction import Transaction


def load_transactions(mempool_path='mempool/'):
    valid_transactions = []
    invalid_transactions = 0
    for filename in os.listdir(mempool_path):
        if filename.endswith('.json'):
            with open(os.path.join(mempool_path, filename), 'r') as file:
                try:
                    data = json.load(file)
                    transaction = Transaction(data)
                    if transaction.is_valid():
                        valid_transactions.append(transaction)
                    else:
                        invalid_transactions += 1
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {filename}")
    print(f"Found \033[0m\033[91m{invalid_transactions}\033[0m invalid tx.")
    return valid_transactions


def mine_block(valid_transactions, bitcoin_wallet, previous_block_hash, difficulty_target):
    # Create the coinbase transaction
    coinbase_tx = {
        "txid": "coinbase_txid_placeholder",
        "version": 1,
        "inputs": [{"prev_hash": "", "index": 0}],
        "outputs": [{"value": 50, "address": bitcoin_wallet}]
    }
    # Add coinbase transaction at the beginning
    valid_transactions.insert(0, coinbase_tx)

    # Placeholder for merkle root calculation
    merkle_root = "merkle_root_placeholder"
    timestamp = int(time.time())
    nonce = 0

    # Adjusting the mining loop to check against the difficulty target
    while True:
        block_header = f"{previous_block_hash}{merkle_root}{timestamp}{nonce}"
        block_hash = hashlib.sha256(block_header.encode()).hexdigest()

        if int(block_hash, 16) < int(difficulty_target, 16):
            print(f"Block mined! Nonce: {nonce}, Hash: {block_hash}")
            break
        nonce += 1

    transactions_txids = [
        tx.txid if isinstance(tx, Transaction) else tx['txid']
        for tx in valid_transactions
    ]
    block = {
        "version": 1,
        "previous_hash": previous_block_hash,
        "merkle_root": merkle_root,
        "timestamp": timestamp,
        "difficulty": difficulty_target,
        "nonce": nonce,
        "transactions": transactions_txids
    }

    # Write the mined block data to output.txt
    with open("output.txt", "w") as outfile:
        json.dump(block, outfile, indent=4)
