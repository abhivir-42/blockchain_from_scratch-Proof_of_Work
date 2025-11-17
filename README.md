# Tutorial 1: Blockchain Client

A simplified blockchain implementation for educational purposes.

## Project Structure

```
Tutorial_1/
├── blockchain_client/          # Main package
│   ├── __init__.py            # Package initialization
│   ├── serialization.py       # Block/transaction hashing
│   ├── merkle.py              # Merkle tree construction
│   ├── block.py               # Block creation and mining
│   ├── blockchain.py          # Blockchain state management
│   ├── proof.py               # Inclusion proof generation/verification
│   └── cli.py                 # Command-line interface
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── blockchain.json.gz          # Initial blockchain state
├── mempool.json.gz            # Pending transactions
└── keys.json.gz               # Account keys
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make main.py executable (optional):
```bash
chmod +x main.py
```

## Usage

### Test Serialization

Test that serialization works correctly:
```bash
python -m blockchain_client.serialization
```

Expected output: `✓ Serialization test passed: 0x073c348de2486c616699fcd8267dc895f2d8b43355b126295da92df2961f8a87`

### Test Merkle Tree

Test Merkle tree construction:
```bash
python -m blockchain_client.merkle
```

### Produce Blocks

Mine new blocks from the mempool:
```bash
python main.py --blockchain-state blockchain.json.gz \
    produce-blocks \
    --mempool mempool.json.gz \
    --blockchain-output new-blockchain.json.gz \
    --mempool-output new-mempool.json.gz \
    -n 15
```

### Get Transaction Hash

Get the hash of a specific transaction:
```bash
python main.py --blockchain-state blockchain.json.gz \
    get-tx-hash 18 7
```

### Generate Inclusion Proof

Generate a Merkle inclusion proof:
```bash
python main.py --blockchain-state blockchain.json.gz \
    generate-proof 18 0x<tx_hash> \
    -o proof.json
```

### Verify Inclusion Proof

Verify a Merkle inclusion proof:
```bash
python main.py --blockchain-state blockchain.json.gz \
    verify-proof proof.json
```

## Implementation Notes

### Serialization Format

Both blocks and transactions use the same format:
1. Sort fields alphabetically by key
2. Create comma-separated string (no spaces)
   - Numbers: decimal without leading zeros
   - Hex strings: keep `0x` prefix
3. SHA-256 hash the result

### Merkle Tree

- Hash function: `H(a,b) = SHA256(a+b) if a<b else SHA256(b+a)`
- Odd nodes: append null hash (`0x` + 64 zeros)
- Leaves are transaction hashes

### Mining

- Difficulty = minimum leading zeros in block hash
- Starts at 1, increases every 50 blocks, caps at 6
- Increment nonce starting from 0 until valid hash found

### Block Timing

- Genesis block: timestamp = 1697412600
- Each block: +10 seconds from previous

## Key Algorithms

### Transaction Selection
1. Filter by `lock_time < next_block_timestamp`
2. Sort by `transaction_fee` (descending)
3. Take top 100

### Block Creation
1. Select transactions
2. Build Merkle tree → get root
3. Create header with Merkle root
4. Mine block (find valid nonce)
5. Add to blockchain

### Inclusion Proof
1. Build Merkle tree for block
2. Collect sibling nodes along path to root
3. Verify by recomputing root from transaction hash

## Bonus Tasks

- **Balance tracking**: Track balances as blocks are mined
- **Signature verification**: Validate ECDSA signatures
- **Transaction generation**: Create new signed transactions

## Testing

The project includes test functions in individual modules. Run them with:
```bash
python -m blockchain_client.serialization
python -m blockchain_client.merkle
```

## Troubleshooting

### Common Issues

1. **Wrong hash**: Check field ordering (alphabetical) and ensure no spaces in serialization
2. **Merkle root mismatch**: Verify hash pair ordering (sorted comparison)
3. **Mining too slow**: Lower difficulty or verify hash comparison logic
4. **Transaction not found**: Check that lock_time filtering is correct

## Next Steps

1. Test serialization with provided example
2. Load and inspect blockchain.json.gz
3. Mine a single block and verify output
4. Implement proof generation/verification
5. Mine multiple blocks
6. Attempt bonus tasks

