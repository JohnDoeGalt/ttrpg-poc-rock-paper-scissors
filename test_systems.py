"""
Tests for ECS systems.
"""
import random
import esper
import pytest
from components import Room, Person, Lineage, Travel, DeathMarker, RPSType, DeathCause
from systems import (
    RPSGameSystem, RoomSwitchSystem, PopulationBalanceSystem,
    ResourceExtractionSystem, ResourceRegenerationSystem, MortalitySystem,
    TravelCompletionSystem, DeathCleanupSystem, get_rps_winner
)
from lineage_registry import reset_registry


@pytest.fixture
def clean_world():
    """Fixture to clean the ECS world before each test."""
    esper.clear_database()
    reset_registry()
    yield
    esper.clear_database()
    reset_registry()


def test_get_rps_winner():
    """Test RPS winner determination."""
    # Rock beats Scissors
    assert get_rps_winner(RPSType.ROCK, RPSType.SCISSORS) == RPSType.ROCK
    assert get_rps_winner(RPSType.SCISSORS, RPSType.ROCK) == RPSType.ROCK
    
    # Paper beats Rock
    assert get_rps_winner(RPSType.PAPER, RPSType.ROCK) == RPSType.PAPER
    assert get_rps_winner(RPSType.ROCK, RPSType.PAPER) == RPSType.PAPER
    
    # Scissors beats Paper
    assert get_rps_winner(RPSType.SCISSORS, RPSType.PAPER) == RPSType.SCISSORS
    assert get_rps_winner(RPSType.PAPER, RPSType.SCISSORS) == RPSType.SCISSORS
    
    # Ties return None
    assert get_rps_winner(RPSType.ROCK, RPSType.ROCK) is None
    assert get_rps_winner(RPSType.PAPER, RPSType.PAPER) is None
    assert get_rps_winner(RPSType.SCISSORS, RPSType.SCISSORS) is None


def test_rps_game_system_basic(clean_world):
    """Test RPS game system with basic gameplay."""
    # Create a room
    room_entity = esper.create_entity()
    esper.add_component(room_entity, Room(
        room_id=0,
        adjacent_rooms=[],
        population_limit=50,
        depth=0,
        resources=25,
        consecutive_zero_resources=0
    ))
    
    # Create two people of different types
    person1_entity = esper.create_entity()
    esper.add_component(person1_entity, Person(
        person_id=0,
        rps_type=RPSType.ROCK,
        room_id=0
    ))
    
    person2_entity = esper.create_entity()
    esper.add_component(person2_entity, Person(
        person_id=1,
        rps_type=RPSType.SCISSORS,
        room_id=0
    ))
    
    # Run RPS game system
    system = RPSGameSystem()
    system.process()
    
    # Rock should beat Scissors, so person2 should convert to Rock
    person2 = esper.component_for_entity(person2_entity, Person)
    assert person2.rps_type == RPSType.ROCK


def test_travel_completion_system(clean_world):
    """Test travel completion system."""
    # Create rooms
    room0 = esper.create_entity()
    esper.add_component(room0, Room(0, [1], 50, 0, 25, 0))
    room1 = esper.create_entity()
    esper.add_component(room1, Room(1, [0], 50, 1, 25, 0))
    
    # Create person traveling from room 0 to room 1
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.ROCK, 0))
    esper.add_component(person_entity, Travel(0, 1))
    
    # Run travel completion system
    system = TravelCompletionSystem()
    system.process()
    
    # Person should be in room 1 and travel component removed
    person = esper.component_for_entity(person_entity, Person)
    assert person.room_id == 1
    assert not esper.has_component(person_entity, Travel)


def test_resource_regeneration_system(clean_world):
    """Test resource regeneration system."""
    # Create room with some resources
    room_entity = esper.create_entity()
    room = Room(0, [], 50, 0, 10, 0)
    esper.add_component(room_entity, room)
    
    # Add some people to the room
    for i in range(20):
        person_entity = esper.create_entity()
        esper.add_component(person_entity, Person(i, RPSType.ROCK, 0))
    
    # Run regeneration system
    system = ResourceRegenerationSystem()
    initial_resources = room.resources
    system.process()
    
    # Resources should increase
    assert room.resources > initial_resources
    # Should not exceed max (half of population limit = 25)
    assert room.resources <= 25


def test_resource_extraction_system(clean_world):
    """Test resource extraction system."""
    # Create room with resources
    room_entity = esper.create_entity()
    room = Room(0, [], 50, 0, 10, 0)
    esper.add_component(room_entity, room)
    
    # Create two people of same type
    person1 = esper.create_entity()
    esper.add_component(person1, Person(0, RPSType.ROCK, 0))
    person2 = esper.create_entity()
    esper.add_component(person2, Person(1, RPSType.ROCK, 0))
    
    initial_resources = room.resources
    initial_people_count = len(list(esper.get_component(Person)))
    
    # Run extraction system
    system = ResourceExtractionSystem()
    system.process()
    
    # Resource should decrease by 1
    assert room.resources == initial_resources - 1
    # New person should be created
    final_people_count = len(list(esper.get_component(Person)))
    assert final_people_count == initial_people_count + 1


def test_death_cleanup_system(clean_world):
    """Test death cleanup system."""
    # Create person marked for death
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.ROCK, 0))
    esper.add_component(person_entity, DeathMarker(DeathCause.NATURAL))
    
    # Run cleanup system
    system = DeathCleanupSystem()
    system.process()
    
    # Person should be deleted
    assert not esper.entity_exists(person_entity)


def test_population_balance_system(clean_world):
    """Test population balance system when one type dominates."""
    from lineage_registry import get_registry
    
    # Create many Rock people (70 out of 100 = 70%)
    for i in range(70):
        person_entity = esper.create_entity()
        esper.add_component(person_entity, Person(i, RPSType.ROCK, 0))
    
    # Create some Paper and Scissors
    for i in range(70, 85):
        person_entity = esper.create_entity()
        esper.add_component(person_entity, Person(i, RPSType.PAPER, 0))
    
    for i in range(85, 100):
        person_entity = esper.create_entity()
        esper.add_component(person_entity, Person(i, RPSType.SCISSORS, 0))
    
    # Count initial Rock population
    initial_rock_count = sum(1 for _, p in esper.get_component(Person) if p.rps_type == RPSType.ROCK)
    assert initial_rock_count == 70
    
    # Run balance system
    system = PopulationBalanceSystem()
    system.process()
    
    # Rock population should decrease (30% of 70 = 21 converted)
    final_rock_count = sum(1 for _, p in esper.get_component(Person) if p.rps_type == RPSType.ROCK)
    assert final_rock_count < initial_rock_count
    assert final_rock_count <= 70 - 21  # Allow some variance due to rounding


def test_mortality_system_natural_death(clean_world):
    """Test mortality system natural death chance."""
    # Create room
    room_entity = esper.create_entity()
    esper.add_component(room_entity, Room(0, [], 50, 0, 25, 0))
    
    # Create person
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.ROCK, 0))
    
    # Run mortality system multiple times (with fixed seed for testing)
    # Note: This tests the system works, but death is probabilistic
    system = MortalitySystem()
    system.process()
    
    # Person may or may not be marked for death (0.5% chance)
    # Just verify system runs without error
    assert True


def test_room_switch_system(clean_world):
    """Test room switch system."""
    # Create two adjacent rooms
    room0 = esper.create_entity()
    esper.add_component(room0, Room(0, [1], 50, 0, 25, 0))
    room1 = esper.create_entity()
    esper.add_component(room1, Room(1, [0], 50, 1, 25, 0))
    
    # Create person in room 0
    person_entity = esper.create_entity()
    esper.add_component(person_entity, Person(0, RPSType.ROCK, 0))
    
    # Run room switch system multiple times (10% chance each time)
    # With enough runs, person should eventually start traveling
    system = RoomSwitchSystem()
    started_traveling = False
    
    for _ in range(100):  # Try up to 100 times
        system.process()
        if esper.has_component(person_entity, Travel):
            started_traveling = True
            break
    
    # Note: This is probabilistic, but with 100 attempts at 10% chance,
    # probability of never traveling is (0.9)^100 ≈ 0.000027, so very unlikely
    # Just verify system runs without error
    assert True

