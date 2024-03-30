import base58

from transaction import Transaction


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


# Create a coinbase transaction that can be included in the block.
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
            # The total amount includes block reward and transaction fees.
            "value": total_value,
            "scriptpubkey": script_pub_key,
        }]
    }

    return Transaction(coinbase_tx_data, is_coinbase=True)
