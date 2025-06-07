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
            p.draw(self.draw_card, 3)
        self.turn = 0
        self.card_images = {}
        self.load_images()
        self.font = pygame.font.SysFont('arial', 20)

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

    def declare_war(self, attacker, defender, suit, reinforcements):
        if not attacker.armies[suit] or not defender.armies[suit]:
            print('War not possible on that suit.')
            return
        attack_total = len(attacker.armies[suit]) + sum(1 for c in attacker.hand if c.suit == suit)
        for r in reinforcements:
            comp = attacker.armies.get(r)
            if not comp:
                continue
            attack_total += sum(1 if c.suit == r else -1 for c in comp)
        defend_total = len(defender.armies[suit]) + sum(1 for c in defender.hand if c.suit == suit)
        if attack_total > defend_total:
            print(f"{attacker.name} wins the war for {suit}!")
            self.discard.extend(defender.armies[suit])
            defender.armies[suit] = []
        else:
            print(f"{defender.name} defends {suit} successfully.")
            for r in [suit] + reinforcements:
                self.discard.extend(attacker.armies[r])
                attacker.armies[r] = []

    def war_phase(self):
        player = self.players[self.turn]
        opponent = self.players[1 - self.turn]
        action = self.get_input(
            f"{player.name}: declare 'war <suit> [reinforcements]' or 'pass': ",
            player,
            None,
            None,
        )
        if action.startswith('war'):
            tokens = action.split()
            if len(tokens) >= 2:
                suit = tokens[1]
                reinforcements = tokens[2:]
                self.declare_war(player, opponent, suit, reinforcements)
                self.maintain_hands()

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
                self.maintain_hands()
                current, opponent = opponent, current
            elif action.startswith('wild'):
                parts = action.split()
                if len(parts) != 3:
                    print('usage: wild <king_idx> <card_idx>')
                    continue
                try:
                    k_idx = int(parts[1])
                    c_idx = int(parts[2])
                except Exception:
                    print('invalid indices')
                    continue
                king = player.remove_card(k_idx)
                if not king or not king.is_king:
                    print('invalid king')
                    if king:
                        player.hand.insert(k_idx, king)
                    continue
                # adjust second index if necessary
                if c_idx > k_idx:
                    c_idx -= 1
                card = player.remove_card(c_idx)
                if not card:
                    print('invalid card')
                    player.hand.insert(k_idx, king)
                    continue
                pile.append((current, (king, card)))
                self.maintain_hands()
                current, opponent = opponent, current
            elif action == 'call':
                if not pile:
                    print('nothing to call')
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
                    self.discard.append(king_card) if winner != last_player else win_p.armies[king_card.suit].append(king_card)
                else:
                    win_p.armies[last_card.suit].append(last_card)
                if winner != last_player:
                    # loser card(s) discarded
                    if isinstance(last_play, tuple):
                        self.discard.extend([king_card, last_card])
                    else:
                        self.discard.append(last_card)
                self.turn = winner
                self.maintain_hands()
                print(f"{win_p.name} wins the duel")
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
            self.war_phase()
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
