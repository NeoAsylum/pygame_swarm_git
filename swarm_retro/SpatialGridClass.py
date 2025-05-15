# pygame_swarm_git/swarm_retro/SpatialGridClass.py

class SpatialGrid:
    def __init__(self, width, height, cell_size=100): # Default cell_size
        self.cell_size = cell_size
        self.grid_width = int(width // self.cell_size) + 1
        self.grid_height = int(height // self.cell_size) + 1
        self.grid = {}  # Dictionary mapping grid cell tuples to lists of birds

    def _get_cell(self, x, y):
        """Compute the cell coordinates for a given position."""
        # Ensure coordinates are within grid boundaries if birds can go slightly off-screen before wrapping
        cell_x = max(0, min(int(x // self.cell_size), self.grid_width - 1))
        cell_y = max(0, min(int(y // self.cell_size), self.grid_height - 1))
        return (cell_x, cell_y)

    def add_bird(self, bird):
        """Add a bird to the spatial grid."""
        # bird.x and bird.y are the bird's current position
        cell = self._get_cell(bird.x, bird.y) 
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(bird)

    def clear(self):
        """Clear the grid before each frame update."""
        self.grid = {} # More efficient to reassign than to clear each list

    def get_nearby_birds(self, bird):
        """Fetch birds in the bird's current cell and its 8 neighbors."""
        center_cell_x, center_cell_y = self._get_cell(bird.x, bird.y)
        nearby_birds = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # Calculate neighbor cell coordinates
                # No need to check bounds here if _get_cell handles it,
                # but good for robustness if cells can be outside world
                # due to bird position being slightly outside before wrapping.
                # However, _get_cell should map any position to a valid cell index.
                cell_to_check = (center_cell_x + dx, center_cell_y + dy)
                
                # Check if the cell coordinates are valid (e.g. not negative, within grid dimensions)
                # This check is important if _get_cell doesn't clamp to grid boundaries strictly for all inputs.
                # (though the current _get_cell *does* clamp)
                if 0 <= cell_to_check[0] < self.grid_width and \
                   0 <= cell_to_check[1] < self.grid_height:
                    if cell_to_check in self.grid:
                        nearby_birds.extend(self.grid[cell_to_check])
        return nearby_birds