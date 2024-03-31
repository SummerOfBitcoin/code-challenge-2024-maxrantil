import struct


# Serialize an integer as a VarInt. VarInt, or Variable Integer, is a method of serializing integers using
# one or more bytes. Smaller numbers take up a smaller number of bytes.
def serialize_varint(i):
    # For integers less than 0xfd (253), serialize as a single byte.
    if i < 0xfd:
        return i.to_bytes(1, byteorder='little')
    # For integers less than or equal to 0xffff (65535), prepend with 0xfd and
    # serialize as 2 bytes.
    elif i <= 0xffff:
        return b'\xfd' + i.to_bytes(2, byteorder='little')
    # For integers less than or equal to 0xffffffff (4294967295), prepend with
    # 0xfe and serialize as 4 bytes.
    elif i <= 0xffffffff:
        return b'\xfe' + i.to_bytes(4, byteorder='little')
    # For larger integers, prepend with 0xff and serialize as 8 bytes.
    else:
        return b'\xff' + i.to_bytes(8, byteorder='little')


# Serialize a transaction input.
def serialize_txin(txin):
    # Previous Transaction Hash, 32 bytes (little-endian)
    serialized = bytes.fromhex(txin['txid'])[::-1]  # Reverse byte order
    # Previous Transaction Output Index, 4 bytes (little-endian)
    serialized += txin['vout'].to_bytes(4, byteorder='little', signed=False)
    # ScriptSig Size, 1–9 bytes (VarInt)
    scriptsig_bytes = bytes.fromhex(txin.get('scriptsig', ''))
    # ScriptSig with its length
    serialized += serialize_varint(len(scriptsig_bytes)) + scriptsig_bytes
    # Sequence, 4 bytes (little-endian)
    serialized += txin['sequence'].to_bytes(4, byteorder='little')
    return serialized


# Serialize a transaction output.
def serialize_txout(txout):
    # Amount, 8 bytes (little-endian)
    serialized = txout['value'].to_bytes(8, byteorder='little', signed=False)
    # Locking-Script Size, 1–9 bytes (VarInt)
    scriptpubkey_bytes = bytes.fromhex(txout['scriptpubkey'])
    serialized += serialize_varint(len(scriptpubkey_bytes)
                                   ) + scriptpubkey_bytes
    return serialized


# Serialize a coinbase transaction.
def serialize_coinbase_tx(coinbase_tx, block_height):
    # Serialize the transaction version as a 4-byte little-endian unsigned
    # integer.
    version = struct.pack("<L", coinbase_tx.version)
    # SegWit marker and flag
    marker = b"\x00"
    flag = b"\x01"
    # There is always exactly one input in a coinbase transaction, represented
    # here as a single byte.
    tx_in_count = struct.pack("<B", 1)
    # Serialize the number of outputs in the coinbase transaction as a single
    # byte.
    tx_out_count = struct.pack("<B", len(coinbase_tx.vout))
    txins = b""
    txouts = b""

    # Serialize the coinbase input:
    # The prev_tx_hash for a coinbase transaction input is always 32 bytes of
    # zeros, indicating no previous transaction.
    prev_tx_hash = bytes.fromhex("00" * 32)
    # The out_index is set to 0xFFFFFFFF (all bits are ones) to indicate that
    # this is a coinbase transaction.
    out_index = struct.pack("<L", 0xFFFFFFFF)
    # Encode block height in little-endian format, prefixed by its length byte.
    height_script = (block_height).to_bytes(
        (block_height.bit_length() + 7) // 8, 'little', signed=False)
    # The script bytes typically include the block height followed by an
    # arbitrary "extra nonce" data.
    # The leading "\x03" indicates the operation to push the next bytes to the
    # stack.
    script_bytes = b"\x03" + height_script + b"ExtraNonce"
    script_len = struct.pack("<B", len(script_bytes))
    # Combine all parts of the coinbase input.
    txins = prev_tx_hash + out_index + script_len + \
        script_bytes + struct.pack("<L", 0xFFFFFFFF)

    # Serialize the outputs:
    for out in coinbase_tx.vout:
        # Serialize the output value as an 8-byte little-endian unsigned
        # integer.
        value = struct.pack("<Q", out["value"])
        # Assuming P2PKH scriptPubKey format, serialize the scriptPubKey.
        scriptPubKey_bytes = bytes.fromhex(out["scriptpubkey"])
        script_len = struct.pack("<B", len(scriptPubKey_bytes))
        # Combine the serialized value and scriptPubKey for each output.
        txouts += value + script_len + scriptPubKey_bytes

    # Witness is the commitment and encoded in hex
    witness_count = struct.pack("<B", len(coinbase_tx.witnesses[0]))
    witness_reserved_value = bytes.fromhex(coinbase_tx.witnesses[0][0])
    witness_len = struct.pack("<B", len(witness_reserved_value))
    witness_data = witness_count + witness_len + witness_reserved_value

    # Serialize the locktime as a 4-byte little-endian unsigned integer.
    locktime = struct.pack("<L", coinbase_tx.locktime)
    # Combine all serialized parts of the coinbase transaction.
    return (
        version +
        marker +
        flag +
        tx_in_count +
        txins +
        tx_out_count +
        txouts +
        witness_data +
        locktime).hex()


# Serialize the block height as per BIP34 for inclusion in a coinbase
# transaction's scriptSig.
def serialize_block_height(block_height):
    # Convert the integer block height to a byte array in little-endian format
    height_bytes = block_height.to_bytes(
        (block_height.bit_length() + 7) // 8, 'little')

    # The length of the height_bytes determines how it will be pushed onto the stack.
    # For block heights, this will usually be a small number, so we can directly use the byte count as the opcode.
    # This simplification assumes all block heights result in a push data size
    # <= 75 bytes.
    push_opcode = len(height_bytes).to_bytes(1, 'little')

    return push_opcode + height_bytes
