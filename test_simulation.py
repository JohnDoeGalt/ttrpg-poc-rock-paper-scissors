"""
Tests for simulation functions.
"""
import esper
import pytest
from simulation import (
    create_rooms, create_people, get_statistics,
    _build_room_tree
)
from components import Room, Person, RPSType
from lineage_registry import reset_registry


@pytest.fixture
def clean_world():
    """Fixture to clean the ECS world before each test."""
    esper.clear_database()
    reset_registry()
    yield
    esper.clear_database()
    reset_registry()


def test_build_room_tree():
    """Test room tree building."""
    # Test with 1 room
    tree = _build_room_tree(1)
    assert len(tree) == 1
    assert 0 in tree
    assert tree[0]['depth'] == 0
    
    # Test with 10 rooms
    tree = _build_room_tree(10)
    assert len(tree) == 10
    assert 0 in tree
    assert tree[0]['depth'] == 0
    
    # Verify all rooms have depth
    for room_id in range(10):
        assert room_id in tree
        assert 'depth' in tree[room_id]
        assert 'adjacent' in tree[room_id]
    
    # Verify room 0 (center) has adjacent rooms
    assert len(tree[0]['adjacent']) > 0


def test_create_rooms(clean_world):
    """Test room creation."""
    room_entities = create_rooms(10)
    
    assert len(room_entities) == 10
    
    # Verify all rooms exist in ECS
    room_count = 0
    for entity, room in esper.get_component(Room):
        assert room.room_id in room_entities
        assert room_entities[room.room_id] == entity
        room_count += 1
    
    assert room_count == 10
    
    # Verify room properties
    for entity, room in esper.get_component(Room):
        assert room.population_limit > 0
        assert room.depth >= 0
        assert room.resources >= 0
        assert isinstance(room.adjacent_rooms, list)


def test_create_people(clean_world):
    """Test people creation."""
    create_rooms(10)
    create_people(100, 10)
    
    # Count people
    people_count = 0
    room_ids_seen = set()
    rps_types_seen = set()
    
    for entity, person in esper.get_component(Person):
        people_count += 1
        assert 0 <= person.room_id < 10
        room_ids_seen.add(person.room_id)
        rps_types_seen.add(person.rps_type)
    
    assert people_count == 100
    assert len(room_ids_seen) > 0  # People should be in multiple rooms
    assert len(rps_types_seen) == 3  # All three RPS types should be present


def test_get_statistics(clean_world):
    """Test statistics collection."""
    create_rooms(10)
    create_people(100, 10)
    
    stats = get_statistics(10)
    
    assert stats['total_people'] == 100
    assert sum(stats['by_base_type'].values()) == 100
    assert stats['by_base_type'][RPSType.ROCK] >= 0
    assert stats['by_base_type'][RPSType.PAPER] >= 0
    assert stats['by_base_type'][RPSType.SCISSORS] >= 0
    
    assert len(stats['by_room']) == 10
    total_by_room = sum(room['total'] for room in stats['by_room'].values())
    assert total_by_room == 100


def test_room_tree_connectivity():
    """Test that room tree is properly connected."""
    tree = _build_room_tree(10)
    
    # All rooms except room 0 should have at least one adjacent room
    for room_id in range(1, 10):
        assert len(tree[room_id]['adjacent']) > 0
    
    # Room 0 should have adjacent rooms
    assert len(tree[0]['adjacent']) > 0
    
    # Verify bidirectional connections (if A is adjacent to B, B should be adjacent to A)
    for room_id, room_data in tree.items():
        for adjacent_id in room_data['adjacent']:
            assert room_id in tree[adjacent_id]['adjacent']


def test_room_population_limits(clean_world):
    """Test that rooms have appropriate population limits."""
    room_entities = create_rooms(10)
    
    # Get depth 0 room (center)
    center_room = None
    for entity, room in esper.get_component(Room):
        if room.depth == 0:
            center_room = room
            break
    
    assert center_room is not None
    
    # Center room should have highest limit
    max_limit = center_room.population_limit
    
    # All other rooms should have lower or equal limits
    for entity, room in esper.get_component(Room):
        assert room.population_limit <= max_limit
        assert room.population_limit >= 5  # Minimum limit

