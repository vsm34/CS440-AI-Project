import pygame

from game.core.world import WorldRenderInfo
from game.core.world import World
from game.entities.troop import SPRITE_ASSETS, UNIT_STATS


# Colors copied from smash2.py for visual parity
BLACK = (20, 20, 20)
GREEN_HP = (50, 205, 50)
RED_HP = (220, 20, 60)
WHITE = (255, 255, 255)
PURPLE = (148, 0, 211)
GOLD = (255, 215, 0)


def draw_arena_with_bridges(
    screen: pygame.Surface,
    width: int,
    height: int,
    play_height: int,
) -> None:
    """
    Recreate the arena background from smash2.py:
    - Dark border clear
    - Green battlefield
    - Blue river strip across the middle
    - Two wooden bridges at the sides
    """
    screen.fill(BLACK)

    # Battlefield ground
    pygame.draw.rect(screen, (40, 100, 40), (0, 0, width, height))

    # River strip through the middle of the play area
    river_y = play_height // 2 - 20
    pygame.draw.rect(screen, (30, 30, 150), (0, river_y, width, 40))

    # Wooden bridges (left and right), matching smash2 approximate positions
    bridge_w, bridge_h = 40, 50
    left_bridge_x = 60
    right_bridge_x = width - 100
    bridge_y = river_y - 5

    pygame.draw.rect(screen, (120, 80, 40), (left_bridge_x, bridge_y, bridge_w, bridge_h))
    pygame.draw.rect(screen, (120, 80, 40), (right_bridge_x, bridge_y, bridge_w, bridge_h))


def draw_entities(
    screen: pygame.Surface,
    world: World,
    render_info: WorldRenderInfo,
) -> None:
    """
    Draw towers and troops using their own draw methods.
    This preserves the detailed pixel-art behavior ported from smash2.py.
    """
    # Towers (player + AI)
    for tower in world.towers:
        tower.draw(screen)

    # Troops (player + AI)
    for troop in world.troops:
        troop.draw(screen)


def draw_card_bar(
    screen: pygame.Surface,
    world: World,
    card_order,
    selected_index: int,
    screen_width: int,
    ui_height: int,
    play_height: int,
    font_large: pygame.font.Font,
    font_ui: pygame.font.Font,
) -> None:
    """
    Recreate the card bar from smash2.py, including:
    - Wooden bar background
    - Four card slots
    - Selected outline
    - Cost numbers and names
    - Troop head sprites drawn from SPRITE_ASSETS
    """
    pygame.draw.rect(screen, (50, 30, 10), (0, play_height, screen_width, ui_height))

    card_w = screen_width // len(card_order)

    for i, card_id in enumerate(card_order):
        x_pos = i * card_w
        bg_color = (100, 80, 60) if i == selected_index else (70, 50, 30)
        pygame.draw.rect(screen, bg_color, (x_pos, play_height, card_w, ui_height))
        pygame.draw.rect(
            screen,
            (30, 10, 0),
            (x_pos, play_height, card_w, ui_height),
            3,
        )

        if i == selected_index:
            pygame.draw.rect(
                screen,
                GOLD,
                (x_pos + 3, play_height + 3, card_w - 6, ui_height - 6),
                3,
            )

        # Determine which unit index this card corresponds to, to fetch its sprite.
        card_def = world.card_defs.get(card_id, {})
        cost = int(card_def.get("cost", 0))
        stats_idx = int(card_def.get("stats_idx", i))

        # Cost number
        cost_txt = font_large.render(str(cost), True, PURPLE)
        screen.blit(cost_txt, (x_pos + 10, play_height + 10))

        # Sprite icon (Mario/DK/Peach/Yoshi, tinted as player)
        sprite = SPRITE_ASSETS.get("player", {}).get(stats_idx)
        if sprite is not None:
            ui_sprite = pygame.transform.scale(sprite, (40, 40))
            screen.blit(ui_sprite, (x_pos + card_w // 2 - 20, play_height + 15))

        # Name label (prefer UNIT_STATS name if available)
        unit_name = card_id.replace("_", " ").title()
        stats = UNIT_STATS.get(stats_idx)
        if stats is not None and "name" in stats:
            unit_name = str(stats["name"])

        name_txt = font_ui.render(unit_name, True, WHITE)
        screen.blit(
            name_txt,
            (x_pos + card_w // 2 - name_txt.get_width() // 2, play_height + 65),
        )


def draw_coins_bar(
    screen: pygame.Surface,
    current_coins: float,
    max_coins: int,
    play_height: int,
    font_large: pygame.font.Font,
) -> None:
    """
    Draw the Coins bar in the same style as the original resource bar from smash2.py:
    - Black background pill
    - Gold fill proportional to coins
    - White numeric label (coins count) and "Coins" label
    """
    pygame.draw.rect(screen, BLACK, (5, play_height - 40, 160, 35))

    ratio = max(0.0, min(1.0, current_coins / max_coins))
    coins_bar_w = int(140 * ratio)
    pygame.draw.rect(screen, GOLD, (10, play_height - 35, coins_bar_w, 25))

    # Numeric coins count
    coins_display = font_large.render(f"{int(current_coins)}", True, WHITE)
    screen.blit(coins_display, (165, play_height - 35))

    # Static "Coins" label
    label = font_large.render("Coins", True, WHITE)
    screen.blit(label, (10, play_height - 55))


def draw_game_over_banner(
    screen: pygame.Surface,
    game_over: bool,
    winner: str | None,
    screen_width: int,
    screen_height: int,
    font_large: pygame.font.Font,
) -> None:
    """
    Draw the centered black banner and winner text when the game ends,
    matching smash2.py's style.
    """
    if not game_over:
        return

    msg = "YOU WIN!" if winner == "player" else "ENEMY WINS!"
    win_msg = font_large.render(msg, True, WHITE)

    rect = win_msg.get_rect(center=(screen_width // 2, screen_height // 2))
    pygame.draw.rect(screen, BLACK, rect.inflate(20, 20))
    screen.blit(win_msg, rect)


