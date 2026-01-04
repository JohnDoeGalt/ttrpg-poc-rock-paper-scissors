"""
Tests for LineageRegistry.
"""
import pytest
from lineage_registry import LineageRegistry, reset_registry, get_registry
from components import RPSType


def test_lineage_registry_creation():
    """Test creating a new lineage registry."""
    registry = LineageRegistry()
    assert registry._next_id == 1
    assert len(registry._lineages) == 0


def test_create_base_lineage():
    """Test creating a base lineage (first split from base type)."""
    registry = LineageRegistry()
    
    lineage_id = registry.create_lineage(
        parent_lineage_id=None,
        original_base_type=RPSType.ROCK,
        split_to_type=RPSType.PAPER
    )
    
    assert lineage_id == 1
    assert registry._next_id == 2
    
    entry = registry.get_lineage(lineage_id)
    assert entry is not None
    assert entry.lineage_id == 1
    assert entry.parent_lineage_id is None
    assert entry.original_base_type == RPSType.ROCK
    assert entry.split_to_type == RPSType.PAPER
    assert entry.generation == 0


def test_create_nested_lineage():
    """Test creating a nested lineage (split from existing lineage)."""
    registry = LineageRegistry()
    
    # Create base lineage
    base_id = registry.create_lineage(
        parent_lineage_id=None,
        original_base_type=RPSType.ROCK,
        split_to_type=RPSType.PAPER
    )
    
    # Create nested lineage
    nested_id = registry.create_lineage(
        parent_lineage_id=base_id,
        original_base_type=RPSType.PAPER,
        split_to_type=RPSType.SCISSORS
    )
    
    assert nested_id == 2
    nested_entry = registry.get_lineage(nested_id)
    assert nested_entry.parent_lineage_id == base_id
    assert nested_entry.generation == 1


def test_get_lineage_path():
    """Test reconstructing lineage path."""
    registry = LineageRegistry()
    
    # Create base lineage: rock -> paper
    base_id = registry.create_lineage(
        parent_lineage_id=None,
        original_base_type=RPSType.ROCK,
        split_to_type=RPSType.PAPER
    )
    
    # Create nested: paper -> scissors
    nested_id = registry.create_lineage(
        parent_lineage_id=base_id,
        original_base_type=RPSType.PAPER,
        split_to_type=RPSType.SCISSORS
    )
    
    path = registry.get_lineage_path(nested_id)
    assert path == ["rock", "paper", "scissors"]


def test_get_lineage_string():
    """Test getting human-readable lineage string."""
    registry = LineageRegistry()
    
    base_id = registry.create_lineage(
        parent_lineage_id=None,
        original_base_type=RPSType.ROCK,
        split_to_type=RPSType.PAPER
    )
    
    lineage_str = registry.get_lineage_string(base_id)
    assert lineage_str == "rock -> paper"
    
    # Test None/0 returns "base"
    assert registry.get_lineage_string(None) == "base"
    assert registry.get_lineage_string(0) == "base"


def test_get_all_lineages():
    """Test getting all lineages."""
    registry = LineageRegistry()
    
    id1 = registry.create_lineage(None, RPSType.ROCK, RPSType.PAPER)
    id2 = registry.create_lineage(id1, RPSType.PAPER, RPSType.SCISSORS)
    
    all_lineages = registry.get_all_lineages()
    assert len(all_lineages) == 2
    assert id1 in all_lineages
    assert id2 in all_lineages


def test_clear_registry():
    """Test clearing the registry."""
    registry = LineageRegistry()
    
    registry.create_lineage(None, RPSType.ROCK, RPSType.PAPER)
    assert len(registry._lineages) == 1
    
    registry.clear()
    assert len(registry._lineages) == 0
    assert registry._next_id == 1


def test_global_registry():
    """Test global registry functions."""
    reset_registry()
    registry1 = get_registry()
    registry2 = get_registry()
    
    # Should be the same instance
    assert registry1 is registry2
    
    # Reset should create new instance
    reset_registry()
    registry3 = get_registry()
    assert registry3 is not registry1

