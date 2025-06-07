import random

SUITS = ['spades', 'hearts', 'diamonds', 'clubs']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

SYMBOLS = {
    'spades': '\u2660',
    'hearts': '\u2665',
    'diamonds': '\u2666',
    'clubs': '\u2663',
}

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    @property
    def value(self) -> int:
        return RANKS.index(self.rank) + 2

    @property
    def is_king(self) -> bool:
        return self.rank == 'K'

    def beats(self, other: 'Card') -> bool:
        if self.suit != other.suit:
            return False
        return self.value > other.value

class Deck:
    def __init__(self):
        self.cards = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop() if self.cards else None

    def add_cards(self, cards: list[Card]):
        """Add cards to the deck and reshuffle."""
        self.cards.extend(cards)
        random.shuffle(self.cards)

    def __len__(self):
        return len(self.cards)
