import json
import hashlib
# from cryptography.hazmat.primitives.asymmetric import ec
# from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.exceptions import InvalidSignature


class Transaction:
    def __init__(self, data, is_coinbase=False, txid=None):
        self.version = data.get('version', 1)
        self.locktime = data.get('locktime', 0)
        self.vin = data.get('vin', [])
        self.vout = data.get('vout', [])
        self.is_coinbase = is_coinbase
        self.txid = txid


    def serialize(self, include_witness=True):
        # Start with serializing the transaction version as a 4-byte little-endian integer.
        serialized = self.version.to_bytes(4, byteorder='little')

        # Check if any of the transaction inputs (vin) contain a witness field.
        segwit = any('witness' in vin for vin in self.vin) and include_witness

        if segwit:
            # If the transaction is SegWit, add the marker (0x00) and flag (0x01) bytes.
            serialized += b'\x00\x01'

        # Serialize the number of transaction inputs (vin) as a VarInt.
        serialized += serialize_varint(len(self.vin))

        # Serialize each transaction input in the vin list.
        for vin in self.vin:
            serialized += serialize_txin(vin)

        # Serialize the number of transaction outputs (vout) as a VarInt.
        serialized += serialize_varint(len(self.vout))

        # Serialize each transaction output in the vout list.
        for vout in self.vout:
            serialized += serialize_txout(vout)

        if segwit:
            # If the transaction is SegWit, serialize the witness data for each input.
            for vin in self.vin:
                if 'witness' in vin:
                    # Serialize the number of witness items for the input as a VarInt,
                    # followed by each witness item (usually a signature and a public key).
                    serialized += serialize_varint(len(vin['witness']))
                    for witness in vin['witness']:
                        witness_bytes = bytes.fromhex(witness)
                        serialized += serialize_varint(len(witness_bytes)) + witness_bytes
                else:
                    # If an input does not have witness data, add a single 0x00 byte
                    # to indicate no witness data for this input.
                    serialized += b'\x00'

        # Finally, serialize the transaction locktime as a 4-byte little-endian integer.
        serialized += self.locktime.to_bytes(4, byteorder='little')

        # Convert the entire serialized transaction to a hexadecimal string for easy transmission or storage.
        return serialized.hex()



    def is_valid(self):
        # Check there's at least one input and one output
        if len(self.vin) <= 0 or len(self.vout) <= 0:
            return False

        # Sum the values of all outputs
        total_output = sum(out["value"] for out in self.vout)

        # Sum the values of all inputs
        total_input = sum(in_["prevout"]["value"] for in_ in self.vin)

        # Ensure total input is at least as much as total output and all
        # outputs have positive values
        if total_input < total_output or any(out.get('value', 0) <= 0 for out in self.vout):
            return False

        # # Verify signatures
        # if not self.verify_signatures():
        #     return False

        return True

    # def verify_signatures(self):
    #     for in_ in self.vin:
    #         # Assuming each input has one or more witnesses, where the last two are
    #         # considered the signature and public key for simplicity
    #         # This needs to be adjusted based on your specific use case and witness structure
    #         if len(in_.get('witness', [])) >= 2:
    #             signature_hex = in_['witness'][-2]
    #             pubkey_hex = in_['witness'][-1]

    #             # Convert hex to bytes
    #             signature = bytes.fromhex(signature_hex)
    #             public_key = bytes.fromhex(pubkey_hex)

    #             # Deserialize the public key
    #             public_key_obj = serialization.load_der_public_key(public_key)

    #             # Data to be signed could vary; this is a placeholder
    #             # In real scenarios, you'd reconstruct the data being signed
    #             data = self.create_signing_data()

    #             try:
    #                 # Assuming ECDSA and SHA256; adjust according to actual requirements
    #                 public_key_obj.verify(signature, data.encode(), ec.ECDSA(hashes.SHA256()))
    #             except InvalidSignature:
    #                 return False  # Signature verification failed
    #     return True

    # def create_signing_data(self):
    #     # Simplified representation of the transaction for signing
    #     # This should be adjusted based on actual transaction signing requirements
    #     tx_parts = [
    #         str(self.version),
    #         str(self.locktime),
    #         ''.join([f"{in_['txid']}:{in_['vout']}" for in_ in self.vin]),
    #         ''.join([f"{out['value']}:{out['scriptpubkey']}" for out in self.vout])
    #     ]
    #     data_to_sign = hashlib.sha256(''.join(tx_parts).encode()).hexdigest()
    #     return data_to_sign



# Serialize an integer as a VarInt. VarInt, or Variable Integer, is a method of serializing integers using
# one or more bytes. Smaller numbers take up a smaller number of bytes.
def serialize_varint(i):
    # For integers less than 0xfd (253), serialize as a single byte.
    if i < 0xfd:
        return i.to_bytes(1, byteorder='little')
    # For integers less than or equal to 0xffff (65535), prepend with 0xfd and serialize as 2 bytes.
    elif i <= 0xffff:
        return b'\xfd' + i.to_bytes(2, byteorder='little')
    # For integers less than or equal to 0xffffffff (4294967295), prepend with 0xfe and serialize as 4 bytes.
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
    serialized += serialize_varint(len(scriptsig_bytes)) + scriptsig_bytes # ScriptSig with its length
    # Sequence, 4 bytes (little-endian)
    serialized += txin['sequence'].to_bytes(4, byteorder='little')
    return serialized


# Serialize a transaction output.
def serialize_txout(txout):
    # Amount, 8 bytes (little-endian)
    serialized = txout['value'].to_bytes(8, byteorder='little', signed=False)
    # Locking-Script Size, 1–9 bytes (VarInt)
    scriptpubkey_bytes = bytes.fromhex(txout['scriptpubkey'])
    serialized += serialize_varint(len(scriptpubkey_bytes)) + scriptpubkey_bytes
    return serialized
