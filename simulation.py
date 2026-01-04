"""
Main simulation file for the Rock-Paper-Scissors room-based simulation.
"""
import random
import esper
from components import Room, Person, RPSType
from systems import (RPSGameSystem, RoomSwitchSystem, PopulationBalanceSystem, 
                     ResourceExtractionSystem, ResourceRegenerationSystem, MortalitySystem,
                     TravelCompletionSystem, DeathCleanupSystem)
from lineage_registry import get_registry, reset_registry


def create_rooms(num_rooms: int = 10) -> dict[int, int]:
    """
    Create rooms arranged in a branching tree structure with population limits.
    Central room has highest limit, rooms further out have lower limits.
    Returns a dict mapping room_id to entity_id.
    """
    room_entities = {}
    
    # Build tree structure: each room knows its parent and children
    # Room 0 is the center, others branch out
    tree_structure = _build_room_tree(num_rooms)
    
    # Calculate population limits based on depth
    # Center room (depth 0) gets highest limit, decreases with depth
    base_limit = 50  # Base limit for center room
    limit_decrease = 8  # Decrease per depth level
    
    for room_id in range(num_rooms):
        depth = tree_structure[room_id]['depth']
        adjacent_rooms = tree_structure[room_id]['adjacent']
        
        # Calculate population limit: decreases with depth
        population_limit = max(5, base_limit - (depth * limit_decrease))
        
        # Resources start at half of max population
        initial_resources = population_limit // 2
        
        entity = esper.create_entity()
        esper.add_component(entity, Room(
            room_id=room_id,
            adjacent_rooms=adjacent_rooms,
            population_limit=population_limit,
            depth=depth,
            resources=initial_resources,
            consecutive_zero_resources=0
        ))
        room_entities[room_id] = entity
    
    return room_entities


def _build_room_tree(num_rooms: int) -> dict:
    """
    Build a tree structure for rooms.
    Returns a dict mapping room_id to {'depth': int, 'adjacent': [room_ids]}
    """
    tree = {}
    
    if num_rooms == 0:
        return tree
    
    # Room 0 is the center (depth 0)
    tree[0] = {'depth': 0, 'adjacent': []}
    
    if num_rooms == 1:
        return tree
    
    # Build tree level by level
    # Strategy: Each room can have 2-3 children, creating a branching structure
    current_level = [0]  # Start with center room
    next_room_id = 1
    current_depth = 1
    
    while next_room_id < num_rooms and current_level:
        next_level = []
        
        for parent_id in current_level:
            if next_room_id >= num_rooms:
                break
            
            # Determine number of children for this parent (2-3 children)
            remaining_rooms = num_rooms - next_room_id
            if remaining_rooms == 1:
                num_children = 1
            elif remaining_rooms == 2:
                num_children = 2
            else:
                # Randomly choose 2 or 3 children
                num_children = random.choice([2, 3])
                num_children = min(num_children, remaining_rooms)
            
            # Create children
            for _ in range(num_children):
                if next_room_id >= num_rooms:
                    break
                
                child_id = next_room_id
                tree[child_id] = {'depth': current_depth, 'adjacent': [parent_id]}
                
                # Add child to parent's adjacent list
                tree[parent_id]['adjacent'].append(child_id)
                
                next_level.append(child_id)
                next_room_id += 1
        
        current_level = next_level
        current_depth += 1
    
    return tree


def create_people(num_people: int = 100, num_rooms: int = 10):
    """
    Create people with random RPS types and assign them to random rooms.
    People start with base types and no lineage.
    """
    rps_types = [RPSType.ROCK, RPSType.PAPER, RPSType.SCISSORS]
    
    for person_id in range(num_people):
        rps_type = random.choice(rps_types)
        room_id = random.randint(0, num_rooms - 1)
        
        entity = esper.create_entity()
        esper.add_component(entity, Person(
            person_id=person_id,
            rps_type=rps_type,
            room_id=room_id
        ))
        # People start with no lineage (base types)


def get_statistics(num_rooms: int = 10) -> dict:
    """
    Collect statistics about the current state of the simulation.
    """
    from components import Lineage
    
    registry = get_registry()
    
    stats = {
        'total_people': 0,
        'by_base_type': {RPSType.ROCK: 0, RPSType.PAPER: 0, RPSType.SCISSORS: 0},
        'by_lineage_id': {},  # Track counts by lineage ID
        'by_room': {room_id: {'total': 0, 'rock': 0, 'paper': 0, 'scissors': 0} 
                    for room_id in range(num_rooms)}
    }
    
    for entity, person in esper.get_component(Person):
        stats['total_people'] += 1
        
        # Count by base type
        stats['by_base_type'][person.rps_type] += 1
        
        # Count by lineage ID
        lineage_id = None
        if esper.has_component(entity, Lineage):
            lineage = esper.component_for_entity(entity, Lineage)
            lineage_id = lineage.lineage_id
        
        if lineage_id not in stats['by_lineage_id']:
            stats['by_lineage_id'][lineage_id] = 0
        stats['by_lineage_id'][lineage_id] += 1
        
        # Count by room
        room_id = person.room_id
        stats['by_room'][room_id]['total'] += 1
        stats['by_room'][room_id][person.rps_type.value] += 1
    
    return stats


def generate_lineage_report(stats: dict, tick: int):
    """
    Generate a text file report listing all lineages and their populations.
    """
    registry = get_registry()
    from components import Lineage, RPSType
    
    filename = f"lineage_report_tick_{tick}.txt"
    
    with open(filename, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write(f"Lineage Population Report - Tick {tick}\n")
        f.write("=" * 70 + "\n\n")
        
        # Count populations by lineage
        lineage_populations = {}
        base_type_populations = {RPSType.ROCK: 0, RPSType.PAPER: 0, RPSType.SCISSORS: 0}
        
        for entity, person in esper.get_component(Person):
            # Check if person has lineage
            if esper.has_component(entity, Lineage):
                lineage = esper.component_for_entity(entity, Lineage)
                lineage_id = lineage.lineage_id
                
                if lineage_id not in lineage_populations:
                    lineage_populations[lineage_id] = 0
                lineage_populations[lineage_id] += 1
            else:
                # Base type (no lineage)
                base_type_populations[person.rps_type] += 1
        
        # Write base type populations
        f.write("Base Types (No Lineage):\n")
        f.write("-" * 70 + "\n")
        for rps_type in RPSType:
            count = base_type_populations[rps_type]
            if count > 0:
                f.write(f"  {rps_type.value.upper():15} : {count:4} people\n")
        f.write("\n")
        
        # Write lineage populations (group by path string and sum populations)
        if lineage_populations:
            f.write("Lineages:\n")
            f.write("-" * 70 + "\n")
            
            # Group lineages by path string and sum populations
            path_populations = {}
            for lineage_id, count in lineage_populations.items():
                lineage_path = registry.get_lineage_path(lineage_id)
                if lineage_path:
                    lineage_str = " -> ".join(p.upper() for p in lineage_path)
                    if lineage_str not in path_populations:
                        path_populations[lineage_str] = 0
                    path_populations[lineage_str] += count
            
            # Sort by population (descending)
            sorted_paths = sorted(path_populations.items(), key=lambda x: -x[1])
            
            for lineage_str, total_count in sorted_paths:
                f.write(f"  {lineage_str:50} : {total_count:4} people\n")
        else:
            f.write("No lineages created.\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write(f"Total People: {stats['total_people']}\n")
        f.write(f"Unique Lineages: {len(lineage_populations)}\n")
        f.write("=" * 70 + "\n")
    
    print(f"\nLineage report saved to: {filename}")


def print_statistics(stats: dict, tick: int):
    """
    Print formatted statistics for the current tick with improved lineage visualization.
    """
    registry = get_registry()
    
    print(f"\n{'='*65}")
    print(f"  Tick {tick:3}  |  Total: {stats['total_people']:3} people")
    print(f"{'='*65}")
    
    # Base type distribution with visual bars
    rock_count = stats['by_base_type'][RPSType.ROCK]
    paper_count = stats['by_base_type'][RPSType.PAPER]
    scissors_count = stats['by_base_type'][RPSType.SCISSORS]
    total = stats['total_people']
    
    rock_pct = (rock_count / total * 100) if total > 0 else 0
    paper_pct = (paper_count / total * 100) if total > 0 else 0
    scissors_pct = (scissors_count / total * 100) if total > 0 else 0
    
    # Visual bar representation using ASCII characters
    bar_length = 20
    rock_bar = '#' * int(rock_pct / 100 * bar_length)
    paper_bar = '#' * int(paper_pct / 100 * bar_length)
    scissors_bar = '#' * int(scissors_pct / 100 * bar_length)
    
    print(f"\nBase Type Distribution:")
    print(f"   [R] Rock    : {rock_count:3} ({rock_pct:5.1f}%) {rock_bar}")
    print(f"   [P] Paper   : {paper_count:3} ({paper_pct:5.1f}%) {paper_bar}")
    print(f"   [S] Scissors: {scissors_count:3} ({scissors_pct:5.1f}%) {scissors_bar}")
    
    # Count surviving unique lineages (those with current population > 0)
    surviving_lineage_ids = [lid for lid, count in stats['by_lineage_id'].items() 
                             if lid is not None and lid != 0 and count > 0]
    surviving_lineages = len(surviving_lineage_ids)
    
    # Calculate surviving lineage changes
    surviving_changes = 0
    for lineage_id in surviving_lineage_ids:
        path = registry.get_lineage_path(lineage_id)
        if len(path) > 1:
            surviving_changes += len(path) - 1
    
    # Count all unique lineages (all that have ever been created in registry)
    all_lineages = registry.get_all_lineages()
    all_unique_lineages = len(all_lineages)
    
    # Calculate all lineage changes (across all lineages ever created)
    all_changes = 0
    for lineage_id in all_lineages.keys():
        path = registry.get_lineage_path(lineage_id)
        if len(path) > 1:
            all_changes += len(path) - 1
    
    print(f"\nLineage Information:")
    print(f"   All Unique Lineages: {all_unique_lineages}")
    print(f"   All Lineage Changes: {all_changes}")
    print(f"   Surviving Unique Lineages: {surviving_lineages}")
    print(f"   Surviving Lineage Changes: {surviving_changes}")
    
    # Room distribution with limits
    print(f"\nRoom Distribution (showing current/max, depth):")
    for room_id in range(len(stats['by_room'])):
        room_stats = stats['by_room'][room_id]
        
        # Get room info (limit, depth, and resources)
        room_limit = 0
        room_depth = 0
        room_resources = 0
        for entity, room in esper.get_component(Room):
            if room.room_id == room_id:
                room_limit = room.population_limit
                room_depth = room.depth
                room_resources = room.resources
                break
        
        # Create a small visual representation for room distribution
        room_total = room_stats['total']
        if room_total > 0:
            # Use letters for visual representation
            visual = ('R' * room_stats['rock'] + 
                     'P' * room_stats['paper'] + 
                     'S' * room_stats['scissors'])[:15]  # Limit length
        else:
            visual = "(empty)"
        
        # Show if at/over limit
        limit_indicator = ""
        if room_total >= room_limit:
            limit_indicator = " [FULL]"
        elif room_total > room_limit * 0.8:
            limit_indicator = " [~FULL]"
        
        print(f"   Room {room_id:2} (d{room_depth}): {room_stats['total']:2}/{room_limit:2} people "
              f"(R:{room_stats['rock']:2} P:{room_stats['paper']:2} S:{room_stats['scissors']:2}) "
              f"Resources: {room_resources:2}{limit_indicator} [{visual}]")


def run_simulation(num_rooms: int = 10, num_people: int = 100, num_ticks: int = 100, 
                   use_graphics: bool = False):
    """
    Run the complete simulation.
    
    Args:
        num_rooms: Number of rooms in the simulation
        num_people: Number of people in the simulation
        num_ticks: Number of ticks to run
        use_graphics: Whether to show graphical visualization
    """
    # Clear any existing entities/components and reset lineage registry
    esper.clear_database()
    reset_registry()
    
    # Create rooms
    print("Creating rooms...")
    create_rooms(num_rooms)
    
    # Create people
    print(f"Creating {num_people} people...")
    create_people(num_people, num_rooms)
    
    # Register systems (order matters)
    # DeathCleanupSystem runs FIRST to clean up deaths from previous tick
    esper.add_processor(DeathCleanupSystem())           # First: clean up deaths from previous tick
    esper.add_processor(ResourceRegenerationSystem())  # Then: regenerate resources
    esper.add_processor(ResourceExtractionSystem())    # Then: extract resources
    esper.add_processor(RPSGameSystem())                # Then: play games (marks combat deaths)
    esper.add_processor(MortalitySystem())              # Then: mark natural/starvation deaths
    esper.add_processor(TravelCompletionSystem())      # Complete travel (people MUST leave roads immediately)
    esper.add_processor(RoomSwitchSystem())              # Then: start new travel
    esper.add_processor(PopulationBalanceSystem())      # Finally: balance population
    
    # Initialize visualizer if requested
    visualizer = None
    if use_graphics:
        try:
            from visualization import SimulationVisualizer
            visualizer = SimulationVisualizer()
            print("Graphical visualization enabled. Close window or press ESC to exit.")
        except ImportError:
            print("Warning: pygame not available. Running without graphics.")
            use_graphics = False
    
    # Print initial state
    initial_stats = get_statistics(num_rooms)
    print_statistics(initial_stats, 0)
    
    # Show initial visualization
    if visualizer:
        if not visualizer.visualize_tick(0, num_rooms):
            visualizer.close()
            return
        import time
        time.sleep(0.5)  # Half second delay
    
    # Run simulation
    print(f"\nRunning simulation for {num_ticks} ticks...")
    import time
    
    for tick in range(1, num_ticks + 1):
        # Process all systems (this runs RPS games and room switching)
        esper.process()
        
        # Update visualization every tick (0.5 seconds per tick)
        # Visualization shows deaths marked this tick (they'll be cleaned up next tick)
        if visualizer:
            if not visualizer.visualize_tick(tick, num_rooms):
                # User closed window
                break
            time.sleep(0.5)  # Half second between ticks
        
        # Print statistics every 10 ticks or on the last tick
        if tick % 10 == 0 or tick == num_ticks:
            stats = get_statistics(num_rooms)
            print_statistics(stats, tick)
    
    # Final statistics
    print("\n=== Final Statistics ===")
    final_stats = get_statistics(num_rooms)
    print_statistics(final_stats, num_ticks)
    
    # Generate lineage report file
    generate_lineage_report(final_stats, num_ticks)
    
    # Ask if user wants to run Gemini evolution analysis
    run_gemini = input("\nRun Gemini API evolution analysis on final state? (Y/N): ").strip().upper() == 'Y'
    if run_gemini:
        # Ask if user wants interactive mode for debugging
        interactive_mode = input("Use interactive mode (pause after each API call for debugging)? (Y/N): ").strip().upper() == 'Y'
        try:
            from gemini_evolution import run_gemini_evolution
            run_gemini_evolution(num_rooms, interactive=interactive_mode)
        except ImportError:
            print("\nWarning: gemini_evolution module not found or dependencies missing.")
            print("Make sure google-generativeai is installed: pip install google-generativeai")
        except Exception as e:
            print(f"\nError running Gemini evolution analysis: {e}")
    
    # Close visualization if open
    if visualizer:
        print("\nVisualization window will close in 3 seconds...")
        import pygame
        for _ in range(30):  # 3 seconds at ~10 checks per second
            visualizer.clock.tick(10)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    visualizer.close()
                    return
            time.sleep(0.1)
        visualizer.close()


if __name__ == "__main__":
    # Set random seed for reproducibility (optional)
    # random.seed(42)
    
    # Ask user if they want visualization
    use_viz = input("Run with visualization? (Y/N): ").strip().upper() == 'Y'
    
    run_simulation(num_rooms=10, num_people=100, num_ticks=100, use_graphics=use_viz)

