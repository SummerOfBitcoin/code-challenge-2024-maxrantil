import os
import json
import hashlib
import time
import struct
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


def generate_txid(transaction_data):
    # Convert the transaction data to a string representation
    tx_string = json.dumps(transaction_data, sort_keys=True)
    # Hash the string
    tx_hash = hashlib.sha256(tx_string.encode()).hexdigest()
    return tx_hash


def double_sha256(input_value):
    return hashlib.sha256(hashlib.sha256(input_value).digest()).digest()


def calculate_merkle_root(transactions):
    if not transactions:
        return None

    tx_hashes = []
    for tx in transactions:
        # Extract txid as a string, accommodating both Transaction objects and dictionaries
        txid_str = tx.txid if isinstance(tx, Transaction) else tx['txid']
        # Ensure txid is a string, then encode, hash, and reverse for correct byte order
        tx_hash = double_sha256(str(txid_str).encode())[::-1]
        tx_hashes.append(tx_hash)

    # Iteratively reduce the list of hashes to a single hash
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 == 1:
            tx_hashes.append(tx_hashes[-1])  # Duplicate last hash if odd number of hashes
        # Hash pairs of consecutive transactions and reduce the list, reversing each hash
        tx_hashes = [double_sha256(tx_hashes[i] + tx_hashes[i+1])[::-1] for i in range(0, len(tx_hashes), 2)]

    # Return the final hash as a hex string, reversing it back to endianness
    return tx_hashes[0][::-1].hex()


def mine_block(valid_transactions, bitcoin_wallet, previous_block_hash, difficulty_target):
    # Create the coinbase transaction
    coinbase_tx = {
        "txid": "coinbase_txid_placeholder",
        "version": 1,
        "inputs": [{"prev_hash": "", "index": 0}],
        "outputs": [{"value": 50, "address": bitcoin_wallet}]
    }
    # Add coinbase transaction at the beginning
    coinbase_tx['txid'] = generate_txid(coinbase_tx)
    valid_transactions.insert(0, coinbase_tx)

    merkle_root = calculate_merkle_root(valid_transactions)
    version = 4
    timestamp = int(time.time())
    nonce = 0
    bits = 0x1d00ffff

    # Convert hex strings to binary
    prev_block_hash_bin = bytes.fromhex(previous_block_hash)
    merkle_root_bin = bytes.fromhex(merkle_root)

    # Mining process: Find a nonce that satisfies the difficulty target
    while True:
        header = struct.pack("<L32s32sLLL", version, prev_block_hash_bin, merkle_root_bin, timestamp, bits, nonce)
        header_hash = hashlib.sha256(hashlib.sha256(header).digest()).digest()

        # Reverse the hash to match endianess
        reversed_hash = header_hash[::-1]

        if int(reversed_hash.hex(), 16) < int(difficulty_target, 16):
            print(f"Block mined! Nonce: {nonce}, Hash: {reversed_hash.hex()}")
            break
        nonce += 1

    # Prepare the output with the block header and transaction IDs
    output_lines = []
    # Add the block header line
    output_lines.append(header.hex())
    # Add the serialized coinbase transaction line
    output_lines.append(json.dumps(coinbase_tx))
    # start from index 1 for the rest of the transactions
    for tx in valid_transactions[1:]:
        # Check if tx is an instance of Transaction or a dictionary and get the txid accordingly
        txid_str = tx.txid if isinstance(tx, Transaction) else tx['txid']
        output_lines.append(str(txid_str))  # Ensure txid is treated as a string

    # Write the output to the file
    with open("output.txt", "w") as outfile:
        for line in output_lines:
            outfile.write(line + "\n")
