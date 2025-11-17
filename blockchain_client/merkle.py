"""
Merkle tree construction and proof generation/verification
"""
from hashlib import sha256
from typing import List, Tuple


# Null hash used for padding when odd number of nodes
NULL_HASH = "0x" + "0" * 64


def hash_pair(a: str, b: str) -> str:
    """
    Hash two values together according to the tutorial spec.
    
    H(a, b) = SHA256(a + b) if a < b
              SHA256(b + a) otherwise
    
    Args:
        a: First hash (with 0x prefix)
        b: Second hash (with 0x prefix)
        
    Returns:
        Combined hash (with 0x prefix)
    """
    # Remove 0x prefix for concatenation
    a_hex = a[2:]
    b_hex = b[2:]
    
    # Concatenate in sorted order
    if a < b:
        combined = a_hex + b_hex
    else:
        combined = b_hex + a_hex
    
    # Hash and return with 0x prefix
    hash_digest = sha256(combined.encode()).hexdigest()
    return f"0x{hash_digest}"


def build_merkle_tree(tx_hashes: List[str]) -> str:
    """
    Build a Merkle tree and return the root.
    
    If there's an odd number of nodes at any level, append NULL_HASH.
    
    Args:
        tx_hashes: List of transaction hashes
        
    Returns:
        Merkle root hash
    """
    if not tx_hashes:
        return NULL_HASH
    
    if len(tx_hashes) == 1:
        return tx_hashes[0]
    
    current_level = tx_hashes[:]
    
    while len(current_level) > 1:
        next_level = []
        
        # Process pairs
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            
            # If odd number, use NULL_HASH for right
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = NULL_HASH
            
            parent = hash_pair(left, right)
            next_level.append(parent)
        
        current_level = next_level
    
    return current_level[0]


def build_merkle_tree_with_proof(tx_hashes: List[str], tx_index: int) -> Tuple[str, List[str]]:
    """
    Build a Merkle tree and generate an inclusion proof for a specific transaction.
    
    Args:
        tx_hashes: List of transaction hashes
        tx_index: Index of the transaction to generate proof for
        
    Returns:
        Tuple of (merkle_root, proof_siblings)
    """
    if not tx_hashes or tx_index >= len(tx_hashes):
        raise ValueError("Invalid transaction index")
    
    if len(tx_hashes) == 1:
        return tx_hashes[0], []
    
    current_level = tx_hashes[:]
    current_index = tx_index
    proof = []
    
    while len(current_level) > 1:
        next_level = []
        next_index = current_index // 2
        
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                right = NULL_HASH
            
            # If this pair contains our target node, add sibling to proof
            if i == current_index:
                proof.append(right)
            elif i + 1 == current_index:
                proof.append(left)
            
            parent = hash_pair(left, right)
            next_level.append(parent)
        
        current_level = next_level
        current_index = next_index
    
    return current_level[0], proof


def verify_merkle_proof(tx_hash: str, proof: List[str], merkle_root: str, tx_index: int, total_txs: int) -> bool:
    """
    Verify a Merkle inclusion proof.
    
    Args:
        tx_hash: Hash of the transaction to verify
        proof: List of sibling hashes
        merkle_root: Expected Merkle root
        tx_index: Index of the transaction in the block
        total_txs: Total number of transactions in the block
        
    Returns:
        True if proof is valid, False otherwise
    """
    current = tx_hash
    current_index = tx_index
    current_level_size = total_txs
    
    for sibling in proof:
        # Determine if we're left or right child
        if current_index % 2 == 0:
            # We're left child
            current = hash_pair(current, sibling)
        else:
            # We're right child
            current = hash_pair(sibling, current)
        
        current_index //= 2
        current_level_size = (current_level_size + 1) // 2
    
    return current == merkle_root


if __name__ == "__main__":
    # Test with simple example
    test_hashes = [
        "0x" + "01" * 32,
        "0x" + "02" * 32,
        "0x" + "03" * 32,
        "0x" + "04" * 32,
        "0x" + "05" * 32,
    ]
    
    root = build_merkle_tree(test_hashes)
    print(f"Merkle root: {root}")
    
    # Generate proof for first transaction
    root_with_proof, proof = build_merkle_tree_with_proof(test_hashes, 0)
    print(f"Proof for tx 0: {proof}")
    
    # Verify the proof
    is_valid = verify_merkle_proof(test_hashes[0], proof, root_with_proof, 0, len(test_hashes))
    print(f"Proof valid: {is_valid}")

