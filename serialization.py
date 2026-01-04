"""
Serialization utilities for saving and loading simulation state.
Allows capturing the entire ECS world state at any point in time.
"""
import json
import esper
from typing import Dict, Any, List
from dataclasses import asdict
from enum import Enum
from components import Room, Person, Lineage, Travel, DeathMarker, RPSType, DeathCause


def serialize_component(component: Any) -> Dict[str, Any]:
    """
    Helper to serialize a component (convert dataclass to dict).
    Handles Enum types by converting them to their values.
    
    Args:
        component: A dataclass component instance
        
    Returns:
        Dictionary representation of the component
    """
    if isinstance(component, (Room, Person, Lineage, Travel, DeathMarker)):
        # Convert to dict first
        comp_dict = asdict(component)
        
        # Convert any Enum values to their string values for JSON serialization
        serialized = {}
        for key, value in comp_dict.items():
            if isinstance(value, Enum):
                serialized[key] = value.value  # Convert Enum to its value
            elif isinstance(value, list):
                # Handle lists that might contain Enums
                serialized[key] = [item.value if isinstance(item, Enum) else item for item in value]
            else:
                serialized[key] = value
        
        return serialized
    return {}  # Fallback for other types


def serialize_world() -> Dict[str, Any]:
    """
    Helper to serialize the entire world state.
    Captures all entities and their components.
    
    Returns:
        Dictionary containing all entities and their components
    """
    state = {
        "entities": {}
    }
    
    # Get all entities that have components
    all_entities = set()
    
    # Collect entities from all component types
    for component_type in [Room, Person, Lineage, Travel, DeathMarker]:
        for entity, component in esper.get_component(component_type):
            all_entities.add(entity)
    
    # Serialize each entity with all its components
    for entity in all_entities:
        components = {}
        
        # Check each component type
        if esper.has_component(entity, Room):
            components["Room"] = serialize_component(esper.component_for_entity(entity, Room))
        if esper.has_component(entity, Person):
            components["Person"] = serialize_component(esper.component_for_entity(entity, Person))
        if esper.has_component(entity, Lineage):
            components["Lineage"] = serialize_component(esper.component_for_entity(entity, Lineage))
        if esper.has_component(entity, Travel):
            components["Travel"] = serialize_component(esper.component_for_entity(entity, Travel))
        if esper.has_component(entity, DeathMarker):
            components["DeathMarker"] = serialize_component(esper.component_for_entity(entity, DeathMarker))
        
        if components:  # Only include entities with components
            state["entities"][str(entity)] = components
    
    return state


def save_simulation_states(states: List[Dict[str, Any]], filename: str = "simulation_states.json"):
    """
    Save a list of serialized states to a JSON file.
    
    Args:
        states: List of serialized world states (one per tick)
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(states, f, indent=4)
    print(f"\nSimulation states saved to: {filename}")


def load_simulation_states(filename: str = "simulation_states.json") -> List[Dict[str, Any]]:
    """
    Load serialized states from a JSON file.
    
    Args:
        filename: Input filename
        
    Returns:
        List of serialized world states
    """
    with open(filename, 'r') as f:
        states = json.load(f)
    return states

