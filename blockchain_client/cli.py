"""
Command-line interface for blockchain client
"""
import argparse
import sys
from .blockchain import (
    load_blockchain, save_blockchain, load_mempool, save_mempool,
    produce_blocks, get_transaction_by_index
)
from .serialization import hash_transaction
from .proof import generate_inclusion_proof, verify_inclusion_proof, save_proof, load_proof


def cmd_produce_blocks(args):
    """Produce new blocks"""
    # Load state
    print(f"Loading blockchain from {args.blockchain_state}...")
    blockchain = load_blockchain(args.blockchain_state)
    print(f"Loaded {len(blockchain)} blocks")
    
    print(f"Loading mempool from {args.mempool}...")
    mempool = load_mempool(args.mempool)
    print(f"Loaded {len(mempool)} transactions")
    
    # Use first address from blockchain as miner (or provide a default)
    miner_address = "0xdc45038aee5144bbfa641912eaf32ebf2bad2bd7"  # Default miner
    
    # Produce blocks
    print(f"\nProducing {args.n} blocks...")
    blockchain, mempool = produce_blocks(blockchain, mempool, args.n, miner_address)
    
    # Save results
    print(f"\nSaving blockchain to {args.blockchain_output}...")
    save_blockchain(blockchain, args.blockchain_output)
    
    print(f"Saving mempool to {args.mempool_output}...")
    save_mempool(mempool, args.mempool_output)
    
    print(f"\n✓ Successfully produced {args.n} blocks!")


def cmd_get_tx_hash(args):
    """Get transaction hash"""
    blockchain = load_blockchain(args.blockchain_state)
    
    tx = get_transaction_by_index(blockchain, args.block_height, args.tx_index)
    tx_hash = hash_transaction(tx)
    
    print(tx_hash)


def cmd_generate_proof(args):
    """Generate inclusion proof"""
    blockchain = load_blockchain(args.blockchain_state)
    
    if args.block_height >= len(blockchain):
        print(f"Error: Block {args.block_height} does not exist", file=sys.stderr)
        sys.exit(1)
    
    block = blockchain[args.block_height]
    
    try:
        proof = generate_inclusion_proof(block, args.tx_hash)
        save_proof(proof, args.output)
        print(f"✓ Proof generated and saved to {args.output}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_verify_proof(args):
    """Verify inclusion proof"""
    proof = load_proof(args.proof_file)
    blockchain = load_blockchain(args.blockchain_state) if args.blockchain_state else None
    
    is_valid = verify_inclusion_proof(proof, blockchain)
    
    if is_valid:
        print("✓ Proof is VALID")
        sys.exit(0)
    else:
        print("✗ Proof is INVALID")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Blockchain Client for Tutorial 1",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--blockchain-state',
        type=str,
        help='Path to blockchain state file (blockchain.json.gz)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # produce-blocks command
    produce_parser = subparsers.add_parser('produce-blocks', help='Produce new blocks')
    produce_parser.add_argument('--mempool', type=str, required=True,
                               help='Path to mempool file')
    produce_parser.add_argument('--blockchain-output', type=str, required=True,
                               help='Path to output blockchain file')
    produce_parser.add_argument('--mempool-output', type=str, required=True,
                               help='Path to output mempool file')
    produce_parser.add_argument('-n', type=int, required=True,
                               help='Number of blocks to produce')
    produce_parser.set_defaults(func=cmd_produce_blocks)
    
    # get-tx-hash command
    gettx_parser = subparsers.add_parser('get-tx-hash', help='Get transaction hash')
    gettx_parser.add_argument('block_height', type=int, help='Block height')
    gettx_parser.add_argument('tx_index', type=int, help='Transaction index')
    gettx_parser.set_defaults(func=cmd_get_tx_hash)
    
    # generate-proof command
    genproof_parser = subparsers.add_parser('generate-proof', help='Generate inclusion proof')
    genproof_parser.add_argument('block_height', type=int, help='Block height')
    genproof_parser.add_argument('tx_hash', type=str, help='Transaction hash')
    genproof_parser.add_argument('-o', '--output', type=str, required=True,
                                help='Output proof file')
    genproof_parser.set_defaults(func=cmd_generate_proof)
    
    # verify-proof command
    verify_parser = subparsers.add_parser('verify-proof', help='Verify inclusion proof')
    verify_parser.add_argument('proof_file', type=str, help='Proof file to verify')
    verify_parser.set_defaults(func=cmd_verify_proof)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()

