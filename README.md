# Element Escape: Twin Spirits

Hey there! Welcome to Element Escape - a fun puzzle game where you help two spirits escape!

## What This Game is About

You're a game developer (well, student!) who created this puzzle game for COMP9001. The game has two cool spirits - a Fire Spirit and a Water Spirit - and they need your help to find their way out!

### Quick Summary
- Guide the Fire Spirit (`F`) to the orange exit (`A`)
- Guide the Water Spirit (`W`) to the purple exit (`B`)
- Collect keys, flip switches, avoid hazards, and solve puzzles!
- Works great for learning Python and game development basics

## How to Play

### Getting Started
Just open your terminal and run:
```bash
python3 main.py
```

That's it! No extra libraries needed - it uses Python's built-in `tkinter` for the graphics.

### Choose Your Mode
When you start, pick one of these:
- **Two-Player Mode** - Control both spirits and switch between them
- **Single-Player Mode** - Control just one spirit

### Game Controls

**With Mouse:**
- Click the arrow buttons to move
- Click "Switch Spirit" to change which one you're controlling
- Click "Restart Level" if you get stuck

**With Keyboard (faster!):**
- `W` = Move up
- `A` = Move left
- `S` = Move down
- `D` = Move right
- `SPACE` = Switch between Fire and Water
- `Ctrl+Z` = Undo (go back a move)
- `Ctrl+Y` = Redo (go forward again)

## Tile Types (What Each Symbol Means)

| Tile | What It Does |
|------|--------------|
| `#` | Wall - can't move through this |
| `.` | Empty space - safe to walk on |
| `F` | Fire Spirit starting spot |
| `W` | Water Spirit starting spot |
| `A` | Fire Spirit's exit (goal!) |
| `B` | Water Spirit's exit (goal!) |
| `K` | Key - pick this up to open doors |
| `D` | Door - need a key to pass |
| `S` | Switch - press this to activate things |
| `X` | Fire hazard - dangerous for Water Spirit! |
| `O` | Water hazard - dangerous for Fire Spirit! |

## Cool Features We've Added

### Achievement System
Unlock achievements as you play! Some examples:
- First Step - Complete your first level
- Speed Runner - Finish a level in under 60 seconds
- Ice Breaker - Slide on ice tiles
- Teleporter Traveler - Use warp portals

Check your achievements anytime by clicking the "Achievements" button!

### Animations
We added smooth animations to make the game feel more alive:
- Sprite movement animation when spirits move
- Particle effects when collecting items
- Celebration burst when you win!
- Spinning warp effect for teleporters

### Undo/Redo
Made a mistake? No problem! Press `Ctrl+Z` to undo your last move. Experiment freely without starting over!

### Level Editor
Want to create your own puzzles? Click "Level Editor" and design your own levels! Save them as `.txt` files and play them later.

### Progress Tracking
Your game progress is automatically saved, so come back anytime and pick up where you left off!

## Example Levels You Can Create

Basic maze:
```
###########
#F.....A.#
#.#####.#
#.......#
#W.....B#
###########
```

With hazards:
```
###########
#F.X.....A#
#.......#
#W.O....B#
###########
```

With keys and doors:
```
###########
#F...K...A#
#...#D#..#
#W.......B#
###########
```

## Difficulty Levels

- **Easy** - Start here! Learn the basics
- **Medium** - Gets trickier, more puzzles to solve
- **Hard** - For experts only! Challenge yourself

## Running the Tests

Want to make sure everything works? Run our test suite:

```bash
python3 -m unittest test_main.py
python3 -m unittest test_puzzle_mechanics.py
python3 -m unittest test_achievements.py
```

All tests should pass! (We've got 63 tests covering all the cool features)

## Project Structure

Here's how the code is organized (nice and tidy!):

```
main.py                 - All the game logic
test_main.py           - Tests for basic game features
test_puzzle_mechanics.py - Tests for teleporters, ice, switches
test_achievements.py  - Tests for achievement system
game_progress.json    - Your saved progress (auto-created)
achievements.json     - Your unlocked achievements (auto-created)
run.py                 - Quick launcher script
```

## Why We Wrote It This Way

This project is designed to be easy to understand:

- **Clear names** - Variables and functions are named to explain themselves
- **Lots of comments** - We explain *why* the code does things, not just *what*
- **Modular design** - Each class has one job, making it easier to follow
- **No fancy tricks** - Just plain Python, nothing too fancy

## Want to Extend It?

Here are some ideas for adding more features:

1. **Sound effects** - Add move sounds, collect sounds, victory music!
2. **More levels** - Create a whole adventure map
3. **Hint system** - Give players a nudge when they're stuck
4. **Leaderboard** - Compete with friends!
5. **Mobile version** - Port it to Kivy for phones

Have fun playing! And remember - if you get stuck, just use Undo and try again. That's what it's there for! 😄
