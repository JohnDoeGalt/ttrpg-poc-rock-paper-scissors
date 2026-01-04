"""
Tests for ECS components.
"""
import pytest
from components import Room, Person, Lineage, Travel, RPSType, DeathMarker, DeathCause


def test_room_creation():
    """Test Room component creation."""
    room = Room(
        room_id=0,
        adjacent_rooms=[1, 2],
        population_limit=50,
        depth=0,
        resources=25,
        consecutive_zero_resources=0
    )
    assert room.room_id == 0
    assert room.adjacent_rooms == [1, 2]
    assert room.population_limit == 50
    assert room.depth == 0
    assert room.resources == 25
    assert room.consecutive_zero_resources == 0


def test_person_creation():
    """Test Person component creation."""
    person = Person(
        person_id=0,
        rps_type=RPSType.ROCK,
        room_id=0
    )
    assert person.person_id == 0
    assert person.rps_type == RPSType.ROCK
    assert person.room_id == 0


def test_lineage_creation():
    """Test Lineage component creation."""
    # With lineage ID
    lineage = Lineage(lineage_id=1)
    assert lineage.lineage_id == 1
    
    # Without lineage ID (None)
    lineage_none = Lineage()
    assert lineage_none.lineage_id is None


def test_travel_creation():
    """Test Travel component creation."""
    travel = Travel(
        source_room_id=0,
        destination_room_id=1
    )
    assert travel.source_room_id == 0
    assert travel.destination_room_id == 1


def test_death_marker_creation():
    """Test DeathMarker component creation."""
    marker = DeathMarker(cause=DeathCause.NATURAL)
    assert marker.cause == DeathCause.NATURAL
    
    marker2 = DeathMarker(cause=DeathCause.COMBAT)
    assert marker2.cause == DeathCause.COMBAT
    
    marker3 = DeathMarker(cause=DeathCause.STARVATION)
    assert marker3.cause == DeathCause.STARVATION


def test_rps_type_enum():
    """Test RPSType enum values."""
    assert RPSType.ROCK.value == "rock"
    assert RPSType.PAPER.value == "paper"
    assert RPSType.SCISSORS.value == "scissors"

