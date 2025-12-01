import sys

import pygame

from game.core.world import World, COINS_MAX
from game.core.actions import PlayCardAction
from game.ui.draw import (
    draw_arena_with_bridges,
    draw_entities,
    draw_card_bar,
    draw_coins_bar,
    draw_game_over_banner,
)


def main() -> None:
    pygame.init()

    # Match smash2.py exactly for window setup.
    SCREEN_WIDTH, SCREEN_HEIGHT = 450, 750
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mario Royale - Pixel Art Fixed")
    clock = pygame.time.Clock()

    world = World(SCREEN_WIDTH, SCREEN_HEIGHT)

    # UI layout (mirrors smash2.py)
    UI_HEIGHT = 100
    PLAY_HEIGHT = SCREEN_HEIGHT - UI_HEIGHT

    # Fonts: same family/sizes as smash2.py
    font_small = pygame.font.SysFont("Arial", 16)
    font_large = pygame.font.SysFont("Arial bold", 24)
    font_ui = pygame.font.Font(None, 20)

    # Card selection state (Mario-style cards)
    card_order = ["mario", "bowser", "dry_bones", "red_shell"]
    selected_index = 0

    running = True
    while running:
        # Fixed 60 FPS just like smash2.py
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Card selection + play (player only)
            if event.type == pygame.KEYDOWN and not world.game_over:
                if event.key == pygame.K_1:
                    selected_index = 0
                elif event.key == pygame.K_2 and len(card_order) > 1:
                    selected_index = 1
                elif event.key == pygame.K_3 and len(card_order) > 2:
                    selected_index = 2
                elif event.key == pygame.K_4 and len(card_order) > 3:
                    selected_index = 3

            if event.type == pygame.MOUSEBUTTONDOWN and not world.game_over:
                mx, my = pygame.mouse.get_pos()

                # Click on card bar to change selection (same region as smash2.py)
                if my >= PLAY_HEIGHT:
                    card_width = SCREEN_WIDTH // len(card_order)
                    idx = int(mx // card_width)
                    if 0 <= idx < len(card_order):
                        selected_index = idx
                # Click in the player's half of the arena to play a card
                elif my > PLAY_HEIGHT // 2:
                    lane_width = SCREEN_WIDTH // 3
                    lane_index = max(0, min(2, mx // lane_width))
                    card_id = card_order[selected_index]
                    action = PlayCardAction(card_id=card_id, lane_index=lane_index)
                    world.apply_player_action(action)

        # UPDATE
        world.step(dt)

        # RENDER arena, entities, and HUD to visually match smash2.py
        render_info = world.get_render_info(SCREEN_HEIGHT)

        draw_arena_with_bridges(screen, SCREEN_WIDTH, SCREEN_HEIGHT, PLAY_HEIGHT)
        draw_entities(screen, world, render_info)
        draw_card_bar(
            screen,
            world,
            card_order,
            selected_index,
            SCREEN_WIDTH,
            UI_HEIGHT,
            PLAY_HEIGHT,
            font_large,
            font_ui,
        )
        draw_coins_bar(
            screen,
            world.player_coins,
            COINS_MAX,
            PLAY_HEIGHT,
            font_large,
        )
        draw_game_over_banner(
            screen,
            world.game_over,
            world.winner,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            font_large,
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
