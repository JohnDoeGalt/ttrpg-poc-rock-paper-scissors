"""
Lineage Registry for tracking population splits.
Uses unique IDs instead of long concatenated strings for scalability.
"""
from dataclasses import dataclass
from typing import Optional, Dict, List
from components import RPSType


@dataclass
class LineageEntry:
    """Entry in the lineage registry tracking a single split event."""
    lineage_id: int
    parent_lineage_id: Optional[int]  # None for base lineages (first splits)
    original_base_type: RPSType  # The base type that split
    split_to_type: RPSType  # The base type it split into
    generation: int  # How many splits deep (0 = first split from base type)


class LineageRegistry:
    """
    Registry that tracks all lineages with unique IDs.
    Scales infinitely without creating long string names.
    """
    
    def __init__(self):
        self._lineages: Dict[int, LineageEntry] = {}
        self._next_id: int = 1  # Start at 1, 0 reserved for "no lineage"
    
    def create_lineage(self, parent_lineage_id: Optional[int], 
                       original_base_type: RPSType, 
                       split_to_type: RPSType) -> int:
        """
        Create a new lineage entry and return its ID.
        
        Args:
            parent_lineage_id: ID of parent lineage (None for first splits from base types)
            original_base_type: The base type that is splitting
            split_to_type: The base type it's splitting into
        
        Returns:
            The new lineage ID
        """
        # Calculate generation
        if parent_lineage_id is None:
            generation = 0
        else:
            parent = self._lineages.get(parent_lineage_id)
            generation = parent.generation + 1 if parent else 0
        
        lineage_id = self._next_id
        self._next_id += 1
        
        entry = LineageEntry(
            lineage_id=lineage_id,
            parent_lineage_id=parent_lineage_id,
            original_base_type=original_base_type,
            split_to_type=split_to_type,
            generation=generation
        )
        
        self._lineages[lineage_id] = entry
        return lineage_id
    
    def get_lineage(self, lineage_id: int) -> Optional[LineageEntry]:
        """Get a lineage entry by ID."""
        return self._lineages.get(lineage_id)
    
    def get_lineage_path(self, lineage_id: int) -> List[str]:
        """
        Reconstruct the full lineage path as a list of type names.
        Example: [rock, paper, scissors] for rock -> paper -> scissors
        
        Returns empty list if lineage_id is None or not found.
        """
        if lineage_id is None or lineage_id == 0:
            return []
        
        path = []
        current_id = lineage_id
        
        while current_id is not None and current_id != 0:
            entry = self._lineages.get(current_id)
            if entry is None:
                break
            
            # Add the split_to_type to the path (this is what they became)
            path.insert(0, entry.split_to_type.value)
            
            # If this is generation 0, also add the original type
            if entry.generation == 0:
                path.insert(0, entry.original_base_type.value)
            
            current_id = entry.parent_lineage_id
        
        return path
    
    def get_lineage_string(self, lineage_id: Optional[int]) -> str:
        """
        Get a human-readable lineage string.
        Example: "rock -> paper -> scissors"
        Returns "base" if no lineage.
        """
        if lineage_id is None or lineage_id == 0:
            return "base"
        
        path = self.get_lineage_path(lineage_id)
        if not path:
            return "base"
        
        return " -> ".join(path)
    
    def get_all_lineages(self) -> Dict[int, LineageEntry]:
        """Get all lineage entries."""
        return self._lineages.copy()
    
    def get_lineages_by_base_type(self, base_type: RPSType) -> List[LineageEntry]:
        """Get all lineages that end with the given base type."""
        return [entry for entry in self._lineages.values() 
                if entry.split_to_type == base_type]
    
    def clear(self):
        """Clear all lineages (useful for resetting simulation)."""
        self._lineages.clear()
        self._next_id = 1


# Global registry instance
_registry: Optional[LineageRegistry] = None


def get_registry() -> LineageRegistry:
    """Get the global lineage registry instance."""
    global _registry
    if _registry is None:
        _registry = LineageRegistry()
    return _registry


def reset_registry():
    """Reset the global registry (useful for testing/resetting)."""
    global _registry
    _registry = LineageRegistry()

