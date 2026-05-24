# Element Escape: Twin Spirits

A puzzle game where students guide Fire and Water spirits to their exits by solving puzzles, collecting keys, activating switches, and avoiding hazards.

## Project Overview

This is a final project for COMP9001 (Computer Science). The game includes:
- 6 built-in levels across 3 difficulties: easy, medium, and hard
- Graphical interface using tkinter (no extra libraries needed)
- Mouse buttons + keyboard controls
- Two-player cooperative mode and single-player mode
- Puzzle mechanics with keys, doors, switches, and hazards
- Move counter, timer, and win confirmation

## New Features (High-Priority Enhancements)

### 1. **Achievement and High Score System**
- Automatically records best moves and fastest times for each level
- Shows completion status with stars (★) in the level selection window
- Tracks overall progress percentage
- Data is saved to `game_progress.json` for future sessions

### 2. **Undo/Redo Functionality**
- Go back to previous moves without restarting the level
- Explore different strategies and learn from mistakes
- Perfect for students to experiment with puzzle solutions
- Keyboard shortcuts: `Ctrl+Z` to undo, `Ctrl+Y` to redo

### 3. **Level Editor**
- Create custom levels with a built-in editor
- Validate levels before saving
- Export as text files that can be loaded with "Load Custom Level"
- Student-friendly interface with clear tile legends

### 4. **Improved Level Management**
- See which levels you've completed
- View your best moves and fastest times
- Progress bar shows completion percentage
- Easy navigation between built-in and custom levels

## How to Run

### Prerequisites
- Python 3.7 or higher
- tkinter installed with Python

### Start the game

Run:
```bash
python3 main.py
```

The game will open a mode selection window first. Then choose difficulty and level.

## Game Features

### Controls

**Mouse Controls:**
- `↑ UP`, `← LEFT`, `↓ DOWN`, `→ RIGHT` buttons move the selected spirit
- `Switch Spirit` changes control between Fire and Water spirits in two-player mode
- `Restart Level` resets the current level
- `Change Level` opens the level selection screen
- `Load Custom Level` opens a custom level file
- `Level Editor` creates new levels
- `Undo` and `Redo` to explore different moves
- `Help` shows game instructions
- `Quit` exits the game

**Keyboard Controls:**
- `W/A/S/D` to move up/left/down/right
- `SPACE` to switch spirits in two-player mode
- `Ctrl+Z` to undo a move
- `Ctrl+Y` to redo a move

### Game Modes

**Two-Player Mode:**
Control both Fire and Water spirits. Switch between them and coordinate their movements to solve puzzles.

**Single-Player Mode:**
Choose to control either Fire or Water spirit exclusively.

### Difficulty Levels

- **Easy:** Perfect for learning the game and understanding mechanics
- **Medium:** Standard puzzles requiring coordination and planning
- **Hard:** Expert challenges with complex mazes and hazards

### Tile Meanings

- `#` = Wall (impassable)
- `.` = Empty space
- `F` = Fire Spirit starting position
- `W` = Water Spirit starting position
- `A` = Fire Spirit exit
- `B` = Water Spirit exit
- `K` = Key (collect to open doors)
- `D` = Door (needs key to pass)
- `S` = Switch (activates puzzles)
- `X` = Fire hazard (dangerous to Water Spirit)
- `O` = Water hazard (dangerous to Fire Spirit)

## How to Use New Features

### Checking Your Progress
When you select a level, you'll see:
- A star (★) next to completed levels
- Your best move count and time if you've completed it
- Overall completion percentage at the top

### Using Undo/Redo
1. Make a move that you want to reverse
2. Click "Undo" or press `Ctrl+Z` to go back
3. Click "Redo" or press `Ctrl+Y` to go forward
4. Experiment without fear of losing progress!

### Creating Custom Levels
1. Click "Level Editor" to open the editor
2. Enter a level name and description
3. Design your level map using the tile symbols
4. Click "Save Level" to create a `.txt` file
5. Use "Load Custom Level" to play your creation

### Examples of Level Patterns
```
Simple maze:
###########
#F.....A.#
#.#####.#
#.......#
#W.....B#
###########

With hazards:
###########
#F.X.....A#
#.......#
#W.O....B#
###########

With keys and doors:
###########
#F...K...A#
#...#D#..#
#W.......B#
###########
```

## Demo Flow for Teacher Presentation

1. Run `python3 main.py`
2. Choose **Two-Player Mode** or **Single-Player Mode**
3. Pick a difficulty level (Easy, Medium, Hard)
4. Select a built-in level and press **Start Game**
5. Use the arrow buttons or `W/A/S/D` to move
6. In two-player mode, press `SPACE` or click **Switch Spirit** to change control
7. Use **Undo** and **Redo** to demonstrate puzzle exploration
8. When the level is finished, view your achievement in the progress bar
9. Use **Level Editor** to create a new custom level live
10. Use **Change Level** to play a different puzzle

## Code Structure

### Main Classes

**Player:** Represents a spirit on the game map with position and attributes.

**Level:** Manages the game map, player positions, and game rules.

**GameProgress:** Tracks achievements and high scores using JSON file storage.

**GameState:** Manages undo/redo history for exploring different strategies.

**GUIGame:** Builds and controls the graphical user interface.

## Student-Friendly Code Features

- Clear, descriptive variable and function names
- Comprehensive comments explaining game logic
- Modular design with separated concerns
- Easy-to-understand data structures
- No advanced Python features (no metaclasses, decorators, etc.)

## Testing

Run the unit tests to verify everything works:
```bash
python3 -m unittest test_main.py
```

All 31 tests cover:
- Player creation and movement
- Level validation and loading
- Game win conditions
- Tile effects and hazards
- Custom level loading

## Future Enhancement Ideas

- Sound effects for moves and achievements
- Leaderboard for worldwide competition
- Level difficulty rating system
- Step-by-step solution hints
- Mobile version using Kivy
- Multiplayer online mode

Enjoy the game!

**Keyboard Shortcuts:**
- `W` = Up
- `A` = Left
- `S` = Down
- `D` = Right
- `SPACE` = Switch Spirit

## Game Rules

### Objective
- Guide Fire Spirit (`F`) to exit `A`
- Guide Water Spirit (`W`) to exit `B`
- In two-player mode, both spirits must reach their exits
- In single-player mode, only the selected spirit must reach its exit

### Tiles
- `#` = Wall (cannot move through)
- `.` = Empty space
- `F` = Fire Spirit start
- `W` = Water Spirit start
- `A` = Fire exit
- `B` = Water exit
- `K` = Key
- `D` = Door
- `S` = Switch
- `X` = Fire hazard (bad for Water Spirit)
- `O` = Water hazard (bad for Fire Spirit)

### Mechanics

- Collect **keys** to open doors
- Step on **switches** to activate puzzle elements
- Avoid hazard tiles specific to each spirit
- The game shows a **move counter** in the status bar
- On success, the game shows a completion pop-up with moves used

## Code Structure

### Main Classes

**Player**
- Saves a spirit's name, symbol, exit symbol, forbidden tile, and position
- `update_position()` moves the spirit to a new location

**Level**
- Loads maps and checks game rules
- Identifies player start positions
- Validates moves, applies tile effects, and checks win conditions

**GUIGame**
- Builds the GUI with tkinter
- Handles user input and game display
- Shows mode and level selection screens
- Updates move count and feedback messages

### Files
- `main.py` – main game code
- `test_main.py` – unit tests for game logic
- `run.py` – easy launch menu for game or tests
- `run.sh` – shell launcher for Linux/macOS

## Teacher Notes

- The game is easy to launch with `python3 main.py`
- It uses only Python built-in libraries
- It is written in a student-friendly style with clear comments
- The game includes a move counter and win confirmation
- The level selection screen and mode menu make it easy to demo

## Testing

Run:
```bash
python3 -m unittest test_main.py
```

## Future Ideas

- Add more levels
- Add sound effects
- Add a hint system
- Create a level editor
- Add a high-score board

## Author

Developed as a final project for COMP9001 (Computer Science)
Date: May 2026
- `level1.txt`, `level2.txt` (optional) - Custom level files

## Testing

The project includes unit tests covering:
- Grid validation (checking rectangular shape)
- Player initialization (correct player creation based on mode)
- Game state validation (demo mode defaults)

Run tests with:
```bash
python3 -m unittest test_main.py -v
```

Expected output: All tests pass (6/6)

## Project Features

### Implemented
✅ Graphical GUI using tkinter
✅ 6 built-in levels
✅ Two-player cooperative mode
✅ Single-player mode (future extension)
✅ Keyboard and mouse controls
✅ Level selection with difficulty
✅ Move counter
✅ Key/switch inventory system
✅ Win condition checking
✅ Help system
✅ Unit tests for core logic
✅ Student-friendly code with documentation

### Student-Friendly Design
- Clear variable names that explain their purpose
- Comprehensive docstrings for all classes and methods
- Comments explaining non-obvious logic
- Organized code structure with logical class separation
- No external dependencies (uses only Python standard library)

## Tips for Teachers and Demo

**For Classroom Demonstration:**
1. Run with `python3 main.py --demo` for a quick demonstration
2. This loads Easy Level 1, a simple introductory level
3. Demonstrate controls (buttons and keyboard shortcuts)
4. Show the level selection menu with `Change Level`
5. Explain the tile legend and game mechanics
6. Solve a level to show win condition

**For Student Understanding:**
- The code uses simple, clear Python patterns suitable for learning
- Each class has a single responsibility
- Methods are kept small and focused
- Comments explain the "why" not just the "what"
- Dataclasses simplify data management

## Future Enhancements

Possible improvements for future versions:
- Add more levels
- Implement level editor
- Add time limits
- Leaderboard system
- Different game modes
- Custom hazards
- Save/load game state

## Author Notes

This project demonstrates:
- Object-oriented programming (classes with specific responsibilities)
- GUI programming with tkinter
- Game logic implementation (collision detection, state management)
- Data validation and error handling
- Unit testing for reliability
- Documentation and code comments for clarity

## License

This is a student project created for educational purposes.

## Contact

For questions or feedback about this project, please refer to the course instructor.
