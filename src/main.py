from block import mine_block
from load_transactions import load_transactions

if __name__ == "__main__":
    mempool_path = 'mempool/'
    valid_transactions = load_transactions(mempool_path)

    previous_block_hash = 'ffffffffffffffffffffffffffffffffffffffffffffffffffff00000000'
    difficulty_target = '0000ffff00000000000000000000000000000000000000000000000000000000'
    bitcoin_address = "1LuckyR1fFHEsXYyx5QK4UFzv3PEAepPMK"
    block_height = 834637
    block_subsidy = 6.25

    # Start mining with adjusted difficulty target
    output_lines = mine_block(
        valid_transactions,
        bitcoin_address,
        previous_block_hash,
        difficulty_target,
        block_height,
        block_subsidy)

    # Write the output to the file
    with open("output.txt", "w") as outfile:
        for line in output_lines:
            outfile.write(line + "\n")
