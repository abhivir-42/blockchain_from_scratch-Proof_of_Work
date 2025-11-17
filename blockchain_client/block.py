"""
Block creation and validation
"""
from typing import Dict, List, Any
from .serialization import hash_transaction, hash_block_header
from .merkle import build_merkle_tree


# Constants from spec
GENESIS_TIMESTAMP = 1697412600
BLOCK_TIME = 10  # seconds
MAX_TRANSACTIONS_PER_BLOCK = 100
MAX_DIFFICULTY = 6
DIFFICULTY_INCREASE_INTERVAL = 50  # blocks


def calculate_difficulty(height: int) -> int:
    """
    Calculate difficulty based on block height.
    
    Starts at 1, increases by 1 every 50 blocks, caps at 6.
    
    Args:
        height: Block height
        
    Returns:
        Difficulty value
    """
    difficulty = 1 + (height // DIFFICULTY_INCREASE_INTERVAL)
    return min(difficulty, MAX_DIFFICULTY)


def select_transactions(mempool: List[Dict[str, Any]], next_block_timestamp: int, 
                       max_count: int = MAX_TRANSACTIONS_PER_BLOCK) -> List[Dict[str, Any]]:
    """
    Select transactions from mempool for inclusion in next block.
    
    Filter by lock_time and select the most profitable (highest fee).
    
    Args:
        mempool: List of pending transactions
        next_block_timestamp: Timestamp of the next block
        max_count: Maximum number of transactions to include
        
    Returns:
        List of selected transactions
    """
    # Filter transactions that can be included (lock_time < next_block_timestamp)
    executable = [tx for tx in mempool if tx['lock_time'] < next_block_timestamp]
    
    # Sort by transaction fee (descending - highest fees first)
    executable.sort(key=lambda tx: tx['transaction_fee'], reverse=True)
    
    # Take top max_count transactions
    return executable[:max_count]


def create_block_header(height: int, previous_hash: str, timestamp: int,
                       transactions: List[Dict[str, Any]], miner: str) -> Dict[str, Any]:
    """
    Create a block header (without hash and before mining).
    
    Args:
        height: Block height
        previous_hash: Hash of previous block header
        timestamp: Block timestamp
        transactions: List of transactions to include
        miner: Miner address
        
    Returns:
        Block header dictionary
    """
    # Calculate Merkle root
    tx_hashes = [hash_transaction(tx) for tx in transactions]
    merkle_root = build_merkle_tree(tx_hashes)
    
    # Calculate difficulty
    difficulty = calculate_difficulty(height)
    
    header = {
        "difficulty": difficulty,
        "height": height,
        "miner": miner,
        "nonce": 0,
        "previous_block_header_hash": previous_hash,
        "timestamp": timestamp,
        "transactions_count": len(transactions),
        "transactions_merkle_root": merkle_root
    }
    
    return header


def mine_block(header: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mine a block by finding a nonce that satisfies the difficulty requirement.
    
    Args:
        header: Block header with nonce starting at 0
        
    Returns:
        Block header with valid nonce and hash
    """
    difficulty = header['difficulty']
    required_prefix = "0x" + "0" * difficulty
    
    nonce = 0
    while True:
        header['nonce'] = nonce
        block_hash = hash_block_header(header)
        
        if block_hash.startswith(required_prefix):
            header['hash'] = block_hash
            print(f"Block mined! Height: {header['height']}, Nonce: {nonce}, Hash: {block_hash}")
            return header
        
        nonce += 1
        
        # Progress indicator every 10000 attempts
        if nonce % 10000 == 0:
            print(f"Mining block {header['height']}... nonce: {nonce}")


def create_block(height: int, previous_hash: str, timestamp: int,
                transactions: List[Dict[str, Any]], miner: str) -> Dict[str, Any]:
    """
    Create and mine a complete block.
    
    Args:
        height: Block height
        previous_hash: Hash of previous block header
        timestamp: Block timestamp
        transactions: List of transactions to include
        miner: Miner address
        
    Returns:
        Complete block dictionary with header and transactions
    """
    # Create header
    header = create_block_header(height, previous_hash, timestamp, transactions, miner)
    
    # Mine block
    mined_header = mine_block(header)
    
    # Create complete block
    block = {
        "header": mined_header,
        "transactions": transactions
    }
    
    return block


def validate_block(block: Dict[str, Any], previous_block: Dict[str, Any] = None) -> bool:
    """
    Validate a block.
    
    Checks:
    - Height is correct
    - Previous hash is correct
    - Hash has required leading zeros
    - Merkle root is valid
    
    Args:
        block: Block to validate
        previous_block: Previous block (None for genesis)
        
    Returns:
        True if valid, False otherwise
    """
    header = block['header']
    transactions = block['transactions']
    
    # Check height
    if previous_block:
        expected_height = previous_block['header']['height'] + 1
        if header['height'] != expected_height:
            return False
        
        # Check previous hash
        if header['previous_block_header_hash'] != previous_block['header']['hash']:
            return False
    
    # Check hash has required leading zeros
    difficulty = header['difficulty']
    required_prefix = "0x" + "0" * difficulty
    if not header['hash'].startswith(required_prefix):
        return False
    
    # Check Merkle root
    tx_hashes = [hash_transaction(tx) for tx in transactions]
    expected_merkle_root = build_merkle_tree(tx_hashes)
    if header['transactions_merkle_root'] != expected_merkle_root:
        return False
    
    return True

