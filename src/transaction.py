import json
# import hashlib
# from cryptography.hazmat.primitives.asymmetric import ec
# from cryptography.hazmat.primitives import serialization, hashes
# from cryptography.exceptions import InvalidSignature


class Transaction:
    def __init__(self, data):
        self.version = data.get('version', 0)
        self.locktime = data.get('locktime', 0)
        self.vin = data.get('vin', [])
        self.vout = data.get('vout', [])
        self.txid = self.calculate_txid()

    def calculate_txid(self):
        return hash(json.dumps(self.__dict__, sort_keys=True))

    def is_valid(self):
        # Check there's at least one input and one output
        if len(self.vin) <= 0 or len(self.vout) <= 0:
            return False

        # Sum the values of all outputs
        total_output = sum(out.get('value', 0)for out in self.vout)

        # Sum the values of all inputs
        total_input = sum(in_.get('prevout', {}).get('value', 0)
                          for in_ in self.vin)

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
