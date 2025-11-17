import pygame
import sys

def main():
    print(">>> main() started")
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Smash Royale")
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))

        # ----- ONE VERTICAL LANE (center lane) -----
        screen_width, screen_height = screen.get_size()
        lane_width = 220
        lane_x = screen_width // 2 - lane_width // 2  # center the lane

        pygame.draw.rect(
            screen,
            (60, 60, 60),
            pygame.Rect(lane_x, 0, lane_width, screen_height)
        )
        # -------------------------------------------

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
