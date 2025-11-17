import pygame


class Tower:
    """Simple placeholder king tower representation."""

    def __init__(self, x: float, y: float, width: int, height: int, owner: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.owner = owner  # "player" or "ai"
        self.color = (180, 180, 180)

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect(self.x, self.y, self.width, self.height),
        )

