import os
import sys
import subprocess
import importlib
import pygame
from cards import Deck, SUITS, SYMBOLS
from collections import defaultdict

EXPECTED_CARDS = [f"{r}_of_{s}.png" for s in SUITS for r in (
    ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
)] + ['back.png']

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

CARD_WIDTH = 80
CARD_HEIGHT = 120

class Player:
    def __init__(self, name, ai=None):
        self.name = name
        self.ai = ai
        self.hand = []
        self.armies = defaultdict(list)

    def draw(self, deck, n=1):
        for _ in range(n):
            card = deck.draw()
            if card:
                self.hand.append(card)

    def remove_card(self, index):
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None

class Game:
    def __init__(self, ai_module: str | None = None):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('King of Montenegro')
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
            p.draw(self.deck, 3)
        self.turn = 0
        self.card_images = {}
        self.load_images()
        self.font = pygame.font.SysFont('arial', 20)

    def load_images(self):
        for fname in os.listdir('cards'):
            if fname.endswith('.png'):
                img = pygame.image.load(os.path.join('cards', fname)).convert_alpha()
                self.card_images[fname[:-4]] = img

    def render_hand(self, player, y):
        for i, card in enumerate(player.hand):
            key = f"{card.rank}_of_{card.suit}"
            img = self.card_images.get(key)
            if img:
                rect = img.get_rect(topleft=(20 + i * (CARD_WIDTH + 10), y))
                self.screen.blit(img, rect)
                txt = self.font.render(str(i), True, (0,0,0))
                self.screen.blit(txt, (rect.x, rect.y + CARD_HEIGHT + 5))

    def show_state(self, reveal=None):
        self.screen.fill((0,128,0))
        self.render_hand(self.players[0], 400)
        self.render_hand(self.players[1], 20)
        if reveal:
            img = self.card_images.get(f"{reveal.rank}_of_{reveal.suit}")
            if img:
                rect = img.get_rect(center=(400, 250))
                self.screen.blit(img, rect)
        pygame.display.flip()

    def get_input(self, prompt, player, reveal, pile):
        if player.ai:
            try:
                return player.ai.choose_action(self, player, reveal, pile)
            except Exception as e:
                print('AI error:', e)
                return 'concede'
        print(prompt)
        pygame.event.pump()
        return input()

    def duel(self):
        reveal = self.deck.draw()
        drawn_king = None
        while reveal and reveal.rank == 'K':
            drawn_king = reveal
            reveal = self.deck.draw()
        if not reveal:
            return False
        pile = []
        current = self.turn
        opponent = 1 - current
        while True:
            player = self.players[current]
            self.show_state(reveal)
            action = self.get_input(
                f"{player.name}: play index, call, or concede: ", player, reveal, pile
            )
            if action.startswith('play'):
                try:
                    idx = int(action.split()[1])
                except Exception:
                    print('invalid index')
                    continue
                card = player.remove_card(idx)
                if not card:
                    print('invalid card')
                    continue
                pile.append((current, card))
                player.draw(self.deck)
                current, opponent = opponent, current
            elif action == 'call':
                if not pile:
                    print('nothing to call')
                    continue
                last_player, last_card = pile[-1]
                valid = last_card.beats(reveal)
                winner = last_player if valid else opponent
                loser = opponent if valid else last_player
                self.players[winner].armies[reveal.suit].append(reveal)
                if drawn_king:
                    self.players[winner].armies[reveal.suit].append(drawn_king)
                self.players[winner].armies[last_card.suit].append(last_card)
                self.turn = winner
                print(f"{self.players[winner].name} wins the duel")
                break
            elif action == 'concede':
                self.players[opponent].armies[reveal.suit].append(reveal)
                if drawn_king:
                    self.players[opponent].armies[reveal.suit].append(drawn_king)
                self.turn = opponent
                print(f"{self.players[opponent].name} wins the duel by concession")
                break
            else:
                print('unknown command')
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

    parser = argparse.ArgumentParser(description='Play King of Montenegro')
    parser.add_argument('--ai', help='Python module path for AI opponent')
    args = parser.parse_args()

    try:
        ensure_card_images()
    except Exception as e:
        print('Failed to generate card images:', e)
        sys.exit(1)

    Game(ai_module=args.ai).run()
