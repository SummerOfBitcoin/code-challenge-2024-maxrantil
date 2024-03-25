import base58
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
                    # Use filename (without .json) as txid
                    txid_from_filename = filename[:-5]
                    transaction = Transaction(data, txid=txid_from_filename)
                    serialized_data = transaction.serialize()
                    # print(f"Serialized data for transaction {txid_from_filename}: {serialized_data}")
                    calculated_txid = double_sha256(serialized_data)
                    if calculated_txid == txid_from_filename:
                        print(f"Transaction {txid_from_filename} is valid.")
                    # else:
                        # print(f"Transaction {txid_from_filename} is invalid.")
                    if transaction.is_valid():
                        valid_transactions.append(transaction)
                    else:
                        invalid_transactions += 1
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {filename}")
    print(f"Found \033[0m\033[91m{invalid_transactions}\033[0m invalid tx.")
    return valid_transactions


#Perform double SHA-256 hashing on the input data.
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
    tx_hashes = []
    for tx in transactions:
        little_endian_hex = bytes.fromhex(tx)[::-1].hex()
        tx_hashes.append(little_endian_hex)

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


# Converts a Bitcoin address to a scriptPubKey.
def bitcoin_address_to_script_pub_key(bitcoin_address):
    # Decode the address using Base58Check to get the payload
    decoded = base58.b58decode_check(bitcoin_address)
    # For P2PKH, prefix with OP_DUP, OP_HASH160, push operation, and postfix with OP_EQUALVERIFY, OP_CHECKSIG
    script_pub_key = b'\x76\xa9' + bytes([len(decoded[1:])]) + decoded[1:] + b'\x88\xac'
    return script_pub_key.hex()


# Create a coinbase transaction that can be included in a block.
def create_coinbase_transaction(bitcoin_address, value=50, tx_fees=0):
    total_value = value + tx_fees
    if total_value < 0:
        raise ValueError("Total value (reward + fees) must be non-negative")

    # Convert bitcoin wallet address to scriptPubKey
    script_pub_key = bitcoin_address_to_script_pub_key(bitcoin_address)

    coinbase_tx_data = {
        "version": 1,
        "locktime": 0,
        "vin": [{
            "txid": "",
            "vout": 0,
            "scriptsig": "",
            "sequence": 0xffffffff,
        }],
        "vout": [{
            "value": total_value,  # The total amount includes block reward and transaction fees.
            "scriptpubkey": script_pub_key,
        }]
    }

    # Assuming a Transaction class exists to handle such data structures
    return Transaction(coinbase_tx_data, is_coinbase=True)


# Serialize a coinbase transaction.
def serialize_coinbase_tx(coinbase_tx, block_height):
    # Serialize the transaction version as a 4-byte little-endian unsigned integer.
    version = struct.pack("<L", coinbase_tx.version)
    # There is always exactly one input in a coinbase transaction, represented here as a single byte.
    tx_in_count = struct.pack("<B", 1)
    # Serialize the number of outputs in the coinbase transaction as a single byte.
    tx_out_count = struct.pack("<B", len(coinbase_tx.vout))
    txins = b""
    txouts = b""

    # Serialize the coinbase input:
    # The prev_tx_hash for a coinbase transaction input is always 32 bytes of zeros, indicating no previous transaction.
    prev_tx_hash = bytes.fromhex("00" * 32)
    # The out_index is set to 0xFFFFFFFF (all bits are ones) to indicate that this is a coinbase transaction.
    out_index = struct.pack("<L", 0xFFFFFFFF)
    # Encode block height in little-endian format, prefixed by its length byte.
    height_script = (block_height).to_bytes((block_height.bit_length() + 7) // 8, 'little', signed=False)
    # The script bytes typically include the block height followed by an arbitrary "extra nonce" data.
    script_bytes = b"\x03" + height_script + b"ExtraNonce"  # The leading "\x03" indicates the operation to push the next bytes to the stack.
    script_len = struct.pack("<B", len(script_bytes))
    # Combine all parts of the coinbase input.
    txins = prev_tx_hash + out_index + script_len + script_bytes + struct.pack("<L", 0xFFFFFFFF)

    # Serialize the outputs:
    for out in coinbase_tx.vout:
        # Serialize the output value as an 8-byte little-endian unsigned integer.
        value = struct.pack("<Q", out["value"])
        # Assuming P2PKH scriptPubKey format, serialize the scriptPubKey.
        scriptPubKey_bytes = bytes.fromhex(out["scriptpubkey"])
        script_len = struct.pack("<B", len(scriptPubKey_bytes))
        # Combine the serialized value and scriptPubKey for each output.
        txouts += value + script_len + scriptPubKey_bytes

    # Serialize the locktime as a 4-byte little-endian unsigned integer.
    locktime = struct.pack("<L", coinbase_tx.locktime)
    # Combine all serialized parts of the coinbase transaction.
    return (version + tx_in_count + txins + tx_out_count + txouts + locktime).hex()


def difficulty_target_to_bits(difficulty_target):
    # Convert the difficulty target from hex to a big-endian integer
    target_int = int(difficulty_target, 16)

    # Ensure the target is in the correct format (non-zero and not just leading zeros)
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
    # both the coefficient and the exponent to not confuse it with a negative number.
    if coefficient & 0x00800000:
        coefficient >>= 8
        size += 1

    # The 'bits' compact format combines the size (exponent) and the adjusted coefficient.
    bits = (size << 24) | coefficient

    return bits


def mine_block(valid_transactions, bitcoin_address, previous_block_hash, difficulty_target, block_height):
    # Create the coinbase transaction as a Transaction instance
    coinbase_tx = create_coinbase_transaction(bitcoin_address, 50)

    # Serialize the coinbase transaction
    coinbase_serialized = serialize_coinbase_tx(coinbase_tx, block_height)

    # Calculate the TXID for the coinbase transaction from its serialized form
    coinbase_tx.txid = coinbase_serialized

    # Insert the coinbase transaction at the beginning of the list of valid transactions
    valid_transactions.insert(0, coinbase_tx)

    # Generate txids list including the actual TXID of the coinbase_tx
    txids = [tx.txid for tx in valid_transactions]

    # Calculate the Merkle root of the txids list
    merkle_root = calculate_merkle_root(txids)

    version = 4 # Block Version 4 became active in December 2015
    timestamp = int(time.time())
    nonce = 0
    bits = difficulty_target_to_bits(difficulty_target)

    # Convert hex strings to binary for header components
    prev_block_hash_bin = bytes.fromhex(previous_block_hash)
    merkle_root_bin = bytes.fromhex(merkle_root)

    # Mining process: find a nonce that satisfies the difficulty target
    while True:
        header = struct.pack("<L32s32sLLL", version, prev_block_hash_bin, merkle_root_bin, timestamp, bits, nonce)
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
        output_lines.append(tx.txid)

    return output_lines
