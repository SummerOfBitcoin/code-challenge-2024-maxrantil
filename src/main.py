import json
import os
class Transaction:
    def __init__(self, data):
        # Initialize the transaction object with data from the JSON structure
        self.version = data.get('version', 0)
        self.locktime = data.get('locktime', 0)
        self.vin = data.get('vin', [])
        self.vout = data.get('vout', [])
        self.txid = self.calculate_txid()

    def calculate_txid(self):
        # Implementation for TXID calculation (placeholder)
        return hash(json.dumps(self.__dict__, sort_keys=True))

    def is_valid(self):
        # Check there's at least one input and one output
        if len(self.vin) <= 0 or len(self.vout) <= 0:
            return False

        # Sum the values of all outputs
        total_output = sum(out.get('value', 0) for out in self.vout)

        # Sum the values of all inputs
        total_input = sum(in_.get('prevout', {}).get('value', 0) for in_ in self.vin)

        # Ensure total input is at least as much as total output and all outputs have positive values
        if total_input < total_output or any(out.get('value', 0) <= 0 for out in self.vout):
            return False

        # Further criteria (e.g., locktime >= 0) are already handled
        return True

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
