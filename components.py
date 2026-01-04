"""
ECS Components for the Rock-Paper-Scissors simulation.
Components are pure data containers with no behavior.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RPSType(Enum):
    """Base Rock-Paper-Scissors types."""
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


@dataclass
class Room:
    """Component representing a room in the simulation."""
    room_id: int
    adjacent_rooms: list[int]  # List of room IDs that are adjacent
    population_limit: int  # Maximum number of people allowed in this room
    depth: int  # Depth in the tree (0 = center, higher = further out)
    resources: int  # Current resource value (starts at half of max population)
    consecutive_zero_resources: int  # Number of consecutive ticks with 0 resources


@dataclass
class Person:
    """
    Component representing a person in the simulation.
    Uses base RPSType for gameplay. Lineage is tracked separately via Lineage component.
    """
    person_id: int
    rps_type: RPSType  # Base type for gameplay
    room_id: int


@dataclass
class Lineage:
    """
    Component tracking the lineage history of a person.
    References a lineage ID in the LineageRegistry.
    None means the person has no lineage (original base type).
    """
    lineage_id: Optional[int] = None


@dataclass
class Travel:
    """
    Component tracking a person who is traveling between rooms.
    Person is on a path and will arrive at destination_room_id after 1 tick.
    """
    source_room_id: int  # Room they left
    destination_room_id: int  # Room they're traveling to


class DeathCause(Enum):
    """Enum for different causes of death."""
    NATURAL = "natural"  # White X
    STARVATION = "starvation"  # Black X
    COMBAT = "combat"  # Red X


@dataclass
class DeathMarker:
    """
    Component marking a person for death.
    They will be eliminated next tick, with visual indicator this tick.
    """
    cause: DeathCause  # Cause of death (determines X color)

