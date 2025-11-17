import pygame

class Troop:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 120  # pixels per second (slow unit)
        self.color = (200, 200, 200)  # light gray (Drybones placeholder)

    def update(self, dt):
        # Move upward (towards enemy)
        self.y -= self.speed * dt

        # Stop at top (temporary)
        if self.y < 0:
            self.y = 0

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect(self.x, self.y, self.width, self.height)
        )
