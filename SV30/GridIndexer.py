import math

min_lat = 33.120581  # Minimum latitude value
max_lat = 38.726809  # Maximum latitude value
min_lon = 124.896901  # Minimum longitude value
max_lon = 132.058734  # Maximum longitude value
cell_size = 0.001  # Cell size in degrees

class GridIndexer:
    def __init__(self, min_lat, max_lat, min_lon, max_lon, cell_size):
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.cell_size = cell_size
        self.num_cols = int(math.ceil((max_lon - min_lon) / cell_size))  # col_size
        self.num_rows = int(math.ceil((max_lat - min_lat) / cell_size))  # row_size
        self.grid = [[None] * self.num_cols for _ in range(self.num_rows)]  # grid_size
        self.populate_grid()

    def populate_grid(self):
        index = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.grid[row][col] = index
                index += 1

    def get_index(self, lat, lon):
        col = int((lon - self.min_lon) / self.cell_size)
        row = int((lat - self.min_lat) / self.cell_size)
        return self.grid[row][col] + 1

    def get_M_coord(self, index):
        row = (index - 1) // self.num_cols
        col = (index - 1) % self.num_cols
        median_lat = self.min_lat + (row + 0.5) * self.cell_size
        median_lon = self.min_lon + (col + 0.5) * self.cell_size
        return round(median_lat, 6), round(median_lon, 6)
