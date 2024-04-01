## P2SH, Derive Address from Script Hash:

Similar to P2PKH, P2SH (Pay to Script Hash) allows funds to be sent to a script's hash. Instead of locking funds to a public key, P2SH locks them to a hash of a script defining spending conditions. This enables complex transactions like multisig. P2SH addresses start with a '3' on the Bitcoin mainnet.

```
  "vin": [
    {
      ...
      "prevout": {
        "scriptpubkey": "a914...87",
        "scriptpubkey_asm": "OP_HASH160 OP_PUSHBYTES_20 [scriptHash] OP_EQUAL",
        "scriptpubkey_type": "p2sh",
        "scriptpubkey_address": "[P2SH Address]",
        "value": ...
      },
      ...
    },
```

 - 1)   *Extract Script Hash*: Get the hash from `scriptpubkey_asm` after `OP_PUSHBYTES_20`.
 - 2)   *Version Byte*: Add `0x05` to the start of the hash for a mainnet P2SH address.
 - 3)   *Double SHA-256*: Hash the versioned hash twice with SHA-256.
 - 4)   *Checksum*: Use the first 4 bytes of the hash from step 3 as a checksum.
 - 5)   *Final Payload*: Combine the version byte, script hash, and checksum.
 - 6)   *Base58Check Encode*: Encode the payload to get the Bitcoin address.

**Creating a Script Hash**:
If you have a redeem script and need to convert it to a script hash for a P2SH address, follow these steps:
 - 1) *SHA-256*: Hash the redeem script with SHA-256.
 - 2) *RIPEMD-160*: Apply RIPEMD-160 hashing to the result of the SHA-256 hash. This is your script hash.
