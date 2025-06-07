import random
from cards import SUITS

class AI:
    def choose_action(self, game, player, reveal, pile):
        """Return an action string like the human input."""
        if reveal is None:
            # war phase
            if random.random() < 0.2:
                suits = [s for s in SUITS if player.armies[s] and game.players[1 - game.turn].armies[s]]
                if suits:
                    return f"war {random.choice(suits)}"
            return 'pass'
        if not pile:
            idx = random.randrange(len(player.hand))
            return f'play {idx}'
        actions = ['call', 'concede', 'play']
        choice = random.choice(actions)
        if choice == 'play':
            idx = random.randrange(len(player.hand))
            return f'play {idx}'
        return choice
