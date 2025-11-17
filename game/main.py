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

        render_info = world.get_render_info(SCREEN_HEIGHT)

        # draw lanes
        for lane_rect in render_info.lane_rects:
            pygame.draw.rect(screen, (60, 60, 60), lane_rect)

        # draw arena boundaries
        pygame.draw.rect(screen, (100, 100, 100), render_info.top_boundary)
        pygame.draw.rect(screen, (100, 100, 100), render_info.bottom_boundary)

        # draw towers
        for tower in world.towers:
            tower.draw(screen)

        # draw troops
        for troop in world.troops:
            troop.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
