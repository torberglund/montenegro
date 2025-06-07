import random

class AI:
    def choose_action(self, game, player, reveal, pile):
        """Return an action string like the human input."""
        if not pile:
            idx = random.randrange(len(player.hand))
            return f'play {idx}'
        actions = ['call', 'concede', 'play']
        choice = random.choice(actions)
        if choice == 'play':
            idx = random.randrange(len(player.hand))
            return f'play {idx}'
        return choice
