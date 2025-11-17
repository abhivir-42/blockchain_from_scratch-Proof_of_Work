"""
Blockchain state management and operations
"""
import gzip
import json
from typing import Dict, List, Any
from .block import (
    create_block, select_transactions, calculate_difficulty,
    GENESIS_TIMESTAMP, BLOCK_TIME
)


def load_blockchain(filepath: str) -> List[Dict[str, Any]]:
    """
    Load blockchain from gzipped JSON file.
    
    Args:
        filepath: Path to blockchain.json.gz
        
    Returns:
        List of blocks
    """
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        blockchain = json.load(f)
    return blockchain


def save_blockchain(blockchain: List[Dict[str, Any]], filepath: str):
    """
    Save blockchain to gzipped JSON file.
    
    Args:
        blockchain: List of blocks
        filepath: Path to output file
    """
    with gzip.open(filepath, 'wt', encoding='utf-8') as f:
        json.dump(blockchain, f, indent=2)


def load_mempool(filepath: str) -> List[Dict[str, Any]]:
    """
    Load mempool from gzipped JSON file.
    
    Args:
        filepath: Path to mempool.json.gz
        
    Returns:
        List of transactions
    """
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        mempool = json.load(f)
    return mempool


def save_mempool(mempool: List[Dict[str, Any]], filepath: str):
    """
    Save mempool to gzipped JSON file.
    
    Args:
        mempool: List of transactions
        filepath: Path to output file
    """
    with gzip.open(filepath, 'wt', encoding='utf-8') as f:
        json.dump(mempool, f, indent=2)


def get_latest_block(blockchain: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get the most recent block from the blockchain.
    
    Args:
        blockchain: List of blocks
        
    Returns:
        Latest block
    """
    if not blockchain:
        return None
    return blockchain[-1]


def get_latest_block_hash(blockchain: List[Dict[str, Any]]) -> str:
    """
    Get the hash of the most recent block header.
    
    Args:
        blockchain: List of blocks
        
    Returns:
        Latest block header hash
    """
    latest_block = get_latest_block(blockchain)
    if latest_block:
        return latest_block['header']['hash']
    return "0x" + "0" * 64  # Genesis previous hash


def produce_blocks(blockchain: List[Dict[str, Any]], mempool: List[Dict[str, Any]], 
                  count: int, miner_address: str) -> tuple:
    """
    Produce multiple new blocks.
    
    Args:
        blockchain: Current blockchain state
        mempool: Current mempool
        count: Number of blocks to produce
        miner_address: Address of the miner
        
    Returns:
        Tuple of (updated_blockchain, updated_mempool)
    """
    blockchain = blockchain.copy()
    mempool = mempool.copy()
    
    for i in range(count):
        # Get info from latest block
        latest_block = get_latest_block(blockchain)
        
        if latest_block:
            height = latest_block['header']['height'] + 1
            previous_hash = latest_block['header']['hash']
            timestamp = latest_block['header']['timestamp'] + BLOCK_TIME
        else:
            # Genesis block
            height = 0
            previous_hash = "0x" + "0" * 64
            timestamp = GENESIS_TIMESTAMP
        
        # Select transactions
        selected_txs = select_transactions(mempool, timestamp)
        
        print(f"\nProducing block {height} with {len(selected_txs)} transactions...")
        
        # Create and mine block
        new_block = create_block(height, previous_hash, timestamp, selected_txs, miner_address)
        
        # Add to blockchain
        blockchain.append(new_block)
        
        # Remove selected transactions from mempool
        # (In a real system, you'd match by transaction hash)
        for tx in selected_txs:
            if tx in mempool:
                mempool.remove(tx)
    
    return blockchain, mempool


def get_transaction_by_index(blockchain: List[Dict[str, Any]], block_height: int, 
                             tx_index: int) -> Dict[str, Any]:
    """
    Get a specific transaction from a block.
    
    Args:
        blockchain: Blockchain state
        block_height: Height of the block
        tx_index: Index of transaction in block
        
    Returns:
        Transaction dictionary
    """
    if block_height >= len(blockchain):
        raise ValueError(f"Block height {block_height} does not exist")
    
    block = blockchain[block_height]
    transactions = block['transactions']
    
    if tx_index >= len(transactions):
        raise ValueError(f"Transaction index {tx_index} does not exist in block {block_height}")
    
    return transactions[tx_index]

