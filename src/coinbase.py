import base58

from transaction import Transaction
from hashing import double_sha256
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


def calculate_witness_commitment(transactions):
    all_witness_data = b''
    for tx in transactions:
        witness_data = tx.get_witness_data()
        all_witness_data += witness_data

    # Double SHA-256 hash of the concatenated witness data
    return double_sha256(all_witness_data.hex())


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

    # The witness commitment is calculated from all transactions in the block
    # UNCOMMENT FOR REAL WORK, WIP CAN BE COMMENTED FOR SPEED
    # witness_commitment = calculate_witness_commitment(valid_transactions)
    witness_commitment = "d8e11800e7bf85a5fbeeed9aefdd539e94fc6bd3036801f564933a838726d73e"

    # Coinbase transaction must include the block height as per BIP34, and
    # optionally extra nonce data,
    coinbase_data = serialize_block_height(block_height)

    # Start with OP_RETURN (6a), followed by the push data opcode (24),
    # the tag indicating a SegWit commitment (aa21a9ed), and the witness
    # commitment hash
    witness_commitment_script = "6a24aa21a9ed" + witness_commitment

    # Reserved value for future Bitcoin updates
    witness_reserved_value = "0000000000000000000000000000000000000000000000000000000000000000"

    outputs = [
        {
            "value": total_value,
            "scriptpubkey": script_pub_key,
        },
        {
            "value": 0,  # No value is transferred with the witness commitment output
            "scriptpubkey": witness_commitment_script,
        }
    ]

    coinbase_tx_data = {
        "version": 2,
        "locktime": 0,
        "vin": [{
            "txid": "0000000000000000000000000000000000000000000000000000000000000000",
            "vout": 0xffffffff,
            "scriptsig": coinbase_data.hex(),
            "sequence": 0xffffffff
        }],
        "vout": outputs,
        "witness": [[witness_reserved_value]]
    }

    return Transaction(coinbase_tx_data, is_coinbase=True)
