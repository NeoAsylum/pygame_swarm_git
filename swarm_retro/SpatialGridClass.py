class SpatialGrid:
    def __init__(self, width, height, cell_size=100):
        self.cell_size = cell_size
        self.grid = {}  # Dictionary mapping grid coordinates to birds
        self.width = width
        self.height = height

    def _get_cell(self, x, y):
        """Compute the cell coordinates for a given position."""
        return (int(x // self.cell_size), int(y // self.cell_size))

    def add_bird(self, bird):
        """Add a bird to the spatial grid."""
        cell = self._get_cell(bird.x, bird.y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(bird)

    def clear(self):
        """Clear the grid before each frame update."""
        self.grid = {}

    def get_nearby_birds(self, bird):
        """Fetch birds in nearby grid cells to reduce neighbor search complexity."""
        x, y = self._get_cell(bird.x, bird.y)
        nearby_birds = []
        for dx in [-1, 0, 1]:  # Check neighboring cells
            for dy in [-1, 0, 1]:
                cell = (x + dx, y + dy)
                if cell in self.grid:
                    nearby_birds.extend(self.grid[cell])
        return nearby_birds
