"""
Tests for serialization utilities.
"""
import esper
import pytest
import json
import os
from components import Room, Person, Lineage, Travel, DeathMarker, RPSType, DeathCause
from serialization import serialize_world, save_simulation_states, load_simulation_states
from lineage_registry import reset_registry


@pytest.fixture
def clean_world():
    """Fixture to clean the ECS world before each test."""
    esper.clear_database()
    reset_registry()
    yield
    esper.clear_database()
    reset_registry()


def test_serialize_world_basic(clean_world):
    """Test basic world serialization."""
    # Create a room
    room_entity = esper.create_entity()
    esper.add_component(room_entity, Room(
        room_id=0,
        adjacent_rooms=[1, 2],
        population_limit=50,
        depth=0,
        resources=25,
        consecutive_zero_resources=0
    ))
    
    # Create a person
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(
        person_id=0,
        rps_type=RPSType.ROCK,
        room_id=0
    ))
    
    # Serialize
    state = serialize_world()
    
    assert "entities" in state
    assert len(state["entities"]) == 2  # Room and person
    
    # Verify room serialization
    room_found = False
    person_found = False
    for entity_str, components in state["entities"].items():
        if "Room" in components:
            room_found = True
            room_data = components["Room"]
            assert room_data["room_id"] == 0
            assert room_data["adjacent_rooms"] == [1, 2]
        if "Person" in components:
            person_found = True
            person_data = components["Person"]
            assert person_data["person_id"] == 0
            assert person_data["rps_type"] == "rock"  # Enum converted to string
    
    assert room_found
    assert person_found


def test_serialize_world_with_lineage(clean_world):
    """Test serialization with lineage component."""
    from lineage_registry import get_registry
    
    # Create lineage
    registry = get_registry()
    lineage_id = registry.create_lineage(None, RPSType.ROCK, RPSType.PAPER)
    
    # Create person with lineage
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.PAPER, 0))
    esper.add_component(person_entity, Lineage(lineage_id=lineage_id))
    
    # Serialize
    state = serialize_world()
    
    # Find person with lineage
    for entity_str, components in state["entities"].items():
        if "Person" in components and "Lineage" in components:
            lineage_data = components["Lineage"]
            assert lineage_data["lineage_id"] == lineage_id


def test_serialize_world_with_travel(clean_world):
    """Test serialization with travel component."""
    # Create person traveling
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.ROCK, 0))
    esper.add_component(person_entity, Travel(0, 1))
    
    # Serialize
    state = serialize_world()
    
    # Find person with travel
    for entity_str, components in state["entities"].items():
        if "Travel" in components:
            travel_data = components["Travel"]
            assert travel_data["source_room_id"] == 0
            assert travel_data["destination_room_id"] == 1


def test_serialize_world_with_death_marker(clean_world):
    """Test serialization with death marker."""
    # Create person marked for death
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.ROCK, 0))
    esper.add_component(person_entity, DeathMarker(DeathCause.NATURAL))
    
    # Serialize
    state = serialize_world()
    
    # Find person with death marker
    for entity_str, components in state["entities"].items():
        if "DeathMarker" in components:
            death_data = components["DeathMarker"]
            assert death_data["cause"] == "natural"


def test_save_and_load_simulation_states(clean_world):
    """Test saving and loading simulation states."""
    # Create some entities
    room_entity = esper.create_entity()
    esper.add_component(room_entity, Room(0, [], 50, 0, 25, 0))
    
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.ROCK, 0))
    
    # Serialize and save
    states = [serialize_world(), serialize_world()]
    test_filename = "test_simulation_states.json"
    
    try:
        save_simulation_states(states, test_filename)
        
        # Verify file exists
        assert os.path.exists(test_filename)
        
        # Load states
        loaded_states = load_simulation_states(test_filename)
        
        assert len(loaded_states) == 2
        assert "entities" in loaded_states[0]
        assert "entities" in loaded_states[1]
        
    finally:
        # Clean up
        if os.path.exists(test_filename):
            os.remove(test_filename)


def test_serialize_empty_world(clean_world):
    """Test serializing an empty world."""
    state = serialize_world()
    
    assert "entities" in state
    assert len(state["entities"]) == 0

