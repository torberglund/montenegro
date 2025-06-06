# King of Montenegro

This repository contains a minimal implementation of the card game **King of Montenegro** using `pygame`.

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

A window will open showing each player's hand. The game logic is largely text-driven: players enter commands in the terminal while the graphical window displays the cards. The implemented rules cover basic duels and collecting armies. The structure allows loading AI opponents in the future, but currently both players are human controlled.

This is a simplified reference implementation and does not cover every nuance from the full rule set, but it provides a starting point for further development.

