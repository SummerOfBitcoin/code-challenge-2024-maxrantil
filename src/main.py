import json
import os

class Transaction:
    def __init__(self, data):
        self.version = data['version']
        self.locktime = data['locktime']
        self.vin = data['vin']
        self.vout = data['vout']
        self.txid = self.calculate_txid()

    def calculate_txid(self):
        # Placeholder for TXID calculation. You might want to implement a hash of the transaction details.
        # This is a simplified example. Real Bitcoin transactions' TXID is a double SHA256 hash of the serialization of all transaction details.
        return hash(json.dumps(self.__dict__, sort_keys=True))

    def is_valid(self):
        # Basic validation: Ensure there's at least one input and one output, and check other conditions as needed.
        return len(self.vin) > 0 and len(self.vout) > 0 and self.locktime >= 0

def load_transactions(mempool_path='mempool/'):
    transactions = []
    for filename in os.listdir(mempool_path):
        if filename.endswith('.json'):
            with open(os.path.join(mempool_path, filename), 'r') as file:
                try:
                    data = json.load(file)
                    transaction = Transaction(data)
                    if transaction.is_valid():
                        transactions.append(transaction)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {filename}")
    return transactions

# Example Usage
mempool_path = 'mempool/'
transactions = load_transactions(mempool_path)
print(f"Loaded {len(transactions)} valid transactions.")
