#!/usr/local/bin/python3

import json

class Board:
    def __init__(self, coordinates: set[tuple[int,int]]|list[tuple[int,int]], max_iterations: int = 1000, is_finished=False):
        ''' Initialize the board with a list of live cell coordinates.
            Coordinates should be a list of (row, col) tuples.
        '''     
        self.is_finished = is_finished

        if not isinstance(coordinates, set) and not isinstance(coordinates, list):
            raise ValueError("Coordinates must be a set or list of (row, col) tuples")

        self._coords = set()
        
        for coord in coordinates:
            x, y = coord
            self._coords.add((x, y))

        self._max_iterations = max_iterations
        if not self._coords:
            self.is_finished = True

    def to_dense(self) -> list[list[int]]:
        ''' Convert the board to a dense 2D list representation. 
            This is not currently used but could easily be exposed with a new endpoint.
        '''
        if not self._coords:
            return [[]]

        min_x, min_y, max_x, max_y = self._find_min_max()
        grid = [[0 for _ in range(min_y, max_y + 1)] for _ in range(min_x, max_x + 1)]
        for r, c in self._coords:
            grid[r][c] = 1
        return grid

    def to_dict(self) -> dict:
        ''' Convert the board to a sparse dictionary representation. '''
        return {
            "coordinates": self._coords,
            "is_finished": self.is_finished
        }

    def to_string(self) -> str:
        ''' Serialize the board to a string representation. '''
        data = {
            "coordinates": list(self._coords),
            "is_finished": self.is_finished
        }
        return json.dumps(data)
    
    def run_iterations(self, iterations: int) -> bool:
        ''' Run the board for a given number of iterations.
            Returns True if all iterations were completed, False if the board
            reached a finished state before completing all iterations.
        '''
        if iterations < 0:
            raise ValueError("Iterations must be non-negative")
        
        if iterations > self._max_iterations:
            raise ValueError(f"Iterations exceed maximum allowed of {self._max_iterations}")

        while iterations > 0:
            if self._iterate():
                return False
            iterations -= 1
        return True

    def _iterate(self) -> bool:
        ''' Perform a single iteration of the Game of Life.
            Returns True if the board has reached a finished state, False otherwise.
        '''
        if self.is_finished:
            return True

        neighbors = {}

        # count neighbors for each live cell
        for coord in self._coords:
            x, y = coord
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (x + dx, y + dy)
                    neighbors[neighbor] = neighbors.get(neighbor, 0) + 1

        # apply the Game of Life rules:
        # Any live cell with fewer than two live neighbours dies, as if by underpopulation.
        # Any live cell with two or three live neighbours lives on to the next generation.
        # Any live cell with more than three live neighbours dies, as if by overpopulation.
        # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
        new_coords = set()
        for position, count in neighbors.items():
            if position in self._coords:
                # live cells
                if count == 2 or count == 3:
                    new_coords.add(position)
            else:
                # dead cells
                if count == 3:
                    new_coords.add(position)

        # if no changes, board is finished
        if self._coords == new_coords:
            self.is_finished = True
            return True
        
        self._coords = new_coords
        
        # if no live cells remain, board is finished
        if not self._coords:
            self.is_finished = True
            return True
        
        return False

    def _find_min_max(self) -> tuple[int, int, int, int]:
        ''' Recalculate the min and max x and y values based on current coordinates. '''
        if not self._coords:
            min_x = 0
            min_y = 0
            max_x = 0
            max_y = 0
            return min_x, min_y, max_x, max_y

        xs, ys = zip(*self._coords)
        min_x = min(xs)
        max_x = max(xs)
        min_y = min(ys)
        max_y = max(ys)

        return min_x, min_y, max_x, max_y
