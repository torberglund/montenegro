# King of Montenegro

This repository contains an implementation of the card game **King of Montenegro** using `pygame`.

## Requirements

- Python 3.11+
- `pygame` (install with `pip install pygame`)

## Generating Card Images

The repository does not store binary PNG files. When you first run the game it
will check for the `cards/` directory and automatically invoke
`render_cards.py` if any images are missing. You can also generate the images
manually with:

```bash
python render_cards.py
```

This script creates a `cards/` directory containing simple PNG images for all
52 playing cards and a card back.

## Playing the Game

Run the game with:

```bash
python game.py
```

To play against the included example AI opponent, run:

```bash
python game.py --ai ai_random


```

A window will open showing each player's hand. The game logic is primarily text-driven: players enter commands in the terminal while the graphical window displays the cards. By default the game starts with two human players, but the `--ai` option loads an AI module for the second player.

### Controls

Enter these commands in the terminal during play:

- `play <index>` – play the card at the given hand index.
- `wild <king_index> <card_index>` – play a King as a wild followed by another card.
- `call` – challenge the previous play.
- `concede` – concede the current duel.
- During the war phase use `war <suit> [reinforcements...]` or `pass`.

## Rules

1. Objective
Command the armys of all four suits by winning duels and declaring war. A player wins by maintaining at least one army (i.e. a pile of captured cards) in every suit while leaving their opponent with none.

2. Components
Deck: One standard 52-card deck.

Draw Pile: The shuffled deck placed face down.

Discard Pile: A pile for used or discarded cards.

Player Hands: Each player holds up to 3 cards.

Army Areas: Each player’s table area where captured cards are organized by suit.

3. Setup
Shuffle the deck thoroughly.

Place the deck face down as the draw pile.

Each player draws 3 cards from the draw pile.

Decide which player goes first by any mutually agreed method.

4. Game Overview
King of Montenegro is played in a series of duels. In each duel, one card is revealed from the draw pile, and players respond by playing cards from their hand (or, if allowed, from their armies) to “beat” it—either truthfully or by bluffing. Winning duels earns you cards that form or add to your suit-specific armies. At any time on your turn, you may also declare war on an opponent’s army, using a specialized combat mechanic that can incorporate reinforcements from other armies.

An additional twist is that Kings act as wild cards. They can be used to “reset” the card value requirement during a duel under specific conditions (detailed below).

5. Gameplay Phases
5.1 The Duel Phase
A duel is the basic contest in King of Montenegro.

5.1.1 Initiating a Duel
Revealing the Card:
The starting player (Player A) flips the top card of the draw pile face up.

Special Note on Drawn Kings:
If the revealed card is a King, it cannot be used directly. Instead, the player must draw another card from the draw pile. The drawn King is set aside and will later be awarded to the winner of the duel along with the card that is played.

Responding to the Revealed Card:
Player A then selects one card from their hand and places it face down as an “answer” to the revealed card.

Standard Rule: The played card must be capable—by rank and suit—of beating the revealed card, though you may opt to bluff.

Wild Card (King) Option:
At any point during the duel, if you lack a suitable card, you may choose to play a King as a wild card to “reset” the required value.

Restrictions:
If, for example, the revealed card is a spade (e.g., spade 5), you may only use a King that is either in your hand or in your spade army.

Procedure:

You select the eligible King and play it face down, declaring it as the wild card (e.g., “spade King”).

Immediately thereafter, you must also play an additional card from your hand. This second card is also placed face down and you declare its suit and value (for example, “heart three”).

Either or both of these declarations may be a bluff.

Your opponent may call your bluff, in which case you reveal both the King and the additional card.

Outcome:
If you win the duel, you collect both the King and the additional card as part of your reward.

5.1.2 Responding and Counter-Responses
After Player A’s play:

Player B’s Options:

Answer: Play a card from hand face down to attempt to beat Player A’s answer.

Call the Bluff: Flip Player A’s card (or cards, if a wild card sequence was used) to check if the play is valid.

Acknowledge Defeat: Concede the duel.

Alternate Play:
If Player B answers, the roles reverse and Player A may then respond. This back-and-forth continues until one player either concedes or calls a bluff.

5.1.3 Hand Maintenance
After each exchange in the duel:

Both players draw cards from the draw pile (if available) until they again have 3 cards in hand.

5.2 Resolving a Duel
When the duel concludes:

If a Player Acknowledges Defeat:
The opponent wins the duel.

The winning player collects the original face-up card (the one flipped from the draw pile).

Army Formation:

If no army exists yet for that suit, the card starts a new army and is placed face up.

If an army already exists, the card is added face down.

If a Bluff is Called:
Both players reveal their most recent face-down played card(s).

The player who was not bluffing (or who correctly identified the bluff) wins the duel.

The winner collects:

The original face-up card.

One additional card drawn from the draw pile.

Plus: Any King played as a wild card (or the drawn King from the draw pile, if that was the case).

The collected cards are then used to form or add to an army following the face up/face down rules.

5.3 Using Army Cards
During a Duel:
You may use a card from one of your established armies if it meets the requirements (i.e., it must be from the same suit as the card in question).

Wild Card Exception:
As described, Kings from the appropriate source (hand or the army corresponding to the revealed card’s suit) may be used as wild cards.

Bluffing:
Cards played from an army are subject to the same bluffing and calling rules as cards from hand.

5.4 Declaring War (with Reinforcement)
At any time on your turn, you may try to wrest control of an opponent’s army by declaring war on that suit.

5.4.1 Declaration & Army Commitment
Attacker’s Declaration:
Announce war on an opponent’s army of a chosen suit (the attacked suit), e.g., “I declare war on your spades.”

Army Commitment:

The attacker uses:

Their own army of the attacked suit, and

Optionally, one or more additional (reinforcement) armies from different suits.

Hand Cards:

Only for the attacked suit’s component do hand cards count.

Reinforcement armies count only the cards already in that army.

The defender uses only their army and hand cards of the attacked suit.

5.4.2 Calculating War Values
Attacker:

Attacked Suit Component:
Value = (Number of attacked suit cards in the attacked army) + (Number of matching attacked suit cards in hand)
(No subtraction is applied.)

Reinforcement Component(s):
For each reinforcement army used, calculate:
Value = (Number of cards in that army that match its own suit) − (Number of cards in that army that do not match)
(Hand cards do not contribute.)

Final Attacker Total:
Sum the attacked suit component and all reinforcement component values.

Defender:
Value = (Number of attacked suit cards in the defender’s corresponding army) + (Number of matching attacked suit cards in hand)
(No subtraction is applied.)

5.4.3 Outcome
If the Attacker’s Total is Higher:
The attacker wins the war. They keep all cards committed to the war, and the defender must discard their entire army for the attacked suit to the discard pile.

If the Defender’s Total is Higher or Tied:
The defender wins the war. They keep their attacked suit army intact, while the attacker discards all armies committed to the war (including any reinforcements).

6. Turn Order & Continuation
The winner of a duel becomes the starting player for the next turn.

Each turn begins by flipping a new card from the draw pile (which might be subject to the King rule as noted).

7. The Draw & Discard Piles
Drawing Cards:
After each play or duel, players draw from the draw pile until they have 3 cards in hand (if cards remain).

Discarding Cards:
Cards lost in duels or from war outcomes go to the discard pile.

Reshuffling:
When the draw pile is exhausted, shuffle the discard pile to form a new draw pile.

8. Winning the Game
The game continues through duels and war declarations until one player meets the victory condition:

Victory Condition:
A player wins when they maintain at least one card (i.e. an established army) in all four suits, while their opponent is missing an army in at least one suit.

9. Additional Clarifications
Bluffing:
You may play a card that does not actually beat the revealed card by number and suit. If your bluff is called, both you and your opponent reveal the contested cards and the duel resolves accordingly.

Army Formation & Card Orientation:

When forming a new army, the first collected card is placed face up to indicate the suit.

Subsequent cards added to that army are placed face down.

Wild Card (King) Recap:

Using a King:
At any point in a duel, if the revealed card (or current required play) is, say, a spade (e.g., spade 5), you may opt to play a King as a wild card—but only if that King comes from your hand or from your spade army.

Procedure:
When playing the wild King, place it face down and declare it as the “spade King” (using the suit of the drawn card). Then, immediately play an additional card from your hand, declaring its suit and value (this declaration may be a bluff).

Calling Bluffs:
Your opponent may call your bluff regarding one or both declarations, triggering a reveal.

Drawn King Exception:
If a King is revealed from the draw pile at the start of a duel, you do not play on with that King. Instead, draw another card from the draw pile—the duel is then played with that new card. The drawn King is reserved and awarded to the winner along with the card used.

House Rules & Variants:
Once familiar with these base mechanics, players are encouraged to experiment with house rules (for example, adjusting reinforcement limits or bluffing protocols).
