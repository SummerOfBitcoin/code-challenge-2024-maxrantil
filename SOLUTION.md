# Pseudo code:

```
1. Read Transactions from mempool Folder:

For each transaction found:

	a. Validate Transaction Details: Check the integrity and adherence to protocols.

	b. Add Valid Transactions to Candidate List: If a transaction passes validation, include it in the list of transactions to be considered for the block.

2. Prioritize Transactions: Implement logic to prioritize transactions based on specific criteria.

3. Construct the Block:

	a. Create Block Header: Formulate the block header with the necessary components.

	b. Serialize Coinbase Transaction: Prepare the coinbase transaction and serialize it.

	c. Add Prioritized Transactions: Insert the transactions into the block, following the order determined by the prioritization process.

4. Output the Block: Write the constructed block to output.txt, ensuring the format aligns with the requirements provided.
```


## Coinbase tx serialization:
```
02000000 - Version
00 - Marker for SegWit
01 - Flag for SegWit
01 - Number of inputs
... - Input
02 - Number of outputs
... - Output 1
... - Output 2
01 - Number of witness elements for the first input
20 - Length of the first witness element (32 bytes)
0000000000000000000000000000000000000000000000000000000000000000 - Witness reserved value
00000000 - Locktime
```
