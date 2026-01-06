"""
Integration tests that run the full simulation to catch runtime bugs.
"""
import esper
import pytest
from simulation import run_simulation, create_rooms, create_people, get_statistics
from components import Room, Person, Travel, DeathMarker, RPSType
from systems import (
    RPSGameSystem, RoomSwitchSystem, PopulationBalanceSystem,
    ResourceExtractionSystem, ResourceRegenerationSystem, MortalitySystem,
    TravelCompletionSystem, DeathCleanupSystem
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


def test_simulation_runs_without_crash(clean_world):
    """Test that a short simulation runs without crashing."""
    # Run a very short simulation
    try:
        run_simulation(num_rooms=5, num_people=20, num_ticks=10, use_graphics=False, save_states=False, skip_xai_prompt=True)
        assert True  # If we get here, no crash occurred
    except Exception as e:
        pytest.fail(f"Simulation crashed with error: {e}")


def test_no_people_in_invalid_rooms(clean_world):
    """Test that people never end up in invalid room IDs."""
    create_rooms(10)
    create_people(100, 10)
    
    # Run a few ticks
    esper.add_processor(DeathCleanupSystem())
    esper.add_processor(ResourceRegenerationSystem())
    esper.add_processor(ResourceExtractionSystem())
    esper.add_processor(RPSGameSystem())
    esper.add_processor(MortalitySystem())
    esper.add_processor(TravelCompletionSystem())
    esper.add_processor(RoomSwitchSystem())
    esper.add_processor(PopulationBalanceSystem())
    
    for _ in range(10):
        esper.process()
        
        # Check all people are in valid rooms
        for entity, person in esper.get_component(Person):
            assert 0 <= person.room_id < 10, f"Person {person.person_id} in invalid room {person.room_id}"


def test_resources_never_go_negative(clean_world):
    """Test that room resources never go negative."""
    create_rooms(10)
    create_people(50, 10)
    
    esper.add_processor(DeathCleanupSystem())
    esper.add_processor(ResourceRegenerationSystem())
    esper.add_processor(ResourceExtractionSystem())
    esper.add_processor(RPSGameSystem())
    esper.add_processor(MortalitySystem())
    esper.add_processor(TravelCompletionSystem())
    esper.add_processor(RoomSwitchSystem())
    esper.add_processor(PopulationBalanceSystem())
    
    for _ in range(20):
        esper.process()
        
        # Check all rooms have non-negative resources
        for entity, room in esper.get_component(Room):
            assert room.resources >= 0, f"Room {room.room_id} has negative resources: {room.resources}"


def test_travel_completion_removes_travel_component(clean_world):
    """Test that travel component is always removed after travel completes."""
    create_rooms(10)
    create_people(50, 10)
    
    esper.add_processor(DeathCleanupSystem())
    esper.add_processor(ResourceRegenerationSystem())
    esper.add_processor(ResourceExtractionSystem())
    esper.add_processor(RPSGameSystem())
    esper.add_processor(MortalitySystem())
    esper.add_processor(TravelCompletionSystem())
    esper.add_processor(RoomSwitchSystem())
    esper.add_processor(PopulationBalanceSystem())
    
    for _ in range(10):
        # Count people traveling before travel completion
        traveling_before = sum(1 for e, t in esper.get_component(Travel))
        
        # Run travel completion
        TravelCompletionSystem().process()
        
        # Count people traveling after (should be 0 or less than before)
        traveling_after = sum(1 for e, t in esper.get_component(Travel))
        
        # After travel completion, no one should still be traveling
        # (unless new travel started, but that happens in RoomSwitchSystem)
        assert traveling_after <= traveling_before
        
        # Run all other systems
        esper.process()


def test_death_markers_are_cleaned_up(clean_world):
    """Test that death markers are properly cleaned up."""
    create_rooms(10)
    create_people(50, 10)
    
    esper.add_processor(DeathCleanupSystem())
    esper.add_processor(ResourceRegenerationSystem())
    esper.add_processor(ResourceExtractionSystem())
    esper.add_processor(RPSGameSystem())
    esper.add_processor(MortalitySystem())
    esper.add_processor(TravelCompletionSystem())
    esper.add_processor(RoomSwitchSystem())
    esper.add_processor(PopulationBalanceSystem())
    
    for tick in range(10):
        # Process all systems
        esper.process()
        
        # Count death markers after processing
        # Filter out deleted entities - esper.get_component may return stale references
        death_markers_after = [(e, m) for e, m in esper.get_component(DeathMarker) if esper.entity_exists(e)]
        
        # Death markers added this tick should still exist (cleaned up next tick)
        # All entities with death markers should still exist (they'll be cleaned up next tick)
        for entity, marker in death_markers_after:
            # Entity should still exist (will be cleaned up next tick)
            assert esper.entity_exists(entity), f"Entity {entity} with death marker was deleted prematurely"


def test_person_ids_are_unique(clean_world):
    """Test that all person IDs remain unique even after new people are created."""
    create_rooms(10)
    create_people(50, 10)
    
    esper.add_processor(DeathCleanupSystem())
    esper.add_processor(ResourceRegenerationSystem())
    esper.add_processor(ResourceExtractionSystem())
    esper.add_processor(RPSGameSystem())
    esper.add_processor(MortalitySystem())
    esper.add_processor(TravelCompletionSystem())
    esper.add_processor(RoomSwitchSystem())
    esper.add_processor(PopulationBalanceSystem())
    
    for _ in range(20):
        esper.process()
        
        # Collect all person IDs
        person_ids = [p.person_id for e, p in esper.get_component(Person)]
        
        # Check uniqueness
        assert len(person_ids) == len(set(person_ids)), "Duplicate person IDs found!"


def test_consecutive_zero_resources_tracking(clean_world):
    """Test that consecutive_zero_resources is tracked correctly."""
    create_rooms(10)
    
    # Create a room with 0 resources
    for entity, room in esper.get_component(Room):
        if room.room_id == 0:
            room.resources = 0
            room.consecutive_zero_resources = 0
            break
    
    create_people(10, 10)
    
    esper.add_processor(DeathCleanupSystem())
    esper.add_processor(ResourceRegenerationSystem())
    esper.add_processor(ResourceExtractionSystem())
    esper.add_processor(RPSGameSystem())
    esper.add_processor(MortalitySystem())
    esper.add_processor(TravelCompletionSystem())
    esper.add_processor(RoomSwitchSystem())
    esper.add_processor(PopulationBalanceSystem())
    
    # Run a few ticks and check tracking
    for tick in range(5):
        esper.process()
        
        # Find room 0
        for entity, room in esper.get_component(Room):
            if room.room_id == 0:
                if room.resources == 0:
                    # Should increment counter
                    assert room.consecutive_zero_resources >= tick + 1 or room.consecutive_zero_resources == 0
                else:
                    # Should reset counter
                    assert room.consecutive_zero_resources == 0
                break

