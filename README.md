# Rock-Paper-Scissors Room Simulation

An ECS-based simulation using the esper library where people play Rock-Paper-Scissors in rooms with resource management, travel mechanics, and philosophical belief evolution.

## Overview

This simulation models:
- **10 rooms** arranged in a branching tree structure (each room has population limits)
- **100 people** who are each either Rock, Paper, or Scissors
- **Resource system**: Rooms have resources that can be extracted by matching pairs to create new people
- **Travel system**: People must spend 1 tick on paths between rooms
- Each tick:
  - Resources regenerate (1-2 per room + population bonus)
  - Matching pairs extract resources and create new people
  - People randomly pair up in their room to play RPS
  - Losers have 20% chance of elimination, 80% chance of conversion
  - **Mortality**: Natural death (0.5%), starvation (5% if 0 resources for 3+ ticks), overcrowding (2% if over capacity)
  - People complete travel between rooms
  - 10% chance for each person to start traveling to an adjacent room
  - **Population balancing**: If any type exceeds 60% of the population, 30% of that dominant type randomly converts to one of the other two types
  - **Lineage tracking**: When a population split occurs, new lineages are created in the LineageRegistry that preserve the full split history (e.g., "rock -> paper -> scissors"). Lineages are tracked via unique IDs for infinite scalability - no long concatenated strings!
- Runs for **300 ticks** (configurable)
- **Lineage reports**: Automatically generates text reports (`lineage_report_tick_{tick}.txt`) showing population counts by lineage
- **State serialization**: Optionally saves complete world state to JSON files for analysis
- **Optional XAI API integration**: After simulation, can generate philosophical belief evolution reports showing how beliefs dilute through lineage splits

## Requirements

- Python 3.7+
- esper library
- pygame (optional, for visualization)
- requests (optional, for XAI API belief evolution analysis)
- pytest (optional, for running tests)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Simulation

```bash
python simulation.py
```

You'll be prompted:
1. **Run with visualization? (Y/N)**: Choose whether to see the graphical visualization
2. **Save simulation states to JSON? (Y/N)**: Choose whether to save the world state at each tick to a JSON file
3. **Run XAI API evolution analysis? (Y/N)**: Choose whether to analyze final lineages with AI (prompted after simulation completes)
4. **Use interactive mode? (Y/N)**: If using XAI, choose whether to pause after each API call

### Visualization Features

The graphical visualization shows:
- Rooms arranged in a tree structure
- Grid-based population limits (each cell = 1 person slot)
- Colored people: Brown (Rock), Light Blue (Paper), Gray (Scissors)
- Paths between connected rooms
- Traveling people shown on paths
- Death markers: White X (natural), Black X (starvation), Red X (combat)
- Updates every 0.5 seconds per tick

Close the visualization window or press ESC to exit early.

### XAI API Setup (Optional)

To use the belief evolution analysis:

1. Get your API key from: https://console.x.ai
2. Set it as an environment variable:
   ```bash
   # Windows PowerShell
   $env:XAI_API_KEY="your_key_here"
   
   # Windows CMD
   set XAI_API_KEY=your_key_here
   
   # Linux/Mac
   export XAI_API_KEY="your_key_here"
   ```

   Or edit `xai_evolution.py` and set `XAI_API_KEY` with your actual API key (this file is in .gitignore).

3. Install the package:
   ```bash
   pip install requests
   ```

**Note**: Rate limits may apply depending on your API tier. The code handles rate limits automatically with delays.

The belief evolution reports are saved to the `output_file/` directory:
- `output_file/belief_evolution_report.txt` - Detailed evolution report for each lineage
- `output_file/lineage_beliefs.txt` - Simplified lineage-to-belief mapping

The `output_file` directory will be created automatically if it doesn't exist.

## Architecture

The simulation uses Entity Component System (ECS) architecture:

### Components (`components.py`)
- **Room**: Represents a room with its ID, adjacent rooms, population limit, resources, and depth in the tree
- **Person**: Represents a person with their ID, RPS type (enum: Rock, Paper, or Scissors), and current room
- **Lineage**: Optional component that tracks lineage history via a lineage ID reference
- **Travel**: Component marking a person who is traveling between rooms (will arrive after 1 tick)
- **DeathMarker**: Component marking a person for death (with cause: natural, starvation, or combat)

### Systems (`systems.py`)
Systems run in this order each tick:
1. **DeathCleanupSystem**: Cleans up entities marked for death from the previous tick
2. **ResourceRegenerationSystem**: Regenerates resources in rooms (1-2 base + population bonus)
3. **ResourceExtractionSystem**: Allows matching pairs to extract resources and create new people
4. **RPSGameSystem**: Handles RPS gameplay within rooms (uses base type for gameplay, preserves lineage)
5. **MortalitySystem**: Marks people for natural death, starvation, and overcrowding
6. **TravelCompletionSystem**: Completes travel and moves people to their destination rooms
7. **RoomSwitchSystem**: Handles 10% chance for people to start traveling to adjacent rooms
8. **PopulationBalanceSystem**: Prevents any type from dominating by converting 30% of a dominant type (>60%) to new lineages via the LineageRegistry

### Lineage System (`lineage_registry.py`)
- **LineageRegistry**: Scalable system for tracking population splits using unique IDs instead of long concatenated strings
- Tracks full split history (e.g., "rock -> paper -> scissors") without storing long strings
- Can reconstruct full lineage paths on demand
- Scales infinitely - no matter how many splits occur, each lineage is just an integer ID

### Main Simulation (`simulation.py`)
- Creates the world, rooms, and people
- Runs the simulation loop for 300 ticks (configurable)
- Outputs statistics every 10 ticks
- Generates lineage report files (`output_file/lineage_report_tick_{tick}.txt`) showing population by lineage
- Optionally saves simulation states to JSON (`output_file/simulation_states_tick_{tick}.json`) for analysis

**Note**: All output files (reports, state files) are saved to the `output_file/` directory, which is created automatically if it doesn't exist.

### Serialization (`serialization.py`)
- Provides utilities to serialize and save the entire ECS world state at any tick
- Saves to JSON format for later analysis or replay
- Captures all entities and their components

### Testing
Test files are included for all major components:
- `test_components.py`: Component tests
- `test_systems.py`: System tests
- `test_simulation.py`: Simulation integration tests
- `test_lineage_registry.py`: Lineage registry tests
- `test_serialization.py`: Serialization tests
- `test_integration.py`: End-to-end integration tests

Run tests with: `pytest`

