
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
