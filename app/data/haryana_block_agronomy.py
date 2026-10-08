"""
Re-export Haryana Block Agronomy Database in app namespace (app/data/haryana_block_agronomy.py).
"""
from src.data.haryana_block_agronomy import (
    HARYANA_BLOCK_AGRONOMY,
    get_all_blocks,
    get_blocks_by_district,
    get_block_by_name
)

__all__ = [
    "HARYANA_BLOCK_AGRONOMY",
    "get_all_blocks",
    "get_blocks_by_district",
    "get_block_by_name"
]
