import pygame
import sys

from game.core.world import World


def main():
    print(">>> main() started")
    pygame.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Smash Royale")
    clock = pygame.time.Clock()

    world = World(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # UPDATE
        world.step(dt)

        # RENDER
        screen.fill((30, 30, 30))

        # draw lane (single lane for now)
        lane_rect = pygame.Rect(
            world.lane_x, 0, world.lane_width, SCREEN_HEIGHT
        )
        pygame.draw.rect(screen, (60, 60, 60), lane_rect)

        # draw troops
        for troop in world.troops:
            troop.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
