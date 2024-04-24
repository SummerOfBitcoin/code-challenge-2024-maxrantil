### Design Approach

#### Initial Setup and MVP Development
The initial setup of my project was guided by the evaluation criteria and test configurations provided by the challenge's grader. My objective was to first create a minimum viable product (MVP) that addressed the fundamental requirements of the challenge. This strategic approach allowed me to systematically structure the project in alignment with the grading rubric, ensuring each component would meet the expected standards upon full implementation.

#### Structuring Based on Evaluation Criteria
1. **Skeleton Application**:
   - I developed a basic application structure that could potentially handle tasks like reading, validating, and processing transactions, as well as constructing and validating blocks. The skeleton was designed to be easily expandable to full functionality in later stages of development.

2. **Guided Development Process**:
   - Each step in the development was directly influenced by the specific requirements and tests outlined by the grader. This included setting up a framework for:
     - **Transaction Reading**: Placeholder functions were created to simulate the reading of transaction data from files.
     - **Transaction Validation**: I outlined potential validation checks that would be necessary, such as format and rule adherence.
     - **Block Construction and Validation**: I drafted the initial logic for constructing a block and validating its components, focusing primarily on the structural requirements such as the block header and the inclusion of a valid coinbase transaction.

3. **Alignment with Test Criteria**:
   - The entire project structure was developed with a clear focus on passing the predefined tests provided in the challenge. This method ensured that each part of the application, once fully implemented, would conform to the required specifications and behave as expected during evaluation.

### Implementation Details

#### Pseudo code:

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

### Results and Performance

#### Efficiency and Decision-Making

This project was designed as a simplified exercise with a static mempool, negating the need for dynamic mempool monitoring and complex optimizations typically required for real-time transaction updates. This static nature allowed us to focus on core functionalities without the overhead of continuous mempool checking.

#### Algorithm Selection

In the development phase, I experimented with advanced algorithms aimed at maximizing fee output by exploring all possible combinations of transactions to optimally fill the block. This approach, while theoretically beneficial for maximizing block rewards, proved to be computationally intensive. The exhaustive computation did not yield a significant improvement in performance compared to the complexity it introduced.

Given these findings, I opted for a simpler, more straightforward method:

    Transaction Prioritization: Transactions were selected based on their fee rate, starting with the most profitable ones. This method facilitated a faster block construction process and ensured a good balance between computational efficiency and block reward optimization.

#### Performance Summary

The simpler transaction selection algorithm proved adequate for the scope of this project, highlighting a key insight: more complex algorithms do not always equate to better performance, especially in controlled or simplified scenarios.

### Conclusion

By using the evaluation criteria and test setups as the primary guide for developing the project structure, I efficiently laid out a foundational framework. This approach allowed me to quickly establish a minimum viable product (MVP) that not only meets the initial expectations set by the grader but is also poised for expansion into a more functional mining simulator. After achieving a passing grade with the MVP, I realized that an explicit step for validating transaction integrity was not necessary, as all transactions provided were valid. However, to ensure robustness and to align more closely with real-world operations, I implemented a check for validating addresses derived from transaction outputs.

This involved parsing input scripts to verify whether they adhered to the P2PKH or P2SH standards. I used detailed cryptographic processes to extract and validate public key hashes and script hashes from transaction inputs, ensuring they correctly formed Bitcoin addresses. This not only reinforced the validity of transactions but also deepened the simulation's alignment with Bitcoin's security protocols, providing an additional layer of authenticity to the project.

For more detailed information on address derivation, refer to the documentation on [P2PKH](https://github.com/SummerOfBitcoin/code-challenge-2024-maxrantil/blob/main/docs/P2PKH_Derive_Address_from_Public_Key_Hash.md) and [P2SH](https://github.com/SummerOfBitcoin/code-challenge-2024-maxrantil/blob/main/docs/P2SH_Derive_Address_from_Script_Hash.md).

I started to implement a validation for the signatures but didn't finish that work because when realizing that time is of the essence, I decided that it was more important to spend it on the proposal.
I can always get back and learn about it after the proposal is finished or after the deadline.

### References

#### Bitcoin Transaction Details
- [What exactly is the vout field?](https://bitcoin.stackexchange.com/questions/100997/what-exactly-is-the-vout-field)
- [How is the size of a Bitcoin transaction calculated?](https://bitcoin.stackexchange.com/questions/92689/how-is-the-size-of-a-bitcoin-transaction-calculated)
- [Transaction Details - Bitcoin Wiki](https://en.bitcoin.it/wiki/Transaction)
- [Technical Transaction Explanation](https://learnmeabitcoin.com/technical/transaction)
- [Witness in Transactions](https://learnmeabitcoin.com/technical/transaction/witness/)
- [Calculating Witness Commitment Hash](https://bitcoin.stackexchange.com/questions/79747/how-do-i-calculate-the-witness-commitment-hash-for-a-given-block)

#### Bitcoin Block Details
- [Understanding the Bitcoin Blockchain Header](https://medium.com/fcats-blockchain-incubator/understanding-the-bitcoin-blockchain-header-a2b0db06b515)
- [Bitcoin Block Details](https://learnmeabitcoin.com/technical/block/)
- [Bitcoin Blockchain Reference](https://developer.bitcoin.org/reference/block_chain.html)
- [Bitcoin Block Construction](https://learn.saylor.org/mod/book/view.php?id=36340&chapterid=18913)

#### Bitcoin Address and Signing
- [Deriving Bech32 Address from P2WPKH Output Script](https://bitcoin.stackexchange.com/questions/79527/how-do-i-derive-bech32-address-from-p2wpkh-output-script)
- [Bitcoin Signatures and Keys](https://learnmeabitcoin.com/technical/keys/signature/)

#### Additional Bitcoin Resources
- [Mastering Bitcoin - Signatures](https://github.com/bitcoinbook/bitcoinbook/blob/develop/ch08_signatures.adoc)
- [Grokking Bitcoin](https://rosenbaum.se/book/grokking-bitcoin-10.html)
