"""
Merkle inclusion proof generation and verification
"""
from typing import Dict, List, Any
import json
from .serialization import hash_transaction
from .merkle import build_merkle_tree_with_proof, verify_merkle_proof


def generate_inclusion_proof(block: Dict[str, Any], tx_hash: str) -> Dict[str, Any]:
    """
    Generate a Merkle inclusion proof for a transaction in a block.
    
    Args:
        block: Block containing the transaction
        tx_hash: Hash of the transaction
        
    Returns:
        Proof dictionary
    """
    transactions = block['transactions']
    tx_hashes = [hash_transaction(tx) for tx in transactions]
    
    # Find transaction index
    try:
        tx_index = tx_hashes.index(tx_hash)
    except ValueError:
        raise ValueError(f"Transaction {tx_hash} not found in block")
    
    # Generate proof
    merkle_root, proof_siblings = build_merkle_tree_with_proof(tx_hashes, tx_index)
    
    proof = {
        "block_height": block['header']['height'],
        "block_hash": block['header']['hash'],
        "transaction_hash": tx_hash,
        "transaction_index": tx_index,
        "merkle_root": merkle_root,
        "proof": proof_siblings,
        "total_transactions": len(transactions)
    }
    
    return proof


def verify_inclusion_proof(proof: Dict[str, Any], blockchain: List[Dict[str, Any]] = None) -> bool:
    """
    Verify a Merkle inclusion proof.
    
    Args:
        proof: Proof dictionary
        blockchain: Optional blockchain to verify against
        
    Returns:
        True if proof is valid
    """
    tx_hash = proof['transaction_hash']
    proof_siblings = proof['proof']
    merkle_root = proof['merkle_root']
    tx_index = proof['transaction_index']
    total_txs = proof['total_transactions']
    
    # Verify proof mathematically
    is_valid = verify_merkle_proof(tx_hash, proof_siblings, merkle_root, tx_index, total_txs)
    
    # If blockchain provided, verify merkle root matches block header
    if blockchain and is_valid:
        block_height = proof['block_height']
        if block_height < len(blockchain):
            block = blockchain[block_height]
            expected_merkle_root = block['header']['transactions_merkle_root']
            is_valid = is_valid and (merkle_root == expected_merkle_root)
    
    return is_valid


def save_proof(proof: Dict[str, Any], filepath: str):
    """
    Save proof to JSON file.
    
    Args:
        proof: Proof dictionary
        filepath: Output file path
    """
    with open(filepath, 'w') as f:
        json.dump(proof, f, indent=2)


def load_proof(filepath: str) -> Dict[str, Any]:
    """
    Load proof from JSON file.
    
    Args:
        filepath: Proof file path
        
    Returns:
        Proof dictionary
    """
    with open(filepath, 'r') as f:
        return json.load(f)

