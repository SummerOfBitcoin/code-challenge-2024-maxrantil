import hashlib
import time
import struct

from transaction import Transaction
from coinbase import create_coinbase_transaction
from hashing import double_sha256, calculate_merkle_root
from serialize import serialize_coinbase_tx


def difficulty_target_to_bits(difficulty_target):
    # Convert the difficulty target from hex to a big-endian integer
    target_int = int(difficulty_target, 16)

    # Ensure the target is in the correct format (non-zero and not just
    # leading zeros)
    if target_int == 0:
        return '00000000'

    # Normalize the target to find the coefficient and exponent
    # The coefficient is the first three bytes of the significant part of the target,
    # adjusted to fit into three bytes if necessary.
    size = (target_int.bit_length() + 7) // 8  # Size in bytes
    if size <= 3:
        coefficient = target_int << (8 * (3 - size))
    else:
        coefficient = target_int >> (8 * (size - 3))

    # The exponent is the size of the original target in bytes.
    # If the significant byte is greater than 0x7f (127), we need to adjust
    # both the coefficient and the exponent to not confuse it with a negative
    # number.
    if coefficient & 0x00800000:
        coefficient >>= 8
        size += 1

    # The 'bits' compact format combines the size (exponent) and the adjusted
    # coefficient.
    bits = (size << 24) | coefficient

    return bits


def mine_block(
        valid_transactions,
        bitcoin_address,
        previous_block_hash,
        difficulty_target,
        block_height):
    # Create the coinbase transaction as a Transaction instance
    coinbase_tx = create_coinbase_transaction(bitcoin_address, 50)

    # Serialize the coinbase transaction
    coinbase_serialized = serialize_coinbase_tx(coinbase_tx, block_height)

    # Calculate the TXID for the coinbase transaction from its serialized form
    coinbase_tx.txid = coinbase_serialized

    # Insert the coinbase transaction at the beginning of the list
    valid_transactions.insert(0, coinbase_tx)

    # Insert the hashed coinbase transaction at the beginning of the list of
    # valid transactions
    coinbase_hash = double_sha256(coinbase_serialized)
    valid_transactions.insert(1, coinbase_hash)

    # Generate txids list including the actual TXID of the coinbase_tx
    txids = [
        tx.txid if isinstance(
            tx,
            Transaction) else tx for tx in valid_transactions]

    # Calculate the Merkle root of the txids list
    merkle_root = calculate_merkle_root(txids)

    version = 4  # Block Version 4 became active in December 2015
    timestamp = int(time.time())
    nonce = 0
    bits = difficulty_target_to_bits(difficulty_target)

    # Convert hex strings to binary for header components
    prev_block_hash_bin = bytes.fromhex(previous_block_hash)
    merkle_root_bin = bytes.fromhex(merkle_root)

    # Mining process: find a nonce that satisfies the difficulty target
    while True:
        header = struct.pack(
            "<L32s32sLLL",
            version,
            prev_block_hash_bin,
            merkle_root_bin,
            timestamp,
            bits,
            nonce)
        header_hash = hashlib.sha256(hashlib.sha256(header).digest()).digest()

        reversed_hash = header_hash[::-1]

        if int(reversed_hash.hex(), 16) < int(difficulty_target, 16):
            print(f"Block mined! Nonce: {nonce}, Hash: {reversed_hash.hex()}")
            break
        nonce += 1

    # Prepare the output
    output_lines = [header.hex()]

    # Append the txid of the coinbase transaction and other transactions
    for tx in valid_transactions:
        if isinstance(tx, Transaction):
            output_lines.append(tx.txid)
        else:
            # If it's a string (hash), append it directly
            output_lines.append(tx)

    return output_lines
