"""
Graphical visualization of the RPS simulation.
Shows rooms as boxes with grid slots, people as colored dots.
"""
import pygame
import math
from typing import Dict, List
from components import Person, Room, RPSType, Travel, DeathMarker, DeathCause
import esper


class SimulationVisualizer:
    """Handles graphical visualization of the simulation."""
    
    def __init__(self, width: int = 1200, height: int = 800):
        """Initialize the visualization window."""
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("RPS Simulation Visualization")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Colors for RPS types
        self.colors = {
            RPSType.ROCK: (139, 69, 19),      # Brown
            RPSType.PAPER: (200, 200, 255),   # Light blue (was white, changed for visibility)
            RPSType.SCISSORS: (192, 192, 192) # Silver/Gray
        }
        
        # Grid parameters
        self.grid_cell_size = 12
        self.grid_spacing = 2
        
    def draw_room_with_grid(self, x: int, y: int, room: Room, people: List[Person]):
        """
        Draw a room as a box with a grid showing population limit.
        People are placed in grid slots.
        """
        # Calculate grid dimensions based on population limit
        # Try to make a roughly square grid
        limit = room.population_limit
        cols = int(math.ceil(math.sqrt(limit)))
        rows = int(math.ceil(limit / cols))
        
        # Room box size
        box_width = cols * (self.grid_cell_size + self.grid_spacing) + self.grid_spacing * 2
        box_height = rows * (self.grid_cell_size + self.grid_spacing) + self.grid_spacing * 2 + 25  # Extra for room label
        
        # Draw room box (black border)
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (x, y, box_width, box_height), 2)
        
        # Draw room label
        room_text = self.font.render(f"R{room.room_id} (d{room.depth})", True, (0, 0, 0))
        self.screen.blit(room_text, (x + 5, y + 2))
        
        # Draw population count
        count_text = self.small_font.render(f"{len(people)}/{limit}", True, (0, 0, 0))
        self.screen.blit(count_text, (x + box_width - 40, y + 2))
        
        # Draw grid and place people
        grid_start_x = x + self.grid_spacing
        grid_start_y = y + 25  # Below label
        
        person_index = 0
        for row in range(rows):
            for col in range(cols):
                if person_index >= limit:
                    break
                
                cell_x = grid_start_x + col * (self.grid_cell_size + self.grid_spacing)
                cell_y = grid_start_y + row * (self.grid_cell_size + self.grid_spacing)
                
                # Draw grid cell (light gray background)
                pygame.draw.rect(self.screen, (240, 240, 240),
                               (cell_x, cell_y, self.grid_cell_size, self.grid_cell_size), 1)
                
                # Place person if available
                if person_index < len(people):
                    person = people[person_index]
                    color = self.colors.get(person.rps_type, (0, 0, 0))
                    
                    # Draw person as filled circle
                    center_x = cell_x + self.grid_cell_size // 2
                    center_y = cell_y + self.grid_cell_size // 2
                    pygame.draw.circle(self.screen, color, 
                                      (center_x, center_y), 
                                      self.grid_cell_size // 2 - 1)
                    
                    # Draw label (R/P/S)
                    label = "R" if person.rps_type == RPSType.ROCK else \
                           "P" if person.rps_type == RPSType.PAPER else "S"
                    # Use black text for all types (readable on colored backgrounds)
                    label_text = self.small_font.render(label, True, (0, 0, 0))
                    label_rect = label_text.get_rect(center=(center_x, center_y))
                    self.screen.blit(label_text, label_rect)
                
                person_index += 1
    
    def visualize_tick(self, tick: int, num_rooms: int = 10):
        """Draw the current state of the simulation."""
        # Clear screen with white background
        self.screen.fill((255, 255, 255))
        
        # Get all rooms and their positions
        rooms_data = []
        for entity, room in esper.get_component(Room):
            rooms_data.append((room, entity))
        
        # Sort by depth, then by room_id for consistent layout
        rooms_data.sort(key=lambda x: (x[0].depth, x[0].room_id))
        
        # Group people by room (with entity references for death markers)
        people_by_room: Dict[int, List[tuple]] = {i: [] for i in range(num_rooms)}
        for entity, person in esper.get_component(Person):
            # Only count people who are not traveling
            if not esper.has_component(entity, Travel):
                people_by_room[person.room_id].append((entity, person))
        
        # Layout rooms in a tree-like structure
        # Center room at top, then branch down
        start_x = 50
        start_y = 80
        room_spacing_x = 120
        room_spacing_y = 150
        
        # Group rooms by depth
        rooms_by_depth = {}
        for room, entity in rooms_data:
            if room.depth not in rooms_by_depth:
                rooms_by_depth[room.depth] = []
            rooms_by_depth[room.depth].append((room, entity))
        
        # Calculate room positions first
        room_positions = {}  # room_id -> (x, y)
        for depth in sorted(rooms_by_depth.keys()):
            rooms_at_depth = rooms_by_depth[depth]
            num_at_depth = len(rooms_at_depth)
            
            # Center rooms at this depth
            total_width = num_at_depth * room_spacing_x
            start_x_depth = (self.width - total_width) // 2
            
            for i, (room, entity) in enumerate(rooms_at_depth):
                x = start_x_depth + i * room_spacing_x
                y = start_y + depth * room_spacing_y
                room_positions[room.room_id] = (x, y)
        
        # Store entity-to-person mapping for death markers
        entity_to_person = {}
        for entity, person in esper.get_component(Person):
            entity_to_person[entity] = person
        
        # Draw paths between connected rooms (before drawing rooms)
        for room, entity in rooms_data:
            source_pos = room_positions[room.room_id]
            for adjacent_room_id in room.adjacent_rooms:
                if adjacent_room_id in room_positions:
                    dest_pos = room_positions[adjacent_room_id]
                    # Draw line between rooms (light gray)
                    pygame.draw.line(self.screen, (200, 200, 200), 
                                   (source_pos[0] + 60, source_pos[1] + 15), 
                                   (dest_pos[0] + 60, dest_pos[1] + 15), 2)
        
        # Draw traveling people on paths
        for entity, travel in esper.get_component(Travel):
            if travel.source_room_id in room_positions and travel.destination_room_id in room_positions:
                source_pos = room_positions[travel.source_room_id]
                dest_pos = room_positions[travel.destination_room_id]
                
                # Calculate midpoint of path (person is halfway there)
                mid_x = (source_pos[0] + dest_pos[0]) // 2 + 60
                mid_y = (source_pos[1] + dest_pos[1]) // 2 + 15
                
                # Get person's type for color
                person = esper.component_for_entity(entity, Person)
                color = self.colors.get(person.rps_type, (0, 0, 0))
                
                # Draw traveling person as a circle on the path
                pygame.draw.circle(self.screen, color, (mid_x, mid_y), 8)
                pygame.draw.circle(self.screen, (0, 0, 0), (mid_x, mid_y), 8, 1)
                
                # Draw label
                label = "R" if person.rps_type == RPSType.ROCK else \
                       "P" if person.rps_type == RPSType.PAPER else "S"
                label_text = self.small_font.render(label, True, (0, 0, 0))
                label_rect = label_text.get_rect(center=(mid_x, mid_y))
                self.screen.blit(label_text, label_rect)
        
        # Draw rooms by depth level (on top of paths)
        for depth in sorted(rooms_by_depth.keys()):
            rooms_at_depth = rooms_by_depth[depth]
            
            for room, entity in rooms_at_depth:
                x, y = room_positions[room.room_id]
                people_data = people_by_room[room.room_id]
                # Extract just Person objects for drawing
                people = [p for _, p in people_data]
                self.draw_room_with_grid(x, y, room, people)
                
                # Draw death markers on people
                for person_entity, person in people_data:
                    if esper.has_component(person_entity, DeathMarker):
                        death_marker = esper.component_for_entity(person_entity, DeathMarker)
                        # Find person's position in grid
                        people_list = [p for _, p in people_data]
                        if person in people_list:
                            person_index = people_list.index(person)
                            # Calculate grid position
                            limit = room.population_limit
                            cols = int(math.ceil(math.sqrt(limit)))
                            rows = int(math.ceil(limit / cols))
                            
                            row = person_index // cols
                            col = person_index % cols
                            
                            cell_x = x + self.grid_spacing + col * (self.grid_cell_size + self.grid_spacing)
                            cell_y = y + 25 + self.grid_spacing + row * (self.grid_cell_size + self.grid_spacing)
                            
                            center_x = cell_x + self.grid_cell_size // 2
                            center_y = cell_y + self.grid_cell_size // 2
                            
                            # Draw X based on death cause
                            if death_marker.cause == DeathCause.NATURAL:
                                x_color = (255, 255, 255)  # White
                            elif death_marker.cause == DeathCause.STARVATION:
                                x_color = (0, 0, 0)  # Black
                            else:  # COMBAT
                                x_color = (255, 0, 0)  # Red
                            
                            # Draw X
                            x_size = self.grid_cell_size // 2
                            pygame.draw.line(self.screen, x_color, 
                                           (center_x - x_size, center_y - x_size),
                                           (center_x + x_size, center_y + x_size), 2)
                            pygame.draw.line(self.screen, x_color, 
                                           (center_x - x_size, center_y + x_size),
                                           (center_x + x_size, center_y - x_size), 2)
        
        # Draw tick information and statistics
        tick_text = self.font.render(f"Tick: {tick}", True, (0, 0, 0))
        self.screen.blit(tick_text, (10, 10))
        
        # Get statistics
        total = 0
        rock_count = 0
        paper_count = 0
        scissors_count = 0
        
        for entity, person in esper.get_component(Person):
            total += 1
            if person.rps_type == RPSType.ROCK:
                rock_count += 1
            elif person.rps_type == RPSType.PAPER:
                paper_count += 1
            else:
                scissors_count += 1
        
        # Draw statistics with color indicators
        stats_y = 35
        stats_text = self.small_font.render(
            f"Total: {total}  ",
            True, (0, 0, 0)
        )
        self.screen.blit(stats_text, (10, stats_y))
        
        # Draw colored indicators for each type
        indicator_x = 100
        indicator_size = 12
        pygame.draw.circle(self.screen, self.colors[RPSType.ROCK], 
                         (indicator_x, stats_y + indicator_size // 2), indicator_size // 2)
        self.screen.blit(self.small_font.render(f"R:{rock_count}", True, (0, 0, 0)), 
                        (indicator_x + 10, stats_y))
        
        indicator_x += 70
        pygame.draw.circle(self.screen, self.colors[RPSType.PAPER], 
                         (indicator_x, stats_y + indicator_size // 2), indicator_size // 2)
        pygame.draw.circle(self.screen, (0, 0, 0), 
                         (indicator_x, stats_y + indicator_size // 2), indicator_size // 2, 1)
        self.screen.blit(self.small_font.render(f"P:{paper_count}", True, (0, 0, 0)), 
                        (indicator_x + 10, stats_y))
        
        indicator_x += 70
        pygame.draw.circle(self.screen, self.colors[RPSType.SCISSORS], 
                         (indicator_x, stats_y + indicator_size // 2), indicator_size // 2)
        self.screen.blit(self.small_font.render(f"S:{scissors_count}", True, (0, 0, 0)), 
                        (indicator_x + 10, stats_y))
        
        # Update display
        pygame.display.flip()
        
        # Handle events (allow window to be closed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def close(self):
        """Close the visualization window."""
        pygame.quit()
