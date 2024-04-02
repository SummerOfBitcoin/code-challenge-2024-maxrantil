import base58
import hashlib

from transaction import Transaction
from hashing import double_sha256, calculate_merkle_root
from serialize import serialize_block_height


# WARNING CAN I USE THE DECODER??
# Converts a Bitcoin address to a scriptPubKey.
def bitcoin_address_to_script_pub_key(bitcoin_address):
    # Decode the address using Base58Check to get the payload
    decoded = base58.b58decode_check(bitcoin_address)
    # For P2PKH, prefix with OP_DUP, OP_HASH160, push operation, and postfix
    # with OP_EQUALVERIFY, OP_CHECKSIG
    script_pub_key = b'\x76\xa9' + \
        bytes([len(decoded[1:])]) + decoded[1:] + b'\x88\xac'
    return script_pub_key.hex()

def reverse_hex_string(hex_str):
    # Convert hex string to bytes
    byte_seq = bytes.fromhex(hex_str)

    # Reverse the byte sequence
    reversed_byte_seq = byte_seq[::-1]

    # Convert back to hex string
    reversed_hex_str = reversed_byte_seq.hex()

    return reversed_hex_str

def calculate_witness_commitment(transactions, witness_reserved_value):
    # Reverse the hex string of the double SHA-256 hash of each transaction's Witness Transaction ID (wtxid)
    all_tx_wtxids = [reverse_hex_string(double_sha256(tx.get_wtxid())) for tx in transactions]

    # Insert the witness reserved value at the beginning of the list of all transaction wtxids.
    # This is presumably to include a specific reserved value in the calculation of the Merkle root,
    # which is a requirement for witness commitments in SegWit.
    all_tx_wtxids.insert(0, witness_reserved_value)

    # Calculate the Merkle root of all transaction wtxids
    merkle_root_of_wtxids = calculate_merkle_root(all_tx_wtxids)

    # Concatenate the calculated Merkle root with the witness reserved value to form a combined string.
    combined = merkle_root_of_wtxids + witness_reserved_value

    # Calculate the double SHA-256 hash of the combined Merkle root and witness reserved value.
    # This final hash is the witness commitment, which is included in a SegWit coinbase transaction.
    witness_commitment = double_sha256(combined)

    return witness_commitment



def create_coinbase_transaction(
    bitcoin_address,
    block_subsidy,
    block_height,
    valid_transactions,
    tx_fees=0,
):
    # Convert block subsidy from bitcoins to satoshis
    block_subsidy_sats = int(block_subsidy * 100000000)
    total_value = block_subsidy_sats + tx_fees

    script_pub_key = bitcoin_address_to_script_pub_key(bitcoin_address)

    # Reserved value for future Bitcoin updates
    witness_reserved_value = "0000000000000000000000000000000000000000000000000000000000000000"
    # The witness commitment is calculated from all transactions in the block
    witness_commitment = calculate_witness_commitment(valid_transactions, witness_reserved_value)

    # Coinbase transaction must include the block height as per BIP34, and
    # optionally extra nonce data,
    coinbase_data = serialize_block_height(block_height)

    # Start with OP_RETURN (6a), followed by the push data opcode (24),
    # the tag indicating a SegWit commitment (aa21a9ed), and the witness
    # commitment hash
    witness_commitment_script = "6a24aa21a9ed" + witness_commitment

    coinbase_tx_data = {
        "version": 2,
        "locktime": 0,
        "vin": [{
            "txid": "0000000000000000000000000000000000000000000000000000000000000000",
            "vout": 0xffffffff,
            "scriptsig": coinbase_data.hex(),
            "sequence": 0xffffffff
        }],
        "vout": [
            {
                "value": total_value,
                "scriptpubkey": script_pub_key,
            },
            {
                "value": 0,  # No value is transferred with the witness commitment output
                "scriptpubkey": witness_commitment_script,
            }
        ],
        "witness": [[witness_reserved_value]]
    }

    print("Witness commitment in coinbase tx:", witness_commitment_script)
    return Transaction(coinbase_tx_data, is_coinbase=True)
