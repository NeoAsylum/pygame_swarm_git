# pygame_swarm_git/swarm_retro/SpatialGridClass.py

class SpatialGrid:
    def __init__(self, width, height, cell_size=100):
        self.cell_size = cell_size
        self.grid_width = int(width // self.cell_size) + 1
        self.grid_height = int(height // self.cell_size) + 1
        self.grid = {}

    def _get_cell(self, x, y):
        cell_x = max(0, min(int(x // self.cell_size), self.grid_width - 1))
        cell_y = max(0, min(int(y // self.cell_size), self.grid_height - 1))
        return (cell_x, cell_y)

    def add_bird(self, bird):
        cell = self._get_cell(bird.x, bird.y) 
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(bird)

    def clear(self):
        self.grid = {}

    def get_nearby_birds(self, bird):
        center_cell_x, center_cell_y = self._get_cell(bird.x, bird.y)
        nearby_birds = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                cell_to_check = (center_cell_x + dx, center_cell_y + dy)
                if 0 <= cell_to_check[0] < self.grid_width and \
                   0 <= cell_to_check[1] < self.grid_height:
                    if cell_to_check in self.grid:
                        nearby_birds.extend(self.grid[cell_to_check])
        return nearby_birds