import pygame
import string
from typing import Tuple

pygame.init()

class Button:
    def __init__(
            self,
            screen,
            text: string,
            fontSize: int,
            textColour: Tuple,
            textColourHighlight : Tuple,
            position: Tuple,
            size: Tuple,
            buttonColour: Tuple,
            buttonColourHighlight: Tuple,
            enabled: bool = True,
            highlighted: bool = False
        ):
        self.text = text
        self.fontSize = fontSize
        self.position = position
        self.enabled = enabled
        self.size = size
        self.buttonColour = buttonColour
        self.buttonColourHighlight = buttonColourHighlight
        self.textColour = textColour
        self.textColourHighlight = textColourHighlight
        self.highlighted = highlighted
        self.font = pygame.font.SysFont('arialblack', self.fontSize)

        self.draw(screen)
        self.highlight(screen)

    def draw(self, screen):
        buttonText = self.font.render(self.text, True, self.textColour)
        buttonRect = pygame.rect.Rect(self.position, self.size)
        buttonTextRect = buttonText.get_rect(center = buttonRect.center)
        pygame.draw.rect(screen, self.buttonColour, buttonRect, 2, 15)
        screen.blit(buttonText, buttonTextRect)

    def highlight(self, screen):
        pos = pygame.mouse.get_pos()
        buttonText = self.font.render(self.text, True, self.textColourHighlight)
        buttonRect = pygame.rect.Rect(self.position, self.size)
        if buttonRect.collidepoint(pos) and self.enabled or self.highlighted:
            buttonTextRect = buttonText.get_rect(center = buttonRect.center)
            pygame.draw.rect(screen, self.buttonColourHighlight, buttonRect, 0, 15)
            screen.blit(buttonText, buttonTextRect)

    def check_click(self):
        pos = pygame.mouse.get_pos()
        buttonRect = pygame.rect.Rect(self.position, self.size)
        if buttonRect.collidepoint(pos) and self.enabled:
            return True
        else:
            return False