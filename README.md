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

