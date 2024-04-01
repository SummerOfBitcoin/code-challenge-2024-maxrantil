## P2PKH, Derive address from Public Key Hash:

When transactions within the Bitcoin network are reviewed, specific elements in the input (vin) section can reveal the locking script mechanism utilized to secure the funds. For P2PKH (Pay to Public Key Hash), the scriptPubKey field within the transaction's previous output (prevout) specifies the conditions under which the funds can be spent. This is illustrated in the transaction structure below, showcasing how a P2PKH locking script is encoded:

```
  "vin": [
    {
      ...
      "prevout": {
        "scriptpubkey": "76a9...ac",
        "scriptpubkey_asm": "OP_DUP OP_HASH160 OP_PUSHBYTES_20 [publicKeyHash] OP_EQUALVERIFY OP_CHECKSIG",
        "scriptpubkey_type": "p2pkh",
        "scriptpubkey_address": "[P2PKH Address]",
        "value": ...
      },
      ...
    },
```
***Steps for Deriving a P2PKH Address:**
 - 1)   *Extract Public Key Hash*: Get the hash from `scriptpubkey_asm` after `OP_PUSHBYTES_20`.
 - 2)   *Version Byte*: Add `0x00` to the start of the hash for a mainnet P2PKH address.
 - 3)   *Double SHA-256*: Hash the versioned hash twice with SHA-256.
 - 4)   *Checksum*: Use the first 4 bytes of the hash from step 3 as a checksum.
 - 5)   *Final Payload*: Combine the version byte, public key hash, and checksum.
 - 6)   *Base58Check Encode*: Encode the payload to get the Bitcoin address.

**Generating Public Key Hash from Public Key**:
If the starting point is the `public key` rather than its hash, the process to arrive at the `public key hash` involves:
 - 1) *SHA-256*: First, apply SHA-256 hashing to the public key.
 - 2) *RIPEMD-160*: Then, apply RIPEMD-160 hashing to the SHA-256 hash. This results in the public key hash.
