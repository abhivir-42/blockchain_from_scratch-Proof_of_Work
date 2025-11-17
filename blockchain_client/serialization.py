"""
Serialization utilities for blocks and transactions
"""
from hashlib import sha256
from typing import Dict, Any


def serialize_transaction(transaction: Dict[str, Any]) -> str:
    """
    Serialize a transaction into a comma-separated string.
    
    Steps:
    1. Sort all fields alphabetically by key
    2. Produce comma-separated string (no spaces)
       - Numbers: decimal without leading zeros
       - Hex values: keep 0x prefix
    
    Args:
        transaction: Dictionary containing transaction fields
        
    Returns:
        Serialized string ready for hashing
    """
    # Sort keys alphabetically
    sorted_keys = sorted(transaction.keys())
    
    values = []
    for key in sorted_keys:
        value = transaction[key]
        if isinstance(value, int):
            # Numbers as decimal without leading zeros
            values.append(str(value))
        else:
            # Strings (hex addresses, signatures) as-is
            values.append(str(value))
    
    return ','.join(values)


def serialize_block_header(header: Dict[str, Any]) -> str:
    """
    Serialize a block header into a comma-separated string.
    
    Note: Do not include the 'hash' field when serializing for mining.
    
    Args:
        header: Dictionary containing block header fields
        
    Returns:
        Serialized string ready for hashing
    """
    # Remove 'hash' field if present (we're computing it)
    header_copy = {k: v for k, v in header.items() if k != 'hash'}
    
    # Sort keys alphabetically
    sorted_keys = sorted(header_copy.keys())
    
    values = []
    for key in sorted_keys:
        value = header_copy[key]
        if isinstance(value, int):
            # Numbers as decimal without leading zeros
            values.append(str(value))
        else:
            # Strings (hex hashes, addresses) as-is
            values.append(str(value))
    
    return ','.join(values)


def hash_transaction(transaction: Dict[str, Any]) -> str:
    """
    Compute the hash of a transaction.
    
    Args:
        transaction: Dictionary containing transaction fields
        
    Returns:
        Hex-encoded hash with 0x prefix
    """
    serialized = serialize_transaction(transaction)
    hash_digest = sha256(serialized.encode()).hexdigest()
    return f"0x{hash_digest}"


def hash_block_header(header: Dict[str, Any]) -> str:
    """
    Compute the hash of a block header.
    
    Args:
        header: Dictionary containing block header fields
        
    Returns:
        Hex-encoded hash with 0x prefix
    """
    serialized = serialize_block_header(header)
    hash_digest = sha256(serialized.encode()).hexdigest()
    return f"0x{hash_digest}"


def test_serialization():
    """Test with the example from the spec"""
    header = {
        "difficulty": 5,
        "height": 203,
        "transactions_merkle_root": "0xddba0c2d7d38a9bc8ba357d1fcb4a4be339ab5fddf8cdcc4419970e4746d1f6e",
        "miner": "0xdc45038aee5144bbfa641912eaf32ebf2bad2bd7",
        "previous_block_header_hash": "0xb2448304889df2935277464e90a73e53b9d2c5820c48de4a40d4fa5b844c7b57",
        "timestamp": 1697412660,
        "transactions_count": 97,
        "nonce": 0
    }
    
    expected = "073c348de2486c616699fcd8267dc895f2d8b43355b126295da92df2961f8a87"
    result = hash_block_header(header)
    
    assert result == f"0x{expected}", f"Expected 0x{expected}, got {result}"
    print(f"✓ Serialization test passed: {result}")


if __name__ == "__main__":
    test_serialization()

