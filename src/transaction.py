import hashlib

from ecdsa import VerifyingKey, SECP256k1, BadSignatureError
from ecdsa.util import sigdecode_der

from serialize import serialize_txin, serialize_txout, serialize_varint
from verify_address import get_hash_from_prevout, derive_address_from_hash

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
        self.weight = self.calculate_weight()

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
        # Verify signatures
        # if not self.verify_transaction_signatures():
        #     return False

        # Verify addresses
        if not self.verify_addresses():
            return False

        return True


    def verify_addresses(self):
        # Address verification for each input
        for vin in self.vin:
            prevout = vin['prevout']
            tx_type = prevout['scriptpubkey_type']
            # Skip checking specific tx types but continue with the loop
            if tx_type == 'v1_p2tr':
                continue
            script_or_pubkey_hash = get_hash_from_prevout(prevout, tx_type)
            address = derive_address_from_hash(script_or_pubkey_hash, tx_type)
            if address != prevout['scriptpubkey_address']:
                return False
        return True


    # Returns the concatenated witness data for the transaction.
    def get_witness_data(self):
        concatenated_witness_data = b''
        for witness in self.witnesses:
            # Convert each witness item from hex to bytes and concatenate
            for w in witness:
                concatenated_witness_data += bytes.fromhex(w)
        return concatenated_witness_data

    def calculate_weight(self, ):
        # Serialize the transaction without witness data for the base size
        serialized_without_witness = self.serialize(include_witness=False)
        # Divided by 2 because the hex string represents 2 hex digits per byte
        base_size = len(serialized_without_witness) // 2

        # Serialize the transaction with witness data for the total size
        serialized_with_witness = self.serialize(include_witness=True)
        # Similarly, divided by 2
        total_size = len(serialized_with_witness) // 2

        # Apply the weight formula
        weight = (base_size * 3) + total_size
        return weight
