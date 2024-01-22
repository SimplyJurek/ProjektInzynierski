from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List
from typing import Tuple
import random
import Global as G

import pygame


@dataclass
class HexagonTile:
    """Hexagon class"""
    radius: float
    position: Tuple[float, float]
    colour: Tuple[int, ...] = (0, 120, 0)
    state: int = 0
    nextstate: int = 0
    neighbours_dict: dict = None
    cellHumidity: float = 0
    cellDensity: float = 0
    cellDuff: float = 0 
    cellHealth: float = 0
    cellResistance: float = 0

    def __post_init__(self):
        self.vertices = self.compute_vertices()

    def change_state(self, hexlist):
        """Calculates whether the state of the cell should change in the next iteration. If yes, changes the nextstate value."""
        if self.state == 0:
            neighbour_state_counter = sum(1 for neighbour in self.neighbours_dict.values() if neighbour is not None and neighbour.state == 2)
            wind_blowing_towards_me = self.is_neighbourXwind_on_fire()
            if neighbour_state_counter >= 2:
                if wind_blowing_towards_me:
                    self.cellHumidity -= 1 * G.wind_strength
                else:
                    self.cellHumidity -= 1
                cellResistance = (
                    self.cellHumidity
                    )
                if cellResistance <= 0:
                    self.nextstate = 2
        if self.state == 2:
            self.cellDensity -= 0.25
            self.cellDuff -= 1
            cellHealth = (
                self.cellDensity + 
                self.cellDuff
                )
            if cellHealth <= 0:
                self.nextstate = 3
        
    def update(self):
        """Updates the Cell's state based on it's current nextstate value."""
        if self.nextstate > self.state:
            self.state = self.nextstate
            if self.state == 0:
                self.colour = [0, 120, 0]
            elif self.state == 2:
                self.colour = [120, 0, 0]
            else:
                self.colour = [100, 100, 100]

    def compute_vertices(self) -> List[Tuple[float, float]]:
        """Returns a list of the hexagon's vertices as x, y tuples"""
        x, y = self.position
        half_radius = self.radius / 2
        minimal_radius = self.minimal_radius
        return [
            (x, y),
            (x - minimal_radius, y + half_radius),
            (x - minimal_radius, y + 3 * half_radius),
            (x, y + 2 * self.radius),
            (x + minimal_radius, y + 3 * half_radius),
            (x + minimal_radius, y + half_radius),
        ]
        
    def is_neighbourXwind_on_fire(self):
        """
        Checks if the neighbour which is on fire is on the same side that the wind is blowing from.
        """
        if G.wind_strength != 0.0:
            # Adjust the cell resistance based on wind influence
            wind_directions_on_fire = [position for position, neighbour in self.neighbours_dict.items() if neighbour is not None and neighbour.state == 2]
            # If the wind direction matches any neighbouring cell on fire, return True
            if G.wind_direction in wind_directions_on_fire:
                return True
        return False

        return 0.0  # No wind influence in this case
        
    def relative_position_flat_top(self, other_hexagon: HexagonTile) -> str:
        """
        Returns the relative position of the given hexagon with respect to the current flat-top hexagon.
        Possible values: 'top_left', 'bottom_left', 'top_right', 'bottom_right', 'top', 'bottom'
        """
        x1, y1 = self.position
        x2, y2 = other_hexagon.position

        if x2 < x1 - self.radius:
            if y2 < y1:
                return 'top_left'
            elif y2 > y1:
                return 'bottom_left'
        elif x2 > x1 + self.radius:
            if y2 < y1:
                return 'top_right'
            elif y2 > y1:
                return 'bottom_right'
        else:
            if y2 < y1:
                return 'top'
            elif y2 > y1:
                return 'bottom'

        # If the hexagons are at the same position
        return 'same_position'
    
    def relative_position_pointy_top(self, other_hexagon: HexagonTile) -> str:
        """
        Returns the relative position of the given hexagon with respect to the current pointy-top hexagon.
        Possible values: 'top_left', 'top_right', 'left', 'right', 'bottom_left', 'bottom_right'
        """
        x1, y1 = self.position
        x2, y2 = other_hexagon.position

        if y2 < y1 - self.radius:
            if x2 < x1:
                return 'top_left'
            elif x2 > x1:
                return 'top_right'
        elif y2 > y1 + self.radius:
            if x2 < x1:
                return 'bottom_left'
            elif x2 > x1:
                return 'bottom_right'
        else:
            if x2 < x1:
                return 'left'
            elif x2 > x1:
                return 'right'

        # If the hexagons are at the same position
        return 'same_position'


    def compute_neighbours(self, hexagons: List[HexagonTile]) -> None:
        """Fills the neighbours_dict with valid neighbors."""
        if G.grid_orientation:
            keys = ['top_left', 'top_right', 'top', 'bottom', 'bottom_left', 'bottom_right']
        else:
            keys = ['top_left', 'top_right', 'left', 'right', 'bottom_left', 'bottom_right']

        self.neighbours_dict = {key: None for key in keys}

        for hexagon in hexagons:
            if self.is_neighbour(hexagon):
                if G.grid_orientation:
                    relative_position = self.relative_position_flat_top(hexagon)
                else:
                    relative_position = self.relative_position_pointy_top(hexagon)

                self.neighbours_dict[relative_position] = hexagon
        

        

    def collide_with_point(self, point: Tuple[float, float]) -> bool:
        """Returns True if distance from centre to point is less than horizontal_length"""
        return math.dist(point, self.apply_camera_offset(self.centre)) < self.minimal_radius

    def is_neighbour(self, hexagon: HexagonTile) -> bool:
        """Returns True if hexagon centre is approximately
        2 minimal radiuses away from own centre
        """
        distance = math.dist(hexagon.centre, self.centre)
        return math.isclose(distance, 2 * self.minimal_radius, rel_tol=0.05)
    
    def apply_camera_offset(self, coords: Tuple) -> Tuple:
        """applies camera shift to hexagon objects and their hitboxes"""
        if len(coords) > 2:
            return [
                ((x - G.SCREEN_CENTER[0]) * G.zoom_factor + G.SCREEN_CENTER[0] + G.camera_offset[0],
                (y - G.SCREEN_CENTER[1]) * G.zoom_factor + G.SCREEN_CENTER[1] + G.camera_offset[1])
                for x, y in coords
            ]
        else:
            return (
                (coords[0] - G.SCREEN_CENTER[0]) * G.zoom_factor + G.SCREEN_CENTER[0] + G.camera_offset[0],
                (coords[1] - G.SCREEN_CENTER[1]) * G.zoom_factor + G.SCREEN_CENTER[1] + G.camera_offset[1]
            )

    def render(self, screen) -> None:
        """Renders the hexagon on the screen"""
        pygame.draw.polygon(screen, self.colour, self.apply_camera_offset(self.vertices))
        pygame.draw.aalines(screen, color = [0, 0, 0], closed=True, points=self.apply_camera_offset(self.vertices))

    @property   
    def centre(self) -> Tuple[float, float]:
        """Centre of the hexagon"""
        x, y = self.position
        return (x, y + self.radius)

    @property
    def minimal_radius(self) -> float:
        """Horizontal length of the hexagon"""
        return self.radius * math.cos(math.radians(30))


class FlatTopHexagonTile(HexagonTile):
    def compute_vertices(self) -> List[Tuple[float, float]]:
        """Returns a list of the hexagon's vertices as x, y tuples"""
        x, y = self.position
        half_radius = self.radius / 2
        minimal_radius = self.minimal_radius
        return [
            (x, y),
            (x - half_radius, y + minimal_radius),
            (x, y + 2 * minimal_radius),
            (x + self.radius, y + 2 * minimal_radius),
            (x + 3 * half_radius, y + minimal_radius),
            (x + self.radius, y),
        ]

    @property
    def centre(self) -> Tuple[float, float]:
        """Centre of the hexagon"""
        x, y = self.position
        return (x + self.radius / 2, y + self.minimal_radius)