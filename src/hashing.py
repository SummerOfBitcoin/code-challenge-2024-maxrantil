# Perform double SHA-256 hashing on the input data.
import hashlib

from transaction import logging

def double_sha256(hex_str):
    bytes_ = bytes.fromhex(hex_str)  # Convert hex string to bytes
    hash_once = hashlib.sha256(bytes_).digest()
    hash_twice = hashlib.sha256(hash_once).digest()
    return hash_twice.hex()


def calculate_merkle_root(transactions):
    # Check if the list of transactions is empty
    if not transactions:
        return None

    # Initial processing of transaction IDs: convert each to little-endian hex
    # tx_hashes = []
    # for tx in transactions:
    #     little_endian_hex = bytes.fromhex(tx)[::-1].hex()
    #     tx_hashes.append(little_endian_hex)
    tx_hashes = []
    for tx in transactions:
        if tx is None:
            logging.error("Encountered None transaction ID.")
            continue  # Skip this transaction ID
        try:
            little_endian_hex = bytes.fromhex(tx)[::-1].hex()
            tx_hashes.append(little_endian_hex)
        except ValueError as e:
            logging.error(f"Invalid transaction ID format: {tx}, Error: {e}")
            continue  # Skip invalid transaction ID


    # Iteratively calculate the Merkle root
    while len(tx_hashes) > 1:
        next_level = []
        for i in range(0, len(tx_hashes), 2):
            # Check if this is the last element without a pair
            if i + 1 == len(tx_hashes):
                # Duplicate it before hashing
                combined_hash = tx_hashes[i] + tx_hashes[i]
            else:
                # Otherwise, combine it with its pair
                combined_hash = tx_hashes[i] + tx_hashes[i + 1]

            # Hash the combined pair
            pair_hash = double_sha256(combined_hash)
            next_level.append(pair_hash)

        # Update tx_hashes with the hashes from the current level
        tx_hashes = next_level

    return bytes.fromhex(tx_hashes[0]).hex()
