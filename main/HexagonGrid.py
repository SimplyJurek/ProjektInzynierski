from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List
from typing import Tuple
import random

import pygame


@dataclass
class HexagonTile:
    """Hexagon class"""

    radius: float
    position: Tuple[float, float]
    colour: Tuple[int, ...]
    highlight_offset: int = 3
    max_highlight_ticks: int = 15
    state: int = 0
    nextstate: int = 0
    flamestate: int = 15 # podstan palacej sie komorki

    def __post_init__(self):
        self.vertices = self.compute_vertices()
        self.highlight_tick = 0
        self.state = 0
        self.health = 100

    # def update(self):

    #     # neighbours_list = self.compute_neighbours(hexagons_copy)
    #     # neighbour_state_counter = 0

    #     # for neighbour in neighbours_list:
    #     #     if neighbour.state == 1:
    #     #         neighbour_state_counter += 1

    #     # if self.state == 0 and neighbour_state_counter >= 2:
    #     #     self.state = 1

    def change_state(self, hexlist):
        """Calculates whether the state of the cell should change in the next iteration. If yes, changes the nextstate value."""
        if self.state == 0:
            neighbours_list = self.compute_neighbours(hexlist)
            neighbour_state_counter = sum(1 for neighbour in neighbours_list if neighbour.state == 1)
            if neighbour_state_counter >= 2:
                self.nextstate = 1
        if self.state == 1:
            self.flamestate -= 1
            if self.flamestate == 0:
                self.nextstate = 2
            #TODO Change the implementation of the fire extinguishing? Not sure if this is the right approach, considering we want to add outside factors such as wind  
            #TODO Add a different state for eg. walls and other materials, some of which may be unflammable, others more flammable eg. grass/bushes
            #TODO add randomizing the possibility of the cell to catch fire, instead of being 100% when at least 2 neighbours are on fire
            
        if self.highlight_tick > 0:
            self.highlight_tick -= 1

        if self.state == 1 and self.health > 0:
            self.colour = [120, 10, 0]
            self.health -= 1
        if self.state == 1 and self.health <= 0:
            self.state = 2
            self.colour = [60, 60, 60]

        # return hexagons_copy
    
    # def update_grid(self,hexlist):
    #     nexthexlist = hexlist

    #     for hexagon in hexlist:
    #         hexagon.update()

        
    def update(self):
        """Updates the Cell's state based on it's current nextstate value."""
        if self.nextstate > self.state:
            self.state = self.nextstate
            if self.state == 0:
                self.colour = [0, 120, 0]
            elif self.state == 1:
                self.colour = [120, 0, 0]
            else:
                self.colour = [100, 100, 100]
        #TODO Maybe add other functionalities except change of color when changing the state


    def compute_vertices(self) -> List[Tuple[float, float]]:
        """Returns a list of the hexagon's vertices as x, y tuples"""
        # pylint: disable=invalid-name
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

    def compute_neighbours(self, hexagons: List[HexagonTile]) -> List[HexagonTile]:
        """Returns hexagons whose centres are two minimal radiuses away from self.centre"""
        # could cache results for performance
        return [hexagon for hexagon in hexagons if self.is_neighbour(hexagon)]

    def collide_with_point(self, point: Tuple[float, float]) -> bool:
        """Returns True if distance from centre to point is less than horizontal_length"""
        return math.dist(point, self.centre) < self.minimal_radius

    def is_neighbour(self, hexagon: HexagonTile) -> bool:
        """Returns True if hexagon centre is approximately
        2 minimal radiuses away from own centre
        """
        distance = math.dist(hexagon.centre, self.centre)
        return math.isclose(distance, 2 * self.minimal_radius, rel_tol=0.05)

    def render(self, screen) -> None:
        """Renders the hexagon on the screen"""
        pygame.draw.polygon(screen, self.highlight_colour, self.vertices)
        pygame.draw.aalines(screen, color = [0, 0, 0], closed=True, points=self.vertices)
       

    def render_highlight(self) -> None:
        """Draws a border around the hexagon with the specified colour"""
        self.highlight_tick = self.max_highlight_ticks
        # pygame.draw.polygon(screen, self.highlight_colour, self.vertices)

    @property
    def centre(self) -> Tuple[float, float]:
        """Centre of the hexagon"""
        x, y = self.position  # pylint: disable=invalid-name
        return (x, y + self.radius)

    @property
    def minimal_radius(self) -> float:
        """Horizontal length of the hexagon"""
        # https://en.wikipedia.org/wiki/Hexagon#Parameters
        return self.radius * math.cos(math.radians(30))

    @property
    def highlight_colour(self) -> Tuple[int, ...]:
        """Colour of the hexagon tile when rendering highlight"""
        offset = self.highlight_offset * self.highlight_tick
        brighten = lambda x, y: x + y if x + y < 255 else 255
        return tuple(brighten(x, offset) for x in self.colour)


class FlatTopHexagonTile(HexagonTile):
    def compute_vertices(self) -> List[Tuple[float, float]]:
        """Returns a list of the hexagon's vertices as x, y tuples"""
        # pylint: disable=invalid-name
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
        x, y = self.position  # pylint: disable=invalid-name
        return (x + self.radius / 2, y + self.minimal_radius)