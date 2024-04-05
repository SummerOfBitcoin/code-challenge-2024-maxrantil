import base58
import bech32
import hashlib


def calculate_checksum(version_byte, hash_bytes):
    """Calculate the checksum for a given version byte and hash bytes."""
    return hashlib.sha256(
        hashlib.sha256(
            version_byte +
            hash_bytes).digest()).digest()[
        :4]


def base58check_encode(version_byte, hash_bytes):
    """Encode version byte and hash bytes into a Base58Check format."""
    checksum = calculate_checksum(version_byte, hash_bytes)
    payload = version_byte + hash_bytes + checksum
    return base58.b58encode(payload).decode('utf-8')


def derive_address_from_hash(hash_data, tx_type):
    if not hash_data:
        return None  # Return None if hash data is not provided

    if tx_type == "p2pkh":
        version_byte = b'\x00'
        hash_bytes = bytes.fromhex(hash_data)
        return base58check_encode(version_byte, hash_bytes)
    elif tx_type == "p2sh":
        version_byte = b'\x05'
        hash_bytes = bytes.fromhex(hash_data)
        return base58check_encode(version_byte, hash_bytes)
    elif tx_type in ["v0_p2wpkh", "v0_p2wsh"]:
        hash_bytes = bytes.fromhex(hash_data)
        # Convert hash bytes to list of integers
        program = list(hash_bytes)
        # Encode to Bech32 with version byte 0
        return bech32_encode('bc', 0, program)

    else:
        return None  # Unsupported tx_type or unimplemented


def base58check_encode(version_byte, hash_bytes):
    """Encode version byte and hash bytes into a Base58Check format."""
    checksum = hashlib.sha256(
        hashlib.sha256(
            version_byte +
            hash_bytes).digest()).digest()[
        :4]
    payload = version_byte + hash_bytes + checksum
    return base58.b58encode(payload).decode('utf-8')


# Encode a Bech32 address.
def bech32_encode(hrp, version, program):
    # Prepare the data payload: version + program (5-bit representation)
    data = [version] + bech32.convertbits(program, 8, 5, pad=True)
    if data is None:
        raise ValueError("Invalid data format for Bech32 conversion.")

    # Compute the checksum and encode
    encoded = bech32.bech32_encode(hrp, data)
    if not encoded:
        raise ValueError("Bech32 encoding failed.")

    return encoded


def get_hash_from_prevout(prevout, tx_type):
    if tx_type in ["p2pkh", "p2sh"]:
        # Extract for traditional address types using the OP code method
        parts = prevout["scriptpubkey_asm"].split(" ")
        index = parts.index("OP_PUSHBYTES_20") + 1
        return parts[index] if len(parts) > index else None
    elif tx_type == "v0_p2wpkh":
        # Extract the pubkey hash for P2WPKH, which is embedded in the
        # scriptPubKey
        script = prevout["scriptpubkey"]
        # P2WPKH scriptpubkey format: "0014{20-byte pubkey hash}"
        if script.startswith("0014"):
            return script[4:]  # Extract and return the pubkey hash
    elif tx_type == "v0_p2wsh":
        # Extract the script hash for P2WSH, which is embedded in the
        # scriptPubKey
        script = prevout["scriptpubkey"]
        # P2WSH scriptpubkey format: "0020{32-byte script hash}"
        if script.startswith("0020"):
            return script[4:]  # Extract and return the script hash
    return None
