import json
import hashlib
import logging
import os
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature

from hashing import double_sha256
from serialize import serialize_txin, serialize_txout, serialize_varint

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Transaction:
    def __init__(self, data, is_coinbase=False, txid=None):
        self.version = data.get('version', 1)
        self.locktime = data.get('locktime', 0)
        self.vin = data.get('vin', [])
        self.vout = data.get('vout', [])
        self.is_coinbase = is_coinbase
        if is_coinbase:
            self.witnesses = data.get('witness', [[]])
        else:
            # For regular transactions, derive witnesses from vin
            self.witnesses = [vin.get('witness', []) for vin in self.vin]
        self.txid = txid

    def serialize(self, include_witness=True):
        # Start with serializing the transaction version as a 4-byte
        # little-endian integer.
        serialized = self.version.to_bytes(4, byteorder='little')

        # Check if any of the transaction inputs (vin) contain a witness field.
        segwit = any('witness' in vin for vin in self.vin) and include_witness

        if segwit:
            # If the transaction is SegWit, add the marker (0x00) and flag
            # (0x01) bytes.
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
            # If the transaction is SegWit, serialize the witness data for each
            # input.
            for vin in self.vin:
                if 'witness' in vin:
                    # Serialize the number of witness items for the input as a VarInt,
                    # followed by each witness item (usually a signature and a
                    # public key).
                    serialized += serialize_varint(len(vin['witness']))
                    for witness in vin['witness']:
                        witness_bytes = bytes.fromhex(witness)
                        serialized += serialize_varint(
                            len(witness_bytes)) + witness_bytes
                else:
                    # If an input does not have witness data, add a single 0x00 byte
                    # to indicate no witness data for this input.
                    serialized += b'\x00'

        # Finally, serialize the transaction locktime as a 4-byte little-endian
        # integer.
        serialized += self.locktime.to_bytes(4, byteorder='little')

        # Convert the entire serialized transaction to a hexadecimal string for
        # easy transmission or storage.
        return serialized.hex()

    def is_valid(self):
        # Check there's at least one input and one output
        if len(self.vin) <= 0 or len(self.vout) <= 0:
            return False

        # Sum the values of all outputs
        total_output = sum(out["value"] for out in self.vout)

        # Sum the values of all inputs
        total_input = sum(in_["prevout"]["value"] for in_ in self.vin)

        # # Ensure total input is at least as much as total output and all
        # # outputs have positive values
        # if total_input < total_output or any(out.get('value', 0) <= 0 for out in self.vout):
        #     print(self.vin)
        #     return False #Check this if 0 value out is valid       ^^
        # Ensure total input is at least as much as total output
        if total_input < total_output:
            print(self.vin)
            return False

        # # Verify signatures
        if not self.verify_signatures():
            return False

        return True

    def verify_signatures(self):
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
        return True

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

    # Returns the concatenated witness data for the transaction.
    def get_witness_data(self):
        concatenated_witness_data = b''
        for witness in self.witnesses:
            # Convert each witness item from hex to bytes and concatenate
            for w in witness:
                concatenated_witness_data += bytes.fromhex(w)
        return concatenated_witness_data


def load_transactions(mempool_path='mempool/'):
    valid_transactions = []
    invalid_transactions = 0
    for filename in os.listdir(mempool_path):
        if filename.endswith('.json'):
            with open(os.path.join(mempool_path, filename), 'r') as file:
                try:
                    data = json.load(file)
                    transaction = Transaction(data)

                    # Determine if any input contains a 'witness' field,
                    # indicating a SegWit transaction
                    is_segwit = any(
                        'witness' in vin for vin in data.get(
                            'vin', []))

                    if is_segwit:
                        # SegWit transactions, use the serialization method
                        # without witness data for txid calculation.
                        serialized_data_without_witness = transaction.serialize(
                            include_witness=False)
                        txid = double_sha256(serialized_data_without_witness)
                    else:
                        # Legacy transactions
                        serialized_data = transaction.serialize()
                        txid = double_sha256(serialized_data)
                    if transaction.is_valid():
                        txid_bytes = bytes.fromhex(txid)
                        txid_little_endian = txid_bytes[::-1].hex()
                        transaction.txid = txid_little_endian
                        valid_transactions.append(transaction)
                    else:
                        invalid_transactions += 1
                except json.JSONDecodeError:
                    logging.error(f"Error decoding JSON from {filename}")
    logging.info(
        f"Found \033[0m\033[91m{invalid_transactions}\033[0m invalid tx.")
    logging.info(
        f"Loaded \033[0m\033[92m{len(valid_transactions)}\033[0m valid tx.")
    return valid_transactions
