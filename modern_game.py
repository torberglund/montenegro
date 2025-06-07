# Modern GUI implementation of King of Montenegro
import os
import sys
import subprocess
import importlib
import pygame
from cards import Deck, SUITS
from collections import defaultdict

EXPECTED_CARDS = [f"{r}_of_{s}.png" for s in SUITS for r in (
    ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
)] + ['back.png']

CARD_WIDTH = 80
CARD_HEIGHT = 120


def ensure_card_images():
    need_render = False
    if not os.path.isdir('cards'):
        need_render = True
    else:
        for fname in EXPECTED_CARDS:
            if not os.path.isfile(os.path.join('cards', fname)):
                need_render = True
                break
    if need_render:
        print('Generating card images...')
        subprocess.run([sys.executable, 'render_cards.py'], check=True)


class Player:
    def __init__(self, name, ai=None):
        self.name = name
        self.ai = ai
        self.hand = []
        self.armies = defaultdict(list)

    def draw(self, draw_func, n=1):
        for _ in range(n):
            card = draw_func()
            if card:
                self.hand.append(card)

    def remove_card(self, index):
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None


class Game:
    def __init__(self, ai_module: str | None = None):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption('King of Montenegro - Modern')
        self.clock = pygame.time.Clock()
        self.deck = Deck()
        self.discard = []
        players = [Player('Player 1')]
        if ai_module:
            try:
                module = importlib.import_module(ai_module)
                ai_cls = getattr(module, 'AI')
                players.append(Player('AI', ai_cls()))
            except Exception as e:
                print(f'Failed to load AI module {ai_module}:', e)
                players.append(Player('Player 2'))
        else:
            players.append(Player('Player 2'))
        self.players = players
        for p in self.players:
            p.draw(self.draw_card, 3)
        self.turn = 0
        self.card_images = {}
        self.load_images()
        self.font = pygame.font.SysFont('arial', 20)

        self.play_area = pygame.Rect(462, 324, CARD_WIDTH, CARD_HEIGHT)
        self.dragging = None  # (index, offset)
        self.drag_pos = (0, 0)

        self.message = ''

    def load_images(self):
        for fname in os.listdir('cards'):
            if fname.endswith('.png'):
                img = pygame.image.load(os.path.join('cards', fname)).convert_alpha()
                self.card_images[fname[:-4]] = img

    def draw_card(self):
        card = self.deck.draw()
        if not card and self.discard:
            self.deck.add_cards(self.discard)
            self.discard = []
            card = self.deck.draw()
        return card

    def maintain_hands(self):
        for p in self.players:
            while len(p.hand) < 3:
                card = self.draw_card()
                if not card:
                    break
                p.hand.append(card)

    # GUI utilities
    def render_text(self, text, pos):
        img = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(img, pos)

    def render_hand(self, player, y, active=False):
        rects = []
        for i, card in enumerate(player.hand):
            key = f"{card.rank}_of_{card.suit}"
            img = self.card_images.get(key)
            if not img:
                continue
            x = 20 + i * (CARD_WIDTH + 10)
            rect = img.get_rect(topleft=(x, y))
            if active and self.dragging and self.dragging[0] == i:
                rect = img.get_rect(center=self.drag_pos)
            self.screen.blit(img, rect)
            rects.append(rect)
            if player.ai is None:
                idx_img = self.font.render(str(i), True, (0,0,0))
                self.screen.blit(idx_img, (rect.x, rect.y + CARD_HEIGHT + 5))
        return rects

    def show_state(self, reveal=None):
        self.screen.fill((0, 128, 0))
        # opponent hand as backs
        opp = self.players[1 - self.turn]
        back = self.card_images.get('back')
        for i in range(len(opp.hand)):
            rect = pygame.Rect(20 + i * (CARD_WIDTH + 10), 20, CARD_WIDTH, CARD_HEIGHT)
            if back:
                self.screen.blit(back, rect)
        # current player hand
        self.hand_rects = self.render_hand(self.players[self.turn], 600, active=True)
        # armies not drawn for simplicity
        if reveal:
            img = self.card_images.get(f"{reveal.rank}_of_{reveal.suit}")
            if img:
                rect = img.get_rect(center=self.play_area.center)
                self.screen.blit(img, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.play_area, 2)
        self.render_text('Call', (900, 600))
        self.render_text('Concede', (900, 630))
        self.render_text(self.message, (20, 560))
        pygame.display.flip()

    # Input handling
    def wait_for_action(self, reveal, pile):
        self.message = ''
        self.dragging = None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, rect in enumerate(self.hand_rects):
                        if rect.collidepoint(pos):
                            self.dragging = (i, pos[0]-rect.x, pos[1]-rect.y)
                            self.drag_pos = pos
                            break
                    if 900 <= pos[0] <= 960:
                        if 600 <= pos[1] <= 620:
                            return 'call'
                        if 630 <= pos[1] <= 660:
                            return 'concede'
                if event.type == pygame.MOUSEMOTION and self.dragging:
                    self.drag_pos = event.pos
                if event.type == pygame.MOUSEBUTTONUP and self.dragging:
                    # drop on play area?
                    pos = event.pos
                    index = self.dragging[0]
                    self.dragging = None
                    if self.play_area.collidepoint(pos):
                        return f'play {index}'
            self.show_state(reveal)
            self.clock.tick(30)

    def duel(self):
        reveal = self.draw_card()
        drawn_king = None
        while reveal and reveal.rank == 'K':
            drawn_king = reveal
            reveal = self.draw_card()
        if not reveal:
            return False
        pile = []
        current = self.turn
        opponent = 1 - current
        while True:
            player = self.players[current]
            self.show_state(reveal)
            action = None
            if player.ai:
                action = player.ai.choose_action(self, player, reveal, pile)
            else:
                action = self.wait_for_action(reveal, pile)
            if action.startswith('play'):
                try:
                    idx = int(action.split()[1])
                except Exception:
                    self.message = 'invalid index'
                    continue
                card = player.remove_card(idx)
                if not card:
                    self.message = 'invalid card'
                    continue
                pile.append((current, card))
                self.maintain_hands()
                current, opponent = opponent, current
            elif action == 'call':
                if not pile:
                    self.message = 'nothing to call'
                    continue
                last_player, last_play = pile[-1]
                if isinstance(last_play, tuple):
                    king_card, last_card = last_play
                    valid = last_card.suit == reveal.suit and last_card.value > reveal.value
                else:
                    last_card = last_play
                    valid = last_card.beats(reveal)
                winner = last_player if valid else opponent
                loser = opponent if valid else last_player
                win_p = self.players[winner]
                lose_p = self.players[loser]
                win_p.armies[reveal.suit].append(reveal)
                bonus = self.draw_card()
                if bonus:
                    win_p.armies[reveal.suit].append(bonus)
                if drawn_king:
                    win_p.armies[reveal.suit].append(drawn_king)
                if isinstance(last_play, tuple):
                    win_p.armies[last_card.suit].append(last_card)
                    if winner != last_player:
                        self.discard.append(king_card)
                    else:
                        win_p.armies[king_card.suit].append(king_card)
                else:
                    win_p.armies[last_card.suit].append(last_card)
                if winner != last_player:
                    if isinstance(last_play, tuple):
                        self.discard.extend([king_card, last_card])
                    else:
                        self.discard.append(last_card)
                self.turn = winner
                self.maintain_hands()
                self.message = f"{win_p.name} wins the duel"
                break
            elif action == 'concede':
                self.players[opponent].armies[reveal.suit].append(reveal)
                if drawn_king:
                    self.players[opponent].armies[reveal.suit].append(drawn_king)
                for _, played in pile:
                    if isinstance(played, tuple):
                        self.discard.extend(played)
                    else:
                        self.discard.append(played)
                self.turn = opponent
                self.maintain_hands()
                self.message = f"{self.players[opponent].name} wins the duel by concession"
                break
            else:
                self.message = 'unknown command'
        # brief display to show result
        for _ in range(30):
            self.show_state()
            self.clock.tick(30)
        return True

    def check_victory(self):
        for i, p in enumerate(self.players):
            if all(len(p.armies[s]) > 0 for s in SUITS):
                other = self.players[1 - i]
                if any(len(other.armies[s]) == 0 for s in SUITS):
                    return i
        return None

    def run(self):
        running = True
        while running:
            winner = self.check_victory()
            if winner is not None:
                print(f"{self.players[winner].name} wins the game!")
                running = False
                continue
            if not self.duel():
                print('No more cards. Game over.')
                break
        pygame.quit()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Play King of Montenegro - Modern GUI')
    parser.add_argument('--ai', help='Python module path for AI opponent')
    args = parser.parse_args()

    try:
        ensure_card_images()
    except Exception as e:
        print('Failed to generate card images:', e)
        sys.exit(1)

    Game(ai_module=args.ai).run()
