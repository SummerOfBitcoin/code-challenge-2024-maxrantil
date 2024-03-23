class Mempool:
    def __init__(self):
        self.seen_inputs = set()

    def add_transaction(self, transaction):
        if self.is_double_spending(transaction):
            print("Double spending detected")
            return False
        else:
            self.update_seen_inputs(transaction)
            return True

    def is_double_spending(self, transaction):
        for vin in transaction.vin:
            input_ref = (vin['txid'], vin['vout'])
            if input_ref in self.seen_inputs:
                return True
        return False

    def update_seen_inputs(self, transaction):
        for vin in transaction.vin:
            input_ref = (vin['txid'], vin['vout'])
            self.seen_inputs.add(input_ref)
