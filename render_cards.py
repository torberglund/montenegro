import os
import pygame
from cards import SUITS, RANKS, SYMBOLS

CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_DIR = 'cards'

pygame.init()
font = pygame.font.SysFont('arial', 24, bold=True)
large_font = pygame.font.SysFont('arial', 36, bold=True)

os.makedirs(CARD_DIR, exist_ok=True)

COLORS = {
    'spades': (0, 0, 0),
    'clubs': (0, 0, 0),
    'hearts': (200, 0, 0),
    'diamonds': (200, 0, 0),
}

def render_card(rank: str, suit: str):
    surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    surface.fill((255, 255, 255))
    pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
    color = COLORS[suit]
    rank_text = font.render(rank, True, color)
    surface.blit(rank_text, (5, 5))
    symbol_text = large_font.render(SYMBOLS[suit], True, color)
    rect = symbol_text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
    surface.blit(symbol_text, rect)
    pygame.image.save(surface, os.path.join(CARD_DIR, f"{rank}_of_{suit}.png"))

for suit in SUITS:
    for rank in RANKS:
        render_card(rank, suit)

# card back
back = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
back.fill((30, 30, 120))
pygame.draw.rect(back, (0, 0, 0), back.get_rect(), 2)
pygame.image.save(back, os.path.join(CARD_DIR, 'back.png'))
