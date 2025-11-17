import pygame
import sys

from entities.troop import Troop  # make sure game/entities/troop.py exists


def main():
    print(">>> main() started")
    pygame.init()

    # Window setup
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Smash Royale")
    clock = pygame.time.Clock()

    # ----- Lane geometry (single vertical lane like Clash) -----
    lane_width = 220
    lane_x = SCREEN_WIDTH // 2 - lane_width // 2
    lane_rect = pygame.Rect(lane_x, 0, lane_width, SCREEN_HEIGHT)
    # -----------------------------------------------------------

    # ----- First troop (Drybones placeholder) -----
    # Centered in the lane, near the bottom of the screen
    troop_start_x = lane_x + lane_width // 2 - 20  # 20 = half of troop width (40)
    troop_start_y = SCREEN_HEIGHT - 60             # a bit above the bottom
    troop = Troop(troop_start_x, troop_start_y)
    # ----------------------------------------------

    running = True
    while running:
        # dt = time in seconds since last frame (for smooth movement)
        dt = clock.tick(60) / 1000.0

        # ---- Event handling ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ---- Update game state ----
        troop.update(dt)

        # ---- Render ----
        screen.fill((30, 30, 30))  # dark background

        # draw lane
        pygame.draw.rect(screen, (60, 60, 60), lane_rect)

        # draw troop
        troop.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
