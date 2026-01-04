"""
ECS Systems for the Rock-Paper-Scissors simulation.
Systems contain the behavior/logic that operates on entities with components.
"""
import random
from typing import Optional
import esper
from components import Person, Room, RPSType, Lineage, Travel, DeathMarker, DeathCause
from lineage_registry import get_registry


def get_rps_winner(type1: RPSType, type2: RPSType) -> Optional[RPSType]:
    """
    Determine the winner of a Rock-Paper-Scissors match.
    Returns the winning RPSType, or None if it's a tie.
    """
    if type1 == type2:
        return None  # Tie
    
    win_conditions = {
        RPSType.ROCK: RPSType.SCISSORS,
        RPSType.PAPER: RPSType.ROCK,
        RPSType.SCISSORS: RPSType.PAPER
    }
    
    if win_conditions[type1] == type2:
        return type1
    else:
        return type2


class RPSGameSystem(esper.Processor):
    """
    System that handles Rock-Paper-Scissors games within each room.
    Pairs up people randomly and makes them play. Losers change to the winner's type and lineage.
    """
    
    def process(self):
        """Process RPS games for all rooms each tick."""
        # Get all rooms
        rooms = {}
        for entity, room in esper.get_component(Room):
            rooms[room.room_id] = []
        
        # Group people by room (exclude those traveling)
        for entity, person in esper.get_component(Person):
            if not esper.has_component(entity, Travel):
                rooms[person.room_id].append(entity)
        
        # Process each room
        for room_id, person_entities in rooms.items():
            if len(person_entities) < 2:
                continue  # Need at least 2 people to play
            
            # Shuffle to randomize pairings
            random.shuffle(person_entities)
            
            # Pair up people (handle odd numbers)
            pairs = []
            for i in range(0, len(person_entities) - 1, 2):
                pairs.append((person_entities[i], person_entities[i + 1]))
            
            # Play RPS for each pair
            for entity1, entity2 in pairs:
                person1 = esper.component_for_entity(entity1, Person)
                person2 = esper.component_for_entity(entity2, Person)
                
                winner_type = get_rps_winner(person1.rps_type, person2.rps_type)
                
                if winner_type is None:
                    continue  # Tie, no change
                
                # 20% chance: eliminate loser, 80% chance: convert loser
                if random.random() < 0.20:
                    # Mark loser for death (combat elimination)
                    if winner_type == person1.rps_type:
                        # person1 wins, mark person2 for death
                        if not esper.has_component(entity2, DeathMarker):
                            esper.add_component(entity2, DeathMarker(cause=DeathCause.COMBAT))
                    else:
                        # person2 wins, mark person1 for death
                        if not esper.has_component(entity1, DeathMarker):
                            esper.add_component(entity1, DeathMarker(cause=DeathCause.COMBAT))
                else:
                    # Convert the loser to winner's type and lineage
                    if winner_type == person1.rps_type:
                        # person1 wins, person2 takes person1's type and lineage
                        person2.rps_type = person1.rps_type
                        # Transfer lineage if person1 has one
                        if esper.has_component(entity1, Lineage):
                            lineage1 = esper.component_for_entity(entity1, Lineage)
                            if not esper.has_component(entity2, Lineage):
                                esper.add_component(entity2, Lineage())
                            lineage2 = esper.component_for_entity(entity2, Lineage)
                            lineage2.lineage_id = lineage1.lineage_id
                        elif esper.has_component(entity2, Lineage):
                            # Remove lineage if winner has none
                            esper.remove_component(entity2, Lineage)
                    else:
                        # person2 wins, person1 takes person2's type and lineage
                        person1.rps_type = person2.rps_type
                        # Transfer lineage if person2 has one
                        if esper.has_component(entity2, Lineage):
                            lineage2 = esper.component_for_entity(entity2, Lineage)
                            if not esper.has_component(entity1, Lineage):
                                esper.add_component(entity1, Lineage())
                            lineage1 = esper.component_for_entity(entity1, Lineage)
                            lineage1.lineage_id = lineage2.lineage_id
                        elif esper.has_component(entity1, Lineage):
                            # Remove lineage if winner has none
                            esper.remove_component(entity1, Lineage)


class TravelCompletionSystem(esper.Processor):
    """
    System that completes travel for people who have been on a path for 1 tick.
    Moves them from source to destination room.
    """
    
    def process(self):
        """Complete travel for all people who are traveling."""
        for entity, travel in esper.get_component(Travel):
            person = esper.component_for_entity(entity, Person)
            # Move person to destination
            person.room_id = travel.destination_room_id
            # Remove travel component
            esper.remove_component(entity, Travel)


class RoomSwitchSystem(esper.Processor):
    """
    System that handles people switching rooms.
    Each person has a 10% chance to start traveling to an adjacent room.
    People must be on a path for 1 tick before arriving.
    """
    
    def process(self):
        """Process room switching for all people each tick."""
        # Get all rooms with their adjacent rooms
        room_adjacents = {}
        for entity, room in esper.get_component(Room):
            room_adjacents[room.room_id] = room.adjacent_rooms
        
        # Process each person (only those not already traveling)
        for entity, person in esper.get_component(Person):
            # Skip if already traveling
            if esper.has_component(entity, Travel):
                continue
            
            # 10% chance to start traveling
            if random.random() < 0.10:
                current_room_id = person.room_id
                adjacent_rooms = room_adjacents.get(current_room_id, [])
                
                if adjacent_rooms:
                    # Choose destination and start traveling
                    destination_room_id = random.choice(adjacent_rooms)
                    esper.add_component(entity, Travel(
                        source_room_id=current_room_id,
                        destination_room_id=destination_room_id
                    ))


class ResourceExtractionSystem(esper.Processor):
    """
    System that handles resource extraction by matching pairs.
    When two people of the same type are in the same room, they can extract
    a resource and create a new person of their type (with lineage).
    """
    
    def process(self):
        """Process resource extraction for all rooms each tick."""
        # Get all rooms with their resources
        rooms_data = {}
        for entity, room in esper.get_component(Room):
            rooms_data[room.room_id] = {'entity': entity, 'room': room, 'people': []}
        
        # Group people by room and type (exclude those traveling)
        for entity, person in esper.get_component(Person):
            if not esper.has_component(entity, Travel) and person.room_id in rooms_data:
                rooms_data[person.room_id]['people'].append((entity, person))
        
        # Process each room
        for room_id, room_info in rooms_data.items():
            room = room_info['room']
            people = room_info['people']
            
            if room.resources <= 0:
                continue  # No resources to extract
            
            # Group people by type only (not lineage)
            type_groups = {}
            for entity, person in people:
                rps_type = person.rps_type
                if rps_type not in type_groups:
                    type_groups[rps_type] = []
                type_groups[rps_type].append((entity, person))
            
            # Find matching pairs (same type, any lineage)
            for rps_type, group in type_groups.items():
                if len(group) >= 2 and room.resources > 0:
                    # We have at least one pair of the same type, extract a resource
                    room.resources -= 1
                    
                    # Randomly select two people from this group to extract
                    pair = random.sample(group, min(2, len(group)))
                    
                    # If there are multiple lineages of this type in the room,
                    # randomly pick which lineage the new person will have
                    # Collect all unique lineages from people of this type in the room
                    available_lineages = []
                    for entity, person in group:
                        if esper.has_component(entity, Lineage):
                            lineage = esper.component_for_entity(entity, Lineage)
                            if lineage.lineage_id not in available_lineages:
                                available_lineages.append(lineage.lineage_id)
                        else:
                            # None represents no lineage (base type)
                            if None not in available_lineages:
                                available_lineages.append(None)
                    
                    # Randomly pick a lineage (or None for base type)
                    chosen_lineage_id = random.choice(available_lineages) if available_lineages else None
                    
                    # Find next available person_id
                    max_person_id = -1
                    for e, p in esper.get_component(Person):
                        max_person_id = max(max_person_id, p.person_id)
                    
                    new_person_id = max_person_id + 1
                    
                    # Create new person
                    new_entity = esper.create_entity()
                    esper.add_component(new_entity, Person(
                        person_id=new_person_id,
                        rps_type=rps_type,
                        room_id=room_id
                    ))
                    
                    # Add lineage if chosen
                    if chosen_lineage_id is not None:
                        esper.add_component(new_entity, Lineage(lineage_id=chosen_lineage_id))
                    
                    # Only extract one resource per room per tick
                    break


class ResourceRegenerationSystem(esper.Processor):
    """
    System that regenerates resources in rooms each tick.
    Regenerates 1-2 resources per room, or based on population.
    """
    
    def process(self):
        """Regenerate resources for all rooms each tick."""
        for entity, room in esper.get_component(Room):
            # Regenerate 1-2 resources per tick, or 1 per 10 people (whichever is higher)
            # This creates population-based regeneration
            people_in_room = sum(1 for e, p in esper.get_component(Person) if p.room_id == room.room_id)
            
            # Base regeneration: 1-2 per tick
            base_regeneration = random.randint(1, 2)
            
            # Population-based bonus: 1 per 10 people (capped at 5 additional)
            population_bonus = min(people_in_room // 10, 5)
            
            total_regeneration = base_regeneration + population_bonus
            
            # Don't exceed the initial resource limit (half of max population)
            max_resources = room.population_limit // 2
            room.resources = min(room.resources + total_regeneration, max_resources)
            
            # Update consecutive zero resources counter
            if room.resources == 0:
                room.consecutive_zero_resources += 1
            else:
                room.consecutive_zero_resources = 0


class MortalitySystem(esper.Processor):
    """
    System that handles natural death, starvation, and overcrowding.
    - Natural death: 0.5% base chance per person per tick
    - Starvation: 5% chance if room has 0 resources for 3+ ticks
    - Overcrowding: 2% additional chance if room is over capacity
    """
    
    def process(self):
        """Process mortality for all people each tick."""
        # Get room data
        rooms_data = {}
        for entity, room in esper.get_component(Room):
            rooms_data[room.room_id] = {
                'room': room,
                'people': []
            }
        
        # Group people by room (exclude those traveling)
        for entity, person in esper.get_component(Person):
            if not esper.has_component(entity, Travel) and person.room_id in rooms_data:
                rooms_data[person.room_id]['people'].append(entity)
        
        # Process each room
        for room_id, room_info in rooms_data.items():
            room = room_info['room']
            people_entities = room_info['people']
            current_population = len(people_entities)
            
            # Check each person in the room
            for person_entity in people_entities:
                # Skip if already marked for death
                if esper.has_component(person_entity, DeathMarker):
                    continue
                
                death_chance = 0.0
                death_cause = None
                
                # 1. Natural death: 0.5% base chance
                natural_death_roll = random.random()
                if natural_death_roll < 0.005:
                    death_cause = DeathCause.NATURAL
                
                # 2. Starvation: 5% chance if room has 0 resources for 3+ ticks
                if death_cause is None and room.consecutive_zero_resources >= 3:
                    starvation_roll = random.random()
                    if starvation_roll < 0.05:
                        death_cause = DeathCause.STARVATION
                
                # 3. Overcrowding: 2% additional chance if room is over capacity
                # (This counts as natural death for visualization)
                if death_cause is None and current_population > room.population_limit:
                    overcrowding_roll = random.random()
                    if overcrowding_roll < 0.02:
                        death_cause = DeathCause.NATURAL
                
                # Mark for death if any cause triggered
                if death_cause is not None:
                    esper.add_component(person_entity, DeathMarker(cause=death_cause))


class DeathCleanupSystem(esper.Processor):
    """
    System that removes people marked for death.
    Runs after visualization so they can be shown with X markers for one tick.
    """
    
    def process(self):
        """Delete all entities marked for death."""
        entities_to_delete = []
        for entity, death_marker in esper.get_component(DeathMarker):
            entities_to_delete.append(entity)
        
        for entity in entities_to_delete:
            esper.delete_entity(entity)


class PopulationBalanceSystem(esper.Processor):
    """
    System that balances population when one type becomes dominant.
    If any RPS type exceeds 60% of the population, 30% of that dominant
    population randomly changes to one of the other two types, creating new lineages.
    """
    
    def process(self):
        """Check for dominant population and apply balancing."""
        registry = get_registry()
        
        # Count total population and by base type
        total_count = 0
        type_counts = {RPSType.ROCK: [], RPSType.PAPER: [], RPSType.SCISSORS: []}
        
        for entity, person in esper.get_component(Person):
            total_count += 1
            type_counts[person.rps_type].append(entity)
        
        if total_count == 0:
            return  # No people to balance
        
        # Check each base type for dominance (> 60%)
        for base_type, entity_list in type_counts.items():
            count = len(entity_list)
            percentage = (count / total_count) * 100
            
            if percentage > 60:
                # Dominant type found - convert 30% to one of the other two types
                num_to_convert = int(count * 0.30)
                if num_to_convert == 0:
                    continue  # Need at least 1 person to convert
                
                # Get the other two base types
                other_base_types = [t for t in RPSType if t != base_type]
                
                # Randomly select entities to convert
                entities_to_convert = random.sample(entity_list, min(num_to_convert, len(entity_list)))
                
                # Track conversions for logging
                conversion_counts = {other_base_types[0]: 0, other_base_types[1]: 0}
                lineage_ids_created = {other_base_types[0]: [], other_base_types[1]: []}
                
                # Convert each selected entity to a new lineage
                for entity in entities_to_convert:
                    person = esper.component_for_entity(entity, Person)
                    
                    # Get current lineage ID (if any)
                    current_lineage_id = None
                    if esper.has_component(entity, Lineage):
                        lineage = esper.component_for_entity(entity, Lineage)
                        current_lineage_id = lineage.lineage_id
                    
                    # Choose new base type
                    new_base_type = random.choice(other_base_types)
                    
                    # Create new lineage in registry
                    new_lineage_id = registry.create_lineage(
                        parent_lineage_id=current_lineage_id,
                        original_base_type=base_type,
                        split_to_type=new_base_type
                    )
                    
                    # Update person's type and lineage
                    person.rps_type = new_base_type
                    
                    # Add or update lineage component
                    if not esper.has_component(entity, Lineage):
                        esper.add_component(entity, Lineage(lineage_id=new_lineage_id))
                    else:
                        lineage = esper.component_for_entity(entity, Lineage)
                        lineage.lineage_id = new_lineage_id
                    
                    conversion_counts[new_base_type] += 1
                    lineage_ids_created[new_base_type].append(new_lineage_id)
                
                # Log the balancing event
                lineage_str_0 = registry.get_lineage_string(lineage_ids_created[other_base_types[0]][0]) if lineage_ids_created[other_base_types[0]] else other_base_types[0].value
                lineage_str_1 = registry.get_lineage_string(lineage_ids_created[other_base_types[1]][0]) if lineage_ids_created[other_base_types[1]] else other_base_types[1].value
                
                print(f"  [BALANCE] {base_type.value.capitalize()} was {percentage:.1f}% ({count}/{total_count}). "
                      f"Converted {len(entities_to_convert)} people: "
                      f"{conversion_counts[other_base_types[0]]} to {lineage_str_0}, "
                      f"{conversion_counts[other_base_types[1]]} to {lineage_str_1}")
                break  # Only process one dominant type per tick

