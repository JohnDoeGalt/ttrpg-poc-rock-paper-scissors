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
- **Optional Gemini API integration**: After simulation, can generate philosophical belief evolution reports showing how beliefs dilute through lineage splits

## Requirements

- Python 3.7+
- esper library
- pygame (optional, for visualization)
- google-generativeai (optional, for belief evolution analysis)

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
2. **Run Gemini API evolution analysis? (Y/N)**: Choose whether to analyze final lineages with AI
3. **Use interactive mode? (Y/N)**: If using Gemini, choose whether to pause after each API call

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

### Gemini API Setup (Optional)

To use the belief evolution analysis:

1. Get your API key from: https://makersuite.google.com/app/apikey
2. Set it as an environment variable:
   ```bash
   # Windows PowerShell
   $env:GEMINI_API_KEY="your_key_here"
   
   # Windows CMD
   set GEMINI_API_KEY=your_key_here
   
   # Linux/Mac
   export GEMINI_API_KEY="your_key_here"
   ```

   Or edit `gemini_evolution.py` and replace the empty string with your key (this file is in .gitignore).

3. Install the package:
   ```bash
   pip install google-generativeai
   ```

**Note**: Free tier has rate limits (5 requests/minute). The code handles this automatically with delays.

## Architecture

The simulation uses Entity Component System (ECS) architecture:

### Components (`components.py`)
- **Room**: Represents a room with its ID and adjacent rooms
- **Person**: Represents a person with their ID, RPS type (enum: Rock, Paper, or Scissors), and current room
- **Lineage**: Optional component that tracks lineage history via a lineage ID reference

### Systems (`systems.py`)
- **RPSGameSystem**: Handles RPS gameplay within rooms each tick (uses base type for gameplay, preserves lineage)
- **RoomSwitchSystem**: Handles 10% chance room switching each tick
- **PopulationBalanceSystem**: Prevents any single type from dominating by converting 30% of a dominant type (>60%) to new lineages via the LineageRegistry

### Lineage System (`lineage_registry.py`)
- **LineageRegistry**: Scalable system for tracking population splits using unique IDs instead of long concatenated strings
- Tracks full split history (e.g., "rock -> paper -> scissors") without storing long strings
- Can reconstruct full lineage paths on demand
- Scales infinitely - no matter how many splits occur, each lineage is just an integer ID

### Main Simulation (`simulation.py`)
- Creates the world, rooms, and people
- Runs the simulation loop for 100 ticks
- Outputs statistics every 10 ticks

