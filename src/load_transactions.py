import hashlib
import json
import logging
import os

from transaction import Transaction
from hashing import hash256


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_transaction_file(file_path):
    """Load a transaction from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)


# Validate transaction filename against its SHA-256 hashed txid.
def validate_transaction_filename(transaction, filename):
    # txid is expected to be in little endian
    txid_bytes = bytes.fromhex(transaction.txid)
    # Hash the little endian bytes
    txid_hashed = hashlib.sha256(txid_bytes).hexdigest()

    # Extract the filename without extension for comparison
    filename_without_extension = os.path.splitext(filename)[0]

    if filename_without_extension != txid_hashed:
        logging.info(
            f"Invalid tx due to txid and filename mismatch: {filename}")
        return False
    return True


def process_transaction(data, filename):
    """Process a single transaction."""
    transaction = Transaction(data)
    if not transaction.is_valid():
        return None, False

    # Determine transaction ID (txid) based on whether it's a SegWit
    # transaction
    serialized_data = transaction.serialize(include_witness='witness' in data)
    txid = hash256(serialized_data)

    # Convert txid to little endian
    txid_bytes = bytes.fromhex(txid)
    txid_little_endian = txid_bytes[::-1].hex()
    transaction.txid = txid_little_endian
    return transaction, validate_transaction_filename(transaction, filename)


def load_transactions(mempool_path='mempool/'):
    valid_transactions = []
    invalid_transactions = 0

    for filename in os.listdir(mempool_path):
        if filename.endswith('.json'):
            try:
                data = load_transaction_file(
                    os.path.join(mempool_path, filename))
                transaction, is_valid = process_transaction(data, filename)
                if transaction and is_valid:
                    valid_transactions.append(transaction)
                else:
                    invalid_transactions += 1
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON from {filename}")
                invalid_transactions += 1

    logging.info(
        f"Found \033[0m\033[91m{invalid_transactions}\033[0m invalid tx.")
    logging.info(
        f"Loaded \033[0m\033[92m{len(valid_transactions)}\033[0m valid tx.")
    return valid_transactions
