# Element Escape: Twin Spirits
# COMP9001 Final Project
# A puzzle game where players guide Fire and Water spirits to their exits
# using keys, switches, and avoiding hazards. GUI-based with clickable controls.
# Date: May 2026

import os
import time
import json
import copy
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataclasses import dataclass
from typing import Optional


class GameProgress:
    """
    Keep track of player achievements and high scores.
    Saves the data to a JSON file so progress is remembered between games.
    """
    
    def __init__(self, save_file='game_progress.json'):
        """Initialize and load any saved progress from file."""
        self.save_file = save_file
        self.progress_data = {
            'completed_levels': {},
            'best_moves': {},
            'best_times': {}
        }
        self.load_from_file()
    
    def load_from_file(self):
        """Read progress data from the JSON file if it exists."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    self.progress_data = json.load(f)
            except Exception:
                pass
    
    def save_to_file(self):
        """Write progress data to the JSON file."""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception:
            pass
    
    def mark_level_complete(self, difficulty, level_name, moves, elapsed_time):
        """Record that a level was completed with the given stats."""
        level_key = f"{difficulty}_{level_name}"
        
        if level_key not in self.progress_data['completed_levels']:
            self.progress_data['completed_levels'][level_key] = True
        
        if level_key not in self.progress_data['best_moves']:
            self.progress_data['best_moves'][level_key] = moves
        else:
            self.progress_data['best_moves'][level_key] = min(
                self.progress_data['best_moves'][level_key], moves
            )
        
        if level_key not in self.progress_data['best_times']:
            self.progress_data['best_times'][level_key] = elapsed_time
        else:
            self.progress_data['best_times'][level_key] = min(
                self.progress_data['best_times'][level_key], elapsed_time
            )
        
        self.save_to_file()
    
    def is_level_completed(self, difficulty, level_name):
        """Check if a level has been completed before."""
        level_key = f"{difficulty}_{level_name}"
        return self.progress_data['completed_levels'].get(level_key, False)
    
    def get_completion_rate(self):
        """Return the percentage of levels completed."""
        total_levels = 0
        for difficulty in ['easy', 'medium', 'hard']:
            levels = Level.DEFAULT_LEVELS.get(difficulty, {})
            total_levels += len(levels)
        
        if total_levels == 0:
            return 0
        
        completed = len(self.progress_data['completed_levels'])
        return int((completed / total_levels) * 100)
    
    def get_best_moves(self, difficulty, level_name):
        """Get the best move count for a level, or None if not completed."""
        level_key = f"{difficulty}_{level_name}"
        return self.progress_data['best_moves'].get(level_key)
    
    def get_best_time(self, difficulty, level_name):
        """Get the best time for a level, or None if not completed."""
        level_key = f"{difficulty}_{level_name}"
        return self.progress_data['best_times'].get(level_key)


class Achievement:
    """
    Represents a single achievement that players can unlock.
    Each achievement has a name, description, and unlock condition.
    """

    def __init__(self, achievement_id, name, description, icon):
        """Create a new achievement with the given details."""
        self.achievement_id = achievement_id
        self.name = name
        self.description = description
        self.icon = icon
        self.unlocked = False

    def __repr__(self):
        """Show achievement status when printing."""
        status = "Unlocked" if self.unlocked else "Locked"
        return f"Achievement: {self.name} ({status})"


class AchievementSystem:
    """
    Manage all achievements in the game.
    Tracks progress, unlocks achievements, and shows notifications to players.
    """

    # All available achievements in the game
    ACHIEVEMENT_DEFINITIONS = {
        'first_step': {
            'name': 'First Step',
            'description': 'Complete your first level!',
            'icon': '🎯'
        },
        'speed_demon': {
            'name': 'Speed Runner',
            'description': 'Complete any level in under 60 seconds!',
            'icon': '⚡'
        },
        'ice_breaker': {
            'name': 'Ice Breaker',
            'description': 'Slide on an ice tile for the first time!',
            'icon': '❄️'
        },
        'teleport_traveler': {
            'name': 'Teleporter Traveler',
            'description': 'Use a teleporter to warp across the map!',
            'icon': '🌀'
        },
        'key_collector': {
            'name': 'Key Collector',
            'description': 'Pick up your first key!',
            'icon': '🔑'
        },
        'switch_master': {
            'name': 'Switch Master',
            'description': 'Activate a switch to open a door!',
            'icon': '🔘'
        },
        'double_trouble': {
            'name': 'Double Trouble',
            'description': 'Activate two switches at once for a conditional door!',
            'icon': '🎮'
        },
        'halfway_there': {
            'name': 'Halfway Hero',
            'description': 'Complete 50% of all levels!',
            'icon': '🏆'
        },
        'completionist': {
            'name': 'Completionist',
            'description': 'Complete all levels in the game!',
            'icon': '🌟'
        },
        'perfect_moves': {
            'name': 'Perfect Moves',
            'description': 'Complete a level with under 20 moves!',
            'icon': '📊'
        },
        'fire_walker': {
            'name': 'Fire Walker',
            'description': 'Guide the Fire Spirit to safety!',
            'icon': '🔥'
        },
        'water_walker': {
            'name': 'Water Walker',
            'description': 'Guide the Water Spirit to safety!',
            'icon': '💧'
        },
        'one_time_use': {
            'name': 'One Time Use',
            'description': 'Activate a one-time switch!',
            'icon': '⏰'
        },
        'perfect_balance': {
            'name': 'Perfect Balance',
            'description': 'Complete a level with exactly the same moves as your best!',
            'icon': '⚖️'
        }
    }

    def __init__(self, save_file='achievements.json'):
        """Initialize the achievement system and load saved progress."""
        self.save_file = save_file
        self.achievements = {}
        self.newly_unlocked = []  # Track newly unlocked for notification
        self._initialize_achievements()
        self.load_from_file()

    def _initialize_achievements(self):
        """Create all achievement objects from the definitions."""
        for achievement_id, details in self.ACHIEVEMENT_DEFINITIONS.items():
            self.achievements[achievement_id] = Achievement(
                achievement_id,
                details['name'],
                details['description'],
                details['icon']
            )

    def load_from_file(self):
        """Load unlocked achievements from the save file."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    unlocked_list = data.get('unlocked_achievements', [])
                    for achievement_id in unlocked_list:
                        if achievement_id in self.achievements:
                            self.achievements[achievement_id].unlocked = True
            except Exception:
                pass

    def save_to_file(self):
        """Save unlocked achievements to the save file."""
        try:
            data = {
                'unlocked_achievements': [
                    aid for aid, ach in self.achievements.items()
                    if ach.unlocked
                ]
            }
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def unlock(self, achievement_id):
        """Try to unlock an achievement. Returns True if newly unlocked."""
        if achievement_id not in self.achievements:
            return False

        achievement = self.achievements[achievement_id]
        if not achievement.unlocked:
            achievement.unlocked = True
            self.newly_unlocked.append(achievement)
            self.save_to_file()
            return True
        return False

    def get_unlocked_count(self):
        """Return how many achievements have been unlocked."""
        return sum(1 for ach in self.achievements.values() if ach.unlocked)

    def get_total_count(self):
        """Return the total number of achievements."""
        return len(self.achievements)

    def get_newly_unlocked(self):
        """Get list of achievements that were just unlocked this session."""
        achievements = self.newly_unlocked.copy()
        self.newly_unlocked = []
        return achievements

    def check_achievement(self, achievement_id):
        """Manually trigger an achievement check (for testing)."""
        return self.unlock(achievement_id)


class AnimationController:
    """
    Controls all animations in the game.
    Provides smooth visual feedback for player actions.
    """

    def __init__(self):
        """Initialize the animation controller with default settings."""
        self.animations_enabled = True
        self.animation_speed = 1.0  # Multiplier for animation speed
        self.current_animations = []  # Track running animations

    def animate_sprite_movement(self, canvas, sprite_id, start_x, start_y,
                                 end_x, end_y, duration=200):
        """
        Animate a sprite moving from one position to another.
        This makes movement feel more dynamic and fun!
        """
        if not self.animations_enabled:
            # If animations are off, just move instantly
            canvas.coords(sprite_id, end_x - 15, end_y - 15, end_x + 15, end_y + 15)
            return

        # Calculate how many steps to use for smooth animation
        steps = 10
        step_duration = int(duration / steps)
        delta_x = (end_x - start_x) / steps
        delta_y = (end_y - start_y) / steps

        def animate_step(step):
            """Move the sprite one step closer to the target."""
            if step < steps:
                new_x = start_x + (delta_x * step)
                new_y = start_y + (delta_y * step)
                canvas.coords(sprite_id, new_x - 15, new_y - 15, new_x + 15, new_y + 15)
                # Schedule the next step
                canvas.after(step_duration, lambda: animate_step(step + 1))
            else:
                # Animation complete, ensure final position
                canvas.coords(sprite_id, end_x - 15, end_y - 15, end_x + 15, end_y + 15)

        animate_step(0)

    def animate_teleporter_warp(self, canvas, x, y, callback=None):
        """
        Animate a teleporter warp effect.
        Creates a spinning/vanishing effect when teleporting!
        """
        if not self.animations_enabled:
            if callback:
                callback()
            return

        # Create a temporary warp effect circle
        # Use a list to store the warp effect so it can be modified in nested function
        radius = 20
        warp_effect_id = [canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                             fill='#8e44ad', outline='#fff', width=2)]
        angle = [0]  # Track rotation angle for animation

        def spin_effect():
            """Make the warp effect spin and fade."""
            if angle[0] < 360:
                # Delete the old effect
                canvas.delete(warp_effect_id[0])
                # Calculate new size for shrinking effect
                current_radius = radius - (angle[0] / 18)
                if current_radius > 0:
                    # Create new smaller effect
                    warp_effect_id[0] = canvas.create_oval(
                        x - current_radius, y - current_radius,
                        x + current_radius, y + current_radius,
                        fill='#8e44ad', outline='#fff', width=2
                    )
                angle[0] += 30
                canvas.after(30, spin_effect)
            else:
                # Clean up and call callback
                canvas.delete(warp_effect_id[0])
                if callback:
                    callback()

        spin_effect()

    def animate_collect_item(self, canvas, x, y, item_type='key'):
        """
        Animate collecting an item (key, switch, etc).
        Shows a little sparkle or particle effect!
        """
        if not self.animations_enabled:
            return

        colors = {
            'key': '#f1c40f',
            'switch': '#27ae60',
            'onetime': '#2ecc71',
            'teleporter': '#9b59b6'
        }
        color = colors.get(item_type, '#fff')

        # Create sparkle particles
        particles = []
        for i in range(8):
            angle = i * 45
            px = x + 10 * (angle / 45)
            py = y + 10 * (angle / 45)
            particle = canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                                          fill=color, outline='')
            particles.append(particle)

        # Animate particles flying outward
        step = [0]  # Use list to track step number

        def animate_particle_step():
            """Move particles outward from center."""
            if step[0] < 5:
                for i, particle in enumerate(particles):
                    angle = i * 45
                    distance = step[0] * 8
                    px = x + distance * (angle / 45)
                    py = y + distance * (angle / 45)
                    canvas.coords(particle, px - 3, py - 3, px + 3, py + 3)
                step[0] += 1
                canvas.after(50, animate_particle_step)
            else:
                # Clean up particles
                for particle in particles:
                    canvas.delete(particle)

        animate_particle_step()

    def animate_level_complete(self, canvas, grid_width, grid_height, tile_size):
        """
        Play a celebration animation when completing a level!
        Shows a burst of colorful particles.
        """
        if not self.animations_enabled:
            return

        import random
        # Create celebration particles
        celebration_colors = ['#e74c3c', '#3498db', '#f1c40f', '#2ecc71', '#9b59b6', '#e67e22']

        for i in range(30):
            # Random starting position near center
            start_x = random.randint(grid_width * tile_size // 2 - 50,
                                    grid_width * tile_size // 2 + 50)
            start_y = random.randint(grid_height * tile_size // 2 - 50,
                                    grid_height * tile_size // 2 + 50)

            color = celebration_colors[i % len(celebration_colors)]
            particle = canvas.create_oval(start_x - 5, start_y - 5,
                                           start_x + 5, start_y + 5,
                                           fill=color, outline='')

            # Animate upward and outward
            def animate_celebration(p):
                """Make particle fly upward with some randomness."""
                for step in range(10):
                    canvas.move(p, random.randint(-5, 5), -10)
                canvas.after(50, lambda: canvas.delete(p))

            # Stagger the animations for a cascading effect
            canvas.after(random.randint(0, 500), lambda p=particle: animate_celebration(p))

    def animate_hazard_warning(self, canvas, sprite_id):
        """
        Flash the sprite when it's about to hit a hazard.
        This gives players a visual warning!
        """
        if not self.animations_enabled:
            return

        flash_count = [0]

        def flash():
            """Toggle the outline color to create flash effect."""
            if flash_count[0] < 6:
                # Alternate between red and normal
                if flash_count[0] % 2 == 0:
                    canvas.itemconfig(sprite_id, outline='#e74c3c', width=3)
                else:
                    canvas.itemconfig(sprite_id, outline='black', width=2)
                flash_count[0] += 1
                canvas.after(100, flash)
            else:
                # Reset to normal
                canvas.itemconfig(sprite_id, outline='black', width=2)

        flash()


class GameState:
    """
    Keep track of the game state so we can undo and redo moves.
    This helps students explore different strategies without losing progress.
    """
    
    def __init__(self):
        """Start with an empty history."""
        self.history = []
        self.current_index = -1
    
    def save_state(self, level, moves, fire_pos, water_pos, has_key):
        """Save the current game state to the history."""
        state = {
            'grid': copy.deepcopy(level.grid),
            'moves': moves,
            'fire_pos': fire_pos,
            'water_pos': water_pos,
            'has_key': has_key,
            'switch_activated': level.switch_activated,
            'one_time_switches': copy.deepcopy(level.one_time_switches),
            'activated_one_time_switches': copy.deepcopy(level.activated_one_time_switches),
            'conditional_switches_active': copy.deepcopy(level.conditional_switches_active),
            'consumed_keys': copy.deepcopy(level.consumed_keys),
            'consumed_switches': copy.deepcopy(level.consumed_switches)
        }

        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]

        self.history.append(state)
        self.current_index += 1
    
    def can_undo(self):
        """Check if there is a previous state to go back to."""
        return self.current_index > 0
    
    def can_redo(self):
        """Check if there is a next state to go forward to."""
        return self.current_index < len(self.history) - 1
    
    def undo(self):
        """Go back to the previous state."""
        if self.can_undo():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def redo(self):
        """Go forward to the next state."""
        if self.can_redo():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def clear(self):
        """Clear all history when starting a new level."""
        self.history = []
        self.current_index = -1


# Player class holds a spirit's current state and map position
@dataclass

class Player:
    """Keep the player's current position and what they can do."""
    name: str
    symbol: str
    exit_symbol: str
    forbidden_tile: str
    row: int = 0
    col: int = 0

    def update_position(self, new_row, new_col):
        """Update the player's position on the map."""
        self.row = new_row
        self.col = new_col


# Level class holds the map and checks the game rules
class Level:
    """Hold the map and game rules for one level."""

    # Tile symbols legend explaining what each symbol means
    TILE_LEGEND = {
        '#': 'Wall',
        '.': 'Empty space',
        'F': 'Fire Spirit start',
        'W': 'Water Spirit start',
        'A': 'Fire exit',
        'B': 'Water exit',
        'K': 'Key',
        'D': 'Door',
        'S': 'Switch',
        'X': 'Fire hazard (dangerous to Water Spirit)',
        'O': 'Water hazard (dangerous to Fire Spirit)',
        'T': 'Teleporter entrance',
        'E': 'Teleporter exit',
        'I': 'Ice tile (slippery - slide until hitting wall)',
        '1': 'One-time switch (can only press once)',
        'C': 'Conditional door (needs two switches activated)'
    }

    # Built-in levels organized by difficulty for easy access
    DEFAULT_LEVELS = {
        'easy': {
            'Easy Level 1': {
                'description': 'Basic tutorial level to learn controls and mechanics. Perfect for beginners!',
                'map': [
                    "###########",
                    "#F..K....A#",
                    "#...#.....#",
                    "#..##.##..#",
                    "#..S..#...#",
                    "#..##.##..#",
                    "#W..D....B#",
                    "###########"
                ]
            },
            'Easy Level 2': {
                'description': 'Practice navigating multiple paths and using switches effectively.',
                'map': [
                    "###########",
                    "#F.....K.A#",
                    "#..##.##..#",
                    "#..#....#.#",
                    "#..#..S.#.#",
                    "#..#..##..#",
                    "#W.D.....B#",
                    "###########"
                ]
            },
            'Easy Level 3': {
                'description': 'Learn about teleporters! Find the hidden portals to reach the exits.',
                'map': [
                    "###########",
                    "#F.T.....A#",
                    "#.........#",
                    "#.E.#####.#",
                    "#.........#",
                    "#W.T.....B#",
                    "#...E.....#",
                    "###########"
                ]
            }
        },
        'medium': {
            'Medium Level 1': {
                'description': 'Standard puzzle with keys, doors, and fire hazards. Coordination between spirits is important.',
                'map': [
                    "###############",
                    "#F...K......A.#",
                    "#.#.###.#.#.#.#",
                    "#.#.#...#.#.#.#",
                    "#.#.#.#.#.#.#.#",
                    "#.#S#.#.#...#.#",
                    "#.#.#.###.###.#",
                    "#X...#.....#B.#",
                    "####.#.###.#..#",
                    "#W..D.#...#..B#",
                    "#....#....#...#",
                    "###############"
                ]
            },
            'Medium Level 2': {
                'description': 'More complex puzzle requiring careful planning of both spirits movements.',
                'map': [
                    "###############",
                    "#F......K..A..#",
                    "#.#.#.###.#.#.#",
                    "#.#.#...#.#.#.#",
                    "#.#.#.#.#.#.#.#",
                    "#.#.#.#...#...#",
                    "#...#.###.###.#",
                    "#.#.#O..#.....#",
                    "#.#.###.#.###.#",
                    "#W...D....#..B#",
                    "#....###....#.#",
                    "###############"
                ]
            },
            'Medium Level 3': {
                'description': 'Master the ice mechanic! Slide carefully to reach the exits without falling into hazards.',
                'map': [
                    "###############",
                    "#F.....I.....A#",
                    "#.III.#I####..#",
                    "#....S#.....#.#",
                    "#.III.#.###...#",
                    "#.....#.....#.#",
                    "#.###.#.###...#",
                    "#.I.I.#...I...#",
                    "#.I.I.#.###.#.#",
                    "#W.I.I...I..B.#",
                    "#.###...#.....#",
                    "###############"
                ]
            }
        },
        'hard': {
            'Hard Level 1': {
                'description': 'Complex maze with multiple hazards and challenging coordination. Expert players only!',
                'map': [
                    "###################",
                    "#F.....X.........A#",
                    "#.#..#.#.##.#.#.###",
                    "#.#.#.#.#..#.#....#",
                    "#.#S#.#.#.##.#.##.#",
                    "#...##...#..#.#...#",
                    "#.#.#####.###.###.#",
                    "#..O........#...#.#",
                    "##.###.#.###.##.###",
                    "#WK.D.#.....#....B#",
                    "#....#...##....B..#",
                    "###################"
                ]
            },
            'Hard Level 2': {
                'description': 'Ultimate challenge with intricate paths and deadly hazards. Test your skills!',
                'map': [
                    "###################",
                    "#F.....X.........A#",
                    "#K#..#.#.##.#.#.###",
                    "#.#.#.#.#..#.#....#",
                    "#.#S#.#.#.##.#.##.#",
                    "#...##...#..#.#...#",
                    "#.#.#####.###.###.#",
                    "#..O........#...#.#",
                    "##.###.#.###.##.###",
                    "#W..D.#.....#....B#",
                    "#....#...##....B..#",
                    "###################"
                ]
            },
            'Hard Level 3': {
                'description': 'Ultimate puzzle! Use conditional doors by pressing both switches to open the path.',
                'map': [
                    "###################",
                    "#F......S.......A.#",
                    "#.#######.#######.#",
                    "#.......#.#.......#",
                    "#.#####.#.#.#####.#",
                    "#.#.1.#.#.#.#.1.#.#",
                    "#.#...#.#.#.#...#.#",
                    "#.#####C#.#C#####.#",
                    "#.................#",
                    "#W................#",
                    "#................B#",
                    "###################"
                ]
            }
        }
    }

    def __init__(self):
        """Initialize an empty level with no players or map."""
        self.grid = []
        self.fire_player: Optional[Player] = None
        self.water_player: Optional[Player] = None
        self.has_key = False
        self.switch_activated = False

        # Puzzle mechanics storage
        self.teleporters = {}  # Maps entrance position to exit position
        self.one_time_switches = set()  # Positions of one-time switches on the map
        self.activated_one_time_switches = set()  # Which one-time switches have been pressed
        self.all_switches_pressed = []  # List of all switch positions for conditional logic
        self.conditional_switches_active = {}  # Tracks state of conditional switches
        self.conditional_doors = set()  # Positions of conditional doors
        self.ice_tiles = set()  # Set of ice tile positions

        # Track last teleport to avoid issues when spirits land on same tile
        self.last_teleport = None

        # Track which tiles have been consumed by effects (for visual feedback)
        self.consumed_keys = set()  # Positions where keys have been collected
        self.consumed_switches = set()  # Positions where one-time switches were activated

        # Track which conditional doors are currently open (derived from switch state)
        self._open_conditional_doors = set()  # Internal tracking of open doors

    def _parse_grid_from_lines(self, lines):
        """Turn each text line into a row of tiles."""
        self.grid = []
        for line in lines:
            self.grid.append(list(line))

    def validate_grid_shape(self):
        """Make sure every row has the same number of columns."""
        if not self.grid:
            raise ValueError("Grid is empty.")
        first_row_length = len(self.grid[0])
        for row_idx, row in enumerate(self.grid):
            if len(row) != first_row_length:
                raise ValueError(
                    f"Row {row_idx} has {len(row)} columns, but expected {first_row_length}."
                )

    def load_file(self, file_path):
        """Read a level map from a text file."""
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        with open(file_path, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        self._parse_grid_from_lines(lines)
        self.validate_grid_shape()

    @classmethod
    def get_default_map(cls, difficulty='medium', level_name=None):
        """Return the built-in map for a chosen level."""
        difficulty_levels = cls.DEFAULT_LEVELS.get(difficulty, cls.DEFAULT_LEVELS['medium'])
        if level_name in difficulty_levels:
            return difficulty_levels[level_name]['map']
        return next(iter(difficulty_levels.values()))['map']

    @classmethod
    def get_default_description(cls, difficulty='medium', level_name=None):
        """Return the description for a chosen built-in level."""
        difficulty_levels = cls.DEFAULT_LEVELS.get(difficulty, cls.DEFAULT_LEVELS['medium'])
        if level_name in difficulty_levels:
            return difficulty_levels[level_name].get('description', '')
        return next(iter(difficulty_levels.values())).get('description', '')

    def load_default_level(self, difficulty='medium', mode='two', controlled_spirit='fire', level_name=None):
        """Load a built-in level by difficulty and name."""
        default_map = self.get_default_map(difficulty, level_name)
        self._setup_new_level(default_map, mode, controlled_spirit)

    def _setup_new_level(self, map_lines, mode='two', controlled_spirit='fire'):
        """Load the map, check it, and reset the level state."""
        self._parse_grid_from_lines(map_lines)
        self.validate_grid_shape()
        self.has_key = False
        self.switch_activated = False

        # Reset puzzle mechanics for the new level
        self.teleporters = {}
        self.one_time_switches = set()
        self.activated_one_time_switches = set()
        self.all_switches_pressed = []
        self.conditional_switches_active = {}
        self.conditional_doors = set()
        self.ice_tiles = set()
        self.last_teleport = None
        self.consumed_keys = set()
        self.consumed_switches = set()
        self._open_conditional_doors = set()

        # Find and pair teleporters, collect ice tiles and switches
        self._setup_puzzle_mechanics()

        self.find_players(mode, controlled_spirit)

    def _update_conditional_doors(self):
        """
        Update which conditional doors are open based on activated switches.
        A conditional door opens when at least 2 switches (regular or one-time) are active.
        """
        self._open_conditional_doors = set()

        # Count how many switches are currently activated
        active_count = sum(1 for pos in self.all_switches_pressed
                         if self.conditional_switches_active.get(pos, False))

        # If we have enough active switches, all conditional doors open
        if active_count >= 2:
            self._open_conditional_doors = set(self.conditional_doors)

    def is_conditional_door_open(self, row, col):
        """Check if a conditional door at position is currently open."""
        pos = (row, col)
        if pos not in self.conditional_doors:
            return False
        # Update the door state based on current switch activation
        self._update_conditional_doors()
        return pos in self._open_conditional_doors

    def _setup_puzzle_mechanics(self):
        """Find and initialize all the new puzzle elements on the map."""
        teleporter_entrances = []
        teleporter_exits = []

        # Scan the grid for puzzle elements
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                # Collect teleporter entrances and exits
                if tile == 'T':
                    teleporter_entrances.append((row_idx, col_idx))
                elif tile == 'E':
                    teleporter_exits.append((row_idx, col_idx))

                # Collect ice tiles
                elif tile == 'I':
                    self.ice_tiles.add((row_idx, col_idx))
                elif tile == '1':
                    self.one_time_switches.add((row_idx, col_idx))
                    self.all_switches_pressed.append((row_idx, col_idx))
                elif tile == 'S':
                    self.all_switches_pressed.append((row_idx, col_idx))
                elif tile == 'C':
                    self.conditional_doors.add((row_idx, col_idx))

        # Pair teleporters: first entrance goes to first exit, etc.
        # Handle mismatched counts by truncating extras
        pair_count = min(len(teleporter_entrances), len(teleporter_exits))
        for i in range(pair_count):
            self.teleporters[teleporter_entrances[i]] = teleporter_exits[i]
    
    def find_players(self, mode='two', controlled_spirit='fire'):
        """Find where Fire and Water start on the map."""
        fire_pos = None
        water_pos = None
        self.fire_player = None
        self.water_player = None
        self.mode = mode
        self.controlled_spirit = controlled_spirit

        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == 'F':
                    fire_pos = (row_idx, col_idx)
                elif tile == 'W':
                    water_pos = (row_idx, col_idx)

        if mode == 'two':
            if fire_pos is None:
                raise ValueError("Fire Spirit start position 'F' is missing.")
            if water_pos is None:
                raise ValueError("Water Spirit start position 'W' is missing.")
            if fire_pos == water_pos:
                raise ValueError("Fire and Water cannot start on the same tile.")

            self.fire_player = Player(
                name="Fire Spirit",
                symbol='F',
                exit_symbol='A',
                forbidden_tile='O',
                row=fire_pos[0],
                col=fire_pos[1]
            )
            self.water_player = Player(
                name="Water Spirit",
                symbol='W',
                exit_symbol='B',
                forbidden_tile='X',
                row=water_pos[0],
                col=water_pos[1]
            )
        else:
            if controlled_spirit == 'fire':
                if fire_pos is None:
                    raise ValueError("Fire Spirit start position 'F' is missing.")
                self.fire_player = Player(
                    name="Fire Spirit",
                    symbol='F',
                    exit_symbol='A',
                    forbidden_tile='O',
                    row=fire_pos[0],
                    col=fire_pos[1]
                )
            else:
                if water_pos is None:
                    raise ValueError("Water Spirit start position 'W' is missing.")
                self.water_player = Player(
                    name="Water Spirit",
                    symbol='W',
                    exit_symbol='B',
                    forbidden_tile='X',
                    row=water_pos[0],
                    col=water_pos[1]
                )

    def is_valid_move(self, player, new_row, new_col):
        """Check if the player can move to the target tile."""
        if new_row < 0 or new_row >= len(self.grid):
            return False
        if new_col < 0 or new_col >= len(self.grid[0]):
            return False

        tile = self.grid[new_row][new_col]

        if tile == '#':
            return False
        if tile == player.forbidden_tile:
            return False
        if tile == 'D' and not self.has_key:
            return False

        # Conditional door needs two switches activated
        if tile == 'C':
            if not self.is_conditional_door_open(new_row, new_col):
                return False

        if self.fire_player and self.water_player:
            other_player = self.water_player if player == self.fire_player else self.fire_player
            if new_row == other_player.row and new_col == other_player.col:
                return False

        return True

    def slide_on_ice(self, player, direction):
        """
        Make the player slide on ice tiles until hitting an obstacle.
        This handles the ice tile mechanic with proper hazard checking.
        """
        current_row, current_col = player.row, player.col

        # Direction vectors for movement
        direction_map = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        delta_row, delta_col = direction_map.get(direction, (0, 0))

        # Keep sliding in the same direction until we hit an obstacle
        while True:
            next_row = current_row + delta_row
            next_col = current_col + delta_col

            # Check if next position is valid before moving
            if not self.is_valid_move(player, next_row, next_col):
                # Stop sliding here
                break

            # Move to the next position
            current_row, current_col = next_row, next_col

            # Check for hazard landing (spirit would be hurt)
            current_tile = self.grid[current_row][current_col]
            if current_tile == player.forbidden_tile:
                # Slid into a hazard - this is bad!
                # The player should not land on hazard tiles
                # Move back one step to last safe position
                current_row -= delta_row
                current_col -= delta_col
                break

            # Stop sliding if we reach a non-ice tile
            if current_tile != 'I':
                break

            # Apply any tile effects at this position (key, switch, teleporter)
            self.apply_tile_effect(player)
            # Update position after effects
            current_row, current_col = player.row, player.col

            # If teleported, stop the ice slide
            if self.last_teleport and (current_row, current_col) == self.last_teleport:
                self.last_teleport = None
                break

        # Update player position to final location
        player.update_position(current_row, current_col)

    def apply_tile_effect(self, player):
        """Apply special effects when the player moves onto a tile."""
        tile = self.grid[player.row][player.col]
        current_pos = (player.row, player.col)

        if tile == 'K':
            self.has_key = True
            self.grid[player.row][player.col] = '.'
            self.consumed_keys.add(current_pos)
        elif tile == 'D' and self.has_key:
            self.has_key = False
            self.grid[player.row][player.col] = '.'
        elif tile == 'S':
            self.switch_activated = True
            # Mark this switch as activated for conditional doors
            switch_pos = (player.row, player.col)
            self.conditional_switches_active[switch_pos] = True
        elif tile == '1':
            # One-time switch can only be pressed once
            switch_pos = (player.row, player.col)
            if switch_pos not in self.activated_one_time_switches:
                self.activated_one_time_switches.add(switch_pos)
                self.consumed_switches.add(switch_pos)
                self.switch_activated = True
                self.conditional_switches_active[switch_pos] = True
        elif tile == 'T':
            # Teleporter: move player to exit position
            # Only teleport if the entrance is in our valid pairs
            entrance_pos = (player.row, player.col)
            if entrance_pos in self.teleporters:
                exit_pos = self.teleporters[entrance_pos]
                # Check the exit tile is valid before teleporting
                exit_tile = self.grid[exit_pos[0]][exit_pos[1]]
                if exit_tile == 'E':
                    player.update_position(exit_pos[0], exit_pos[1])
                    self.last_teleport = exit_pos

    def check_win(self, mode='two', controlled_spirit='fire'):
        """Return True when the win condition is met."""
        if mode == 'two':
            if self.fire_player is None or self.water_player is None:
                return False
            fire_at_exit = (self.grid[self.fire_player.row][self.fire_player.col] == 'A')
            water_at_exit = (self.grid[self.water_player.row][self.water_player.col] == 'B')
            return fire_at_exit and water_at_exit

        if controlled_spirit == 'fire' and self.fire_player is not None:
            return self.grid[self.fire_player.row][self.fire_player.col] == 'A'
        if controlled_spirit == 'water' and self.water_player is not None:
            return self.grid[self.water_player.row][self.water_player.col] == 'B'
        return False


# The game window and how the player interacts with it
class GUIGame:
    """Build the GUI and control the game logic."""

    # Tile size for drawing each tile on the screen
    TILE_SIZE = 40
    
    # Map each tile symbol to a color
    COLORS = {
        '#': '#2c3e50',
        '.': '#ecf0f1',
        'F': '#e74c3c',
        'W': '#3498db',
        'A': '#f39c12',
        'B': '#9b59b6',
        'K': '#f1c40f',
        'D': '#95a5a6',
        'S': '#16a085',
        'X': '#e67e22',
        'O': '#1abc9c',
        'T': '#8e44ad',  # Purple for teleporter entrance
        'E': '#d35400',  # Orange for teleporter exit
        'I': '#3498db',  # Light blue for ice tiles
        '1': '#27ae60',  # Green for one-time switch
        'C': '#c0392b'   # Dark red for conditional door
    }

    def __init__(self, root):
        """Initialize the game with GUI components."""
        self.root = root
        self.root.title("Element Escape: Twin Spirits")
        self.root.geometry("900x950")
        self.root.resizable(False, False)

        # Game state variables
        self.level = Level()
        self.moves = 0
        self.current_difficulty = 'medium'
        self.level_name = None
        self.mode = 'two'
        self.controlled_spirit = 'fire'
        self.current_player_controlling = 'fire'
        self.custom_level_path = None
        self.custom_description = ''
        self.start_time = None
        self.timer_id = None
        
        # New features: progress tracking, undo/redo, and level editor
        self.progress = GameProgress()
        self.game_state = GameState()

        # Achievement system and animations for extra fun!
        self.achievements = AchievementSystem()
        self.animations = AnimationController()

        # UI tip widgets are created later in _build_ui; initialize attributes here
        # so static analyzers and students reading the code know they exist.
        self.tips_label = None
        self.show_tips_btn = None
        # Pre-declare common UI widget attributes to avoid "attribute unknown" warnings
        self.progress_label = None
        self.status_label = None
        self.description_label = None
        self.message_label = None
        self.canvas = None
        self.controls_frame = None
        self.actions_frame = None
        self.restart_button = None
        self.undo_button = None
        self.redo_button = None
        self.select_level_button = None
        self.custom_button = None
        self.editor_button = None
        self.help_button = None
        self.achievements_button = None
        self.quit_button = None

        # Track first-time events for achievements
        self.has_used_teleporter = False
        self.has_slid_on_ice = False
        self.has_collected_key = False
        self.has_activated_switch = False
        self.has_activated_onetime = False
        self.levels_completed_count = 0

        # Build the GUI layout
        self._build_ui()

        # Show game mode selection first
        self.show_game_mode_selection()

    def _build_ui(self):
        """Build the user interface components."""
        # Main container for the game screen
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title area at the top
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill=tk.X, pady=5)
        
        self.title_label = ttk.Label(title_frame, text="Element Escape: Twin Spirits", 
                                     font=("Arial", 18, "bold"))
        self.title_label.pack(side=tk.LEFT)

        # Progress display: shows overall completion and achievements
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.pack(fill=tk.X, pady=3)
        
        self.progress_label = ttk.Label(progress_frame, text="Progress: 0% | Levels Completed: 0/6", 
                                       font=("Arial", 9), foreground="green")
        self.progress_label.pack(side=tk.LEFT)

        # Status line for difficulty, moves, and items
        self.status_label = ttk.Label(self.main_frame, text="Loading level...", 
                                     font=("Arial", 10))
        self.status_label.pack(pady=5)

        # Description text for the current level
        self.description_label = ttk.Label(self.main_frame, text="", 
                                          font=("Arial", 9), foreground="gray")
        self.description_label.pack(pady=3)

        # Feedback line for the player, showing friendly status messages
        self.message_label = ttk.Label(self.main_frame, text="Choose a level to begin.",
                                       font=("Arial", 10), foreground="blue")
        self.message_label.pack(pady=2)

        # The map area where the game is drawn
        self.canvas = tk.Canvas(self.main_frame, bg='white', highlightthickness=1)
        self.canvas.pack(pady=10)

        # Movement buttons arranged in an arrow layout
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(fill=tk.X, pady=10)

        self.up_button = ttk.Button(self.controls_frame, text="↑ UP (W)", 
                                    command=lambda: self.move_player('up'))
        self.up_button.grid(row=0, column=1, padx=5, pady=5)

        self.left_button = ttk.Button(self.controls_frame, text="← LEFT (A)", 
                                      command=lambda: self.move_player('left'))
        self.left_button.grid(row=1, column=0, padx=5, pady=5)

        self.down_button = ttk.Button(self.controls_frame, text="↓ DOWN (S)", 
                                      command=lambda: self.move_player('down'))
        self.down_button.grid(row=1, column=1, padx=5, pady=5)

        self.right_button = ttk.Button(self.controls_frame, text="RIGHT (D) →", 
                                       command=lambda: self.move_player('right'))
        self.right_button.grid(row=1, column=2, padx=5, pady=5)

        # Switch player button for two-player mode
        self.switch_button = ttk.Button(self.controls_frame, text="Switch Spirit (SPACE)", 
                                       command=self.switch_controlled_spirit)
        self.switch_button.grid(row=0, column=3, padx=5, pady=5)

        # Action buttons for game controls
        self.actions_frame = ttk.Frame(self.main_frame)
        self.actions_frame.pack(fill=tk.X, pady=5)

        self.restart_button = ttk.Button(self.actions_frame, text="Restart Level", 
                                        command=self.restart_level)
        self.restart_button.pack(side=tk.LEFT, padx=3)

        # Undo/Redo buttons for exploring different strategies
        self.undo_button = ttk.Button(self.actions_frame, text="Undo (Ctrl+Z)", 
                                     command=self.undo_move)
        self.undo_button.pack(side=tk.LEFT, padx=3)

        self.redo_button = ttk.Button(self.actions_frame, text="Redo (Ctrl+Y)", 
                                     command=self.redo_move)
        self.redo_button.pack(side=tk.LEFT, padx=3)

        self.select_level_button = ttk.Button(self.actions_frame, text="Change Level", 
                                             command=self.show_level_selection)
        self.select_level_button.pack(side=tk.LEFT, padx=3)

        self.custom_button = ttk.Button(self.actions_frame, text="Load Custom Level", 
                                        command=self.load_custom_level)
        self.custom_button.pack(side=tk.LEFT, padx=3)

        # Editor button to create custom levels
        self.editor_button = ttk.Button(self.actions_frame, text="Level Editor", 
                                       command=self.show_level_editor)
        self.editor_button.pack(side=tk.LEFT, padx=3)

        self.help_button = ttk.Button(self.actions_frame, text="Help",
                                     command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=3)

        # Button to view achievements
        self.achievements_button = ttk.Button(self.actions_frame, text="Achievements",
                                              command=self.show_achievements)
        self.achievements_button.pack(side=tk.LEFT, padx=3)

        self.quit_button = ttk.Button(self.actions_frame, text="Quit",
                                     command=self.root.quit)
        self.quit_button.pack(side=tk.LEFT, padx=3)

        # Bind keyboard shortcuts for quick control
        self.root.bind('<w>', lambda e: self.move_player('up'))
        self.root.bind('<a>', lambda e: self.move_player('left'))
        self.root.bind('<s>', lambda e: self.move_player('down'))
        self.root.bind('<d>', lambda e: self.move_player('right'))
        self.root.bind('<space>', lambda e: self.switch_controlled_spirit())
        self.root.bind('<Control-z>', lambda e: self.undo_move())
        self.root.bind('<Control-y>', lambda e: self.redo_move())

    def show_game_mode_selection(self):
        """Let the player choose single-player or two-player mode."""
        mode_window = tk.Toplevel(self.root)
        mode_window.title("Choose Game Mode")
        # (Mode selection window - tips are shown in the main UI.)
        mode_window.geometry("350x300")
        mode_window.resizable(False, False)
        mode_window.transient(self.root)
        mode_window.grab_set()

        # Title
        ttk.Label(mode_window, text="Select Game Mode", 
                 font=("Arial", 14, "bold")).pack(pady=20)

        # Two-player mode button
        def start_two_player():
            self.mode = 'two'
            self.controlled_spirit = 'fire'
            self.current_player_controlling = 'fire'
            mode_window.destroy()
            self.show_level_selection()

        ttk.Button(mode_window, text="Two-Player Mode\n(Control both spirits)", 
                  command=start_two_player, width=30).pack(pady=10)

        # Single-player mode frame
        single_frame = ttk.LabelFrame(mode_window, text="Single-Player Mode", padding=10)
        single_frame.pack(padx=20, pady=10, fill=tk.X)

        # Choose which spirit in single-player
        spirit_var = tk.StringVar(value='fire')
        ttk.Radiobutton(single_frame, text="Control Fire Spirit", 
                       variable=spirit_var, value='fire').pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(single_frame, text="Control Water Spirit", 
                       variable=spirit_var, value='water').pack(anchor=tk.W, pady=5)

        # Start single-player button
        def start_single_player():
            self.mode = 'single'
            self.controlled_spirit = spirit_var.get()
            self.current_player_controlling = spirit_var.get()
            mode_window.destroy()
            self.show_level_selection()

        ttk.Button(single_frame, text="Start Single-Player", 
                  command=start_single_player, width=25).pack(pady=10)

    def toggle_tips(self):
        """Toggle the small tips panel on/off — written in a simple, student tone."""
        # Be defensive: the UI widgets may not exist yet during startup.
        if self.tips_label is None or self.show_tips_btn is None:
            return

        # Use the widget methods only when they are present.
        if self.tips_label.winfo_ismapped():
            self.tips_label.pack_forget()
            self.show_tips_btn.config(text="Show Tips")
        else:
            self.tips_label.pack(padx=6, pady=6)
            self.show_tips_btn.config(text="Hide Tips")

        # (Hint text moved to main UI; no extra widgets needed here.)

    def load_level(self):
        """Load the current level, either built-in or custom file."""
        try:
            self.moves = 0
            self.start_time = time.perf_counter()
            self.stop_timer()
            self.start_timer()

            if self.custom_level_path:
                self.level = Level()
                self.level.load_file(self.custom_level_path)
                self.level._setup_puzzle_mechanics()
                self.level.find_players(mode=self.mode, controlled_spirit=self.controlled_spirit)
            elif self.level_name:
                self.custom_level_path = None
                self.custom_description = ''
                self.level = Level()
                self.level.load_default_level(
                    difficulty=self.current_difficulty,
                    mode=self.mode,
                    controlled_spirit=self.controlled_spirit,
                    level_name=self.level_name
                )
            else:
                self.set_feedback_message("No level selected yet.")
                return

            self.refresh_display()
            self.set_feedback_message("Level loaded. Use arrow buttons or W/A/S/D to move.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load level: {str(e)}")

    def load_custom_level(self):
        """Load a custom level from a text file."""
        file_path = filedialog.askopenfilename(
            title="Open Custom Level",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            self.custom_level_path = file_path
            self.level_name = os.path.basename(file_path)
            self.current_difficulty = 'custom'
            self.custom_description = f"Custom level loaded from {self.level_name}."
            self.load_level()
            self.set_feedback_message("Custom level loaded. Use the arrows or W/A/S/D to move.")
        except Exception as e:
            self.custom_level_path = None
            messagebox.showerror("Error", f"Failed to load custom level: {str(e)}")

    def show_level_selection(self):
        """Display a window for the player to select difficulty and level."""
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Choose Level")
        selection_window.geometry("550x450")
        selection_window.resizable(False, False)
        selection_window.transient(self.root)
        selection_window.grab_set()

        # Title
        ttk.Label(selection_window, text="Select Your Difficulty and Level", 
                 font=("Arial", 12, "bold")).pack(pady=10)

        # Difficulty selection frame
        difficulty_frame = ttk.LabelFrame(selection_window, text="Difficulty", padding=10)
        difficulty_frame.pack(fill=tk.X, padx=10, pady=5)

        difficulty_var = tk.StringVar(value=self.current_difficulty)
        for diff in ['easy', 'medium', 'hard']:
            ttk.Radiobutton(difficulty_frame, text=diff.upper(), 
                           variable=difficulty_var, value=diff).pack(anchor=tk.W)

        # Level description label
        description_label = ttk.Label(selection_window, text="", font=("Arial", 9), 
                                     foreground="gray", wraplength=450, justify=tk.LEFT)
        description_label.pack(padx=10, pady=5)

        # Level selection frame
        level_frame = ttk.LabelFrame(selection_window, text="Levels", padding=10)
        level_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Listbox for level selection
        level_listbox = tk.Listbox(level_frame, height=8)
        level_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(level_frame, orient=tk.VERTICAL, command=level_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        level_listbox.config(yscrollcommand=scrollbar.set)

        # Hint for the player
        ttk.Label(selection_window, text="Double-click a level or press Start Game. ★ = Completed",
                 font=("Arial", 9), foreground="gray").pack(pady=5)

        # Populate listbox with levels for the selected difficulty
        def update_levels(*args):
            selected_difficulty = difficulty_var.get()
            level_listbox.delete(0, tk.END)
            levels = Level.DEFAULT_LEVELS.get(selected_difficulty, {})
            for level_name in levels.keys():
                # Show star if level is completed
                is_complete = self.progress.is_level_completed(selected_difficulty, level_name)
                display_text = f"★ {level_name}" if is_complete else f"  {level_name}"
                level_listbox.insert(tk.END, display_text)
            if level_listbox.size() > 0:
                level_listbox.selection_set(0)
                update_description()

        def update_description(*args):
            selected_difficulty = difficulty_var.get()
            if level_listbox.curselection():
                selected_item = level_listbox.get(level_listbox.curselection())
                # Remove the star symbol if present
                selected_level = selected_item.replace("★ ", "").replace("  ", "")
                desc = Level.get_default_description(selected_difficulty, selected_level)
                
                # Add best moves and time if available
                best_moves = self.progress.get_best_moves(selected_difficulty, selected_level)
                best_time = self.progress.get_best_time(selected_difficulty, selected_level)
                
                if best_moves is not None:
                    desc += f"\n\nBest: {best_moves} moves in {best_time}s"
                
                description_label.config(text=desc)

        # Bind events for dynamic updates
        if hasattr(difficulty_var, 'trace_add'):
            difficulty_var.trace_add('write', update_levels)
        else:
            difficulty_var.trace('w', update_levels)
        level_listbox.bind('<<ListboxSelect>>', update_description)

        # Start game button
        def start_game():
            if level_listbox.curselection():
                self.current_difficulty = difficulty_var.get()
                selected_item = level_listbox.get(level_listbox.curselection())
                self.level_name = selected_item.replace("★ ", "").replace("  ", "")
                self.custom_level_path = None
                self.custom_description = ''
                self.game_state.clear()
                self.load_level()
                self.set_feedback_message("Level ready. Move your spirit and solve the puzzle!")
                selection_window.destroy()

        ttk.Button(selection_window, text="Start Game", command=start_game).pack(pady=10)
        level_listbox.bind('<Double-Button-1>', lambda e: start_game())

        # Initialize level list
        update_levels()

    def switch_controlled_spirit(self):
        """Switch the controlled spirit in two-player mode."""
        if self.mode == 'two':
            if self.current_player_controlling == 'fire':
                self.current_player_controlling = 'water'
            else:
                self.current_player_controlling = 'fire'
            self.refresh_display()
            self.set_feedback_message(f"Now controlling {self.current_player_controlling.capitalize()} Spirit.")

    def move_player(self, direction):
        """Move the selected spirit on the map."""
        if not self.level.fire_player and not self.level.water_player:
            return

        # Choose the spirit we are moving right now
        if self.mode == 'two':
            player = self.level.fire_player if self.current_player_controlling == 'fire' else self.level.water_player
        else:
            player = self.level.fire_player if self.controlled_spirit == 'fire' else self.level.water_player

        if player is None:
            return

        # Calculate new position based on direction
        new_row, new_col = player.row, player.col
        if direction == 'up':
            new_row -= 1
        elif direction == 'down':
            new_row += 1
        elif direction == 'left':
            new_col -= 1
        elif direction == 'right':
            new_col += 1

        # Try the move. If the spot is okay, move the player.
        if self.level.is_valid_move(player, new_row, new_col):
            # Save game state before moving (for undo/redo)
            fire_pos = (self.level.fire_player.row, self.level.fire_player.col) if self.level.fire_player else None
            water_pos = (self.level.water_player.row, self.level.water_player.col) if self.level.water_player else None
            self.game_state.save_state(self.level, self.moves, fire_pos, water_pos, self.level.has_key)

            # Store old position for animation
            old_x = player.col * self.TILE_SIZE + self.TILE_SIZE / 2
            old_y = player.row * self.TILE_SIZE + self.TILE_SIZE / 2

            player.update_position(new_row, new_col)

            # Check if we landed on ice - if so, slide until we hit something
            if self.level.grid[new_row][new_col] == 'I':
                self.level.slide_on_ice(player, direction)
                # Track ice sliding achievement
                if not self.has_slid_on_ice:
                    self.has_slid_on_ice = True
                    self.check_and_unlock_achievements()

            # Apply tile effects and track achievements
            tile_before_effect = self.level.grid[player.row][player.col]
            self.level.apply_tile_effect(player)

            # Check what we collected/touched for achievements
            self._check_tile_achievements(tile_before_effect, player)

            self.moves += 1

            # Animate the sprite movement
            new_x = player.col * self.TILE_SIZE + self.TILE_SIZE / 2
            new_y = player.row * self.TILE_SIZE + self.TILE_SIZE / 2
            self._animate_sprite_move(player, old_x, old_y, new_x, new_y)

            # Check win condition
            if self.level.check_win(self.mode, self.controlled_spirit):
                elapsed = int(time.perf_counter() - self.start_time) if self.start_time else 0

                # Play celebration animation!
                grid_width = len(self.level.grid[0])
                grid_height = len(self.level.grid)
                self.animations.animate_level_complete(self.canvas, grid_width, grid_height, self.TILE_SIZE)

                messagebox.showinfo("Success!",
                                   f"You completed the level!\n\nMoves used: {self.moves}\nTime: {elapsed}s\n\nExcellent work!")

                # Record this achievement
                self.progress.mark_level_complete(self.current_difficulty, self.level_name, self.moves, elapsed)
                self.update_progress_display()

                # Check level completion achievements
                self.levels_completed_count += 1
                self.check_and_unlock_achievements()

                self.restart_level()
                self.set_feedback_message("Great job! The level was restarted. Try another one or choose Change Level.")
            else:
                self.refresh_display()
                self.set_feedback_message("Good move! Keep going.")
        else:
            self.set_feedback_message("That move is blocked. Try another direction.")

    def _check_tile_achievements(self, tile, player):
        """Check and unlock achievements based on the tile the player touched."""
        if tile == 'K' and not self.has_collected_key:
            self.has_collected_key = True
            self.achievements.unlock('key_collector')
            # Show collect animation
            x = player.col * self.TILE_SIZE + self.TILE_SIZE / 2
            y = player.row * self.TILE_SIZE + self.TILE_SIZE / 2
            self.animations.animate_collect_item(self.canvas, x, y, 'key')
            self._show_achievement_popup('key_collector')

        elif tile == 'S' and not self.has_activated_switch:
            self.has_activated_switch = True
            self.achievements.unlock('switch_master')
            x = player.col * self.TILE_SIZE + self.TILE_SIZE / 2
            y = player.row * self.TILE_SIZE + self.TILE_SIZE / 2
            self.animations.animate_collect_item(self.canvas, x, y, 'switch')
            self._show_achievement_popup('switch_master')

        elif tile == '1' and not self.has_activated_onetime:
            self.has_activated_onetime = True
            self.achievements.unlock('one_time_use')
            x = player.col * self.TILE_SIZE + self.TILE_SIZE / 2
            y = player.row * self.TILE_SIZE + self.TILE_SIZE / 2
            self.animations.animate_collect_item(self.canvas, x, y, 'onetime')
            self._show_achievement_popup('one_time_use')

        elif tile == 'T' and not self.has_used_teleporter:
            self.has_used_teleporter = True
            self.achievements.unlock('teleport_traveler')
            # Play teleporter animation
            x = player.col * self.TILE_SIZE + self.TILE_SIZE / 2
            y = player.row * self.TILE_SIZE + self.TILE_SIZE / 2
            self.animations.animate_teleporter_warp(self.canvas, x, y)
            self._show_achievement_popup('teleport_traveler')

    def _animate_sprite_move(self, player, old_x, old_y, new_x, new_y):
        """Animate a sprite moving from old position to new position."""
        # Find the sprite canvas ID for this player
        sprite_id = None
        if player == self.level.fire_player:
            sprite_id = getattr(self, 'fire_sprite_id', None)
        elif player == self.level.water_player:
            sprite_id = getattr(self, 'water_sprite_id', None)

        if sprite_id:
            self.animations.animate_sprite_movement(self.canvas, sprite_id, old_x, old_y, new_x, new_y)

    def check_and_unlock_achievements(self):
        """Check all achievement conditions and unlock any that are met."""
        # First level completed
        if self.levels_completed_count >= 1:
            self.achievements.unlock('first_step')

        # Speed runner - complete level under 60 seconds
        if self.start_time:
            elapsed = int(time.perf_counter() - self.start_time)
            if elapsed < 60 and self.levels_completed_count >= 1:
                self.achievements.unlock('speed_demon')

        # Ice breaker - slide on ice
        if self.has_slid_on_ice:
            self.achievements.unlock('ice_breaker')

        # Double trouble - activate two switches (check conditional door state)
        active_switches = sum(1 for pos in self.level.all_switches_pressed
                           if self.level.conditional_switches_active.get(pos, False))
        if active_switches >= 2:
            self.achievements.unlock('double_trouble')

        # Halfway hero - 50% completion
        completion = self.progress.get_completion_rate()
        if completion >= 50:
            self.achievements.unlock('halfway_there')

        # Completionist - 100% completion
        if completion >= 100:
            self.achievements.unlock('completionist')

        # Perfect moves - under 20 moves
        if self.moves > 0 and self.moves <= 20:
            self.achievements.unlock('perfect_moves')

        # Fire walker and water walker - in two player mode
        if self.mode == 'two':
            if self.level.fire_player and self.level.grid[self.level.fire_player.row][self.level.fire_player.col] == 'A':
                self.achievements.unlock('fire_walker')
            if self.level.water_player and self.level.grid[self.level.water_player.row][self.level.water_player.col] == 'B':
                self.achievements.unlock('water_walker')

    def _show_achievement_popup(self, achievement_id):
        """Show a popup notification for a newly unlocked achievement."""
        if achievement_id in self.achievements.achievements:
            achievement = self.achievements.achievements[achievement_id]
            self.set_feedback_message(f"Achievement Unlocked: {achievement.icon} {achievement.name}!")

    def show_achievements(self):
        """Display the achievements window."""
        ach_window = tk.Toplevel(self.root)
        ach_window.title("Achievements")
        ach_window.geometry("450x500")
        ach_window.resizable(False, False)
        ach_window.transient(self.root)
        ach_window.grab_set()

        # Title
        ttk.Label(ach_window, text="Your Achievements",
                 font=("Arial", 16, "bold")).pack(pady=15)

        # Show progress
        unlocked = self.achievements.get_unlocked_count()
        total = self.achievements.get_total_count()
        ttk.Label(ach_window, text=f"Progress: {unlocked}/{total} achievements unlocked",
                 font=("Arial", 11), foreground="blue").pack(pady=5)

        # Create a frame with scrollbar for achievements list
        list_frame = ttk.Frame(ach_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(list_frame, bg='#f5f5f5')
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        achievements_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.create_window((0, 0), window=achievements_frame, anchor=tk.NW)

        # Add each achievement to the list
        for achievement_id, achievement in self.achievements.achievements.items():
            ach_frame = ttk.Frame(achievements_frame)
            ach_frame.pack(fill=tk.X, pady=5, padx=5)

            # Icon and name
            if achievement.unlocked:
                icon_text = achievement.icon
                status_color = "green"
            else:
                icon_text = "?"
                status_color = "gray"

            ttk.Label(ach_frame, text=icon_text, font=("Arial", 20)).pack(side=tk.LEFT, padx=10)
            name_label = ttk.Label(ach_frame, text=achievement.name,
                                   font=("Arial", 10, "bold"),
                                   foreground=status_color if not achievement.unlocked else "black")
            name_label.pack(side=tk.LEFT, padx=5)

            # Description
            desc_text = achievement.description
            if not achievement.unlocked:
                desc_text = "???"
            desc_label = ttk.Label(ach_frame, text=desc_text,
                                   font=("Arial", 9),
                                   foreground="gray")
            desc_label.pack(side=tk.LEFT, padx=5)

            # Update window size
            ach_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox(tk.ALL))

        # Close button
        ttk.Button(ach_window, text="Close", command=ach_window.destroy).pack(pady=15)

    def set_feedback_message(self, message):
        """Update the text line that gives the player helpful feedback."""
        # Safely update the message label if it exists. Keep wording simple for students.
        if self.message_label is not None:
            self.message_label.config(text=message)
        else:
            # If UI not ready, print to console so feedback is still visible.
            print("Feedback:", message)

    def update_progress_display(self):
        """Update the progress bar showing completion percentage."""
        completion = self.progress.get_completion_rate()
        total_levels = 6
        completed = len(self.progress.progress_data['completed_levels'])
        # Only update the UI when the progress label exists (helpful during startup).
        if self.progress_label is not None:
            self.progress_label.config(text=f"Progress: {completion}% | Levels Completed: {completed}/{total_levels}")

    def undo_move(self):
        """Go back to the previous game state."""
        if not self.game_state.can_undo():
            self.set_feedback_message("Nothing to undo!")
            return
        
        state = self.game_state.undo()
        if state:
            self.level.grid = state['grid']
            self.moves = state['moves']
            self.level.has_key = state['has_key']
            self.level.switch_activated = state['switch_activated']
            self.level.one_time_switches = copy.deepcopy(state['one_time_switches'])
            self.level.activated_one_time_switches = copy.deepcopy(state['activated_one_time_switches'])
            self.level.conditional_switches_active = copy.deepcopy(state['conditional_switches_active'])
            self.level.consumed_keys = copy.deepcopy(state.get('consumed_keys', set()))
            self.level.consumed_switches = copy.deepcopy(state.get('consumed_switches', set()))

            # Restore player positions
            if state['fire_pos'] and self.level.fire_player:
                self.level.fire_player.row = state['fire_pos'][0]
                self.level.fire_player.col = state['fire_pos'][1]
            if state['water_pos'] and self.level.water_player:
                self.level.water_player.row = state['water_pos'][0]
                self.level.water_player.col = state['water_pos'][1]

            self.refresh_display()
            self.set_feedback_message("Undone! You can redo if needed.")

    def redo_move(self):
        """Go forward to the next game state."""
        if not self.game_state.can_redo():
            self.set_feedback_message("Nothing to redo!")
            return
        
        state = self.game_state.redo()
        if state:
            self.level.grid = state['grid']
            self.moves = state['moves']
            self.level.has_key = state['has_key']
            self.level.switch_activated = state['switch_activated']
            self.level.one_time_switches = copy.deepcopy(state['one_time_switches'])
            self.level.activated_one_time_switches = copy.deepcopy(state['activated_one_time_switches'])
            self.level.conditional_switches_active = copy.deepcopy(state['conditional_switches_active'])
            self.level.consumed_keys = copy.deepcopy(state.get('consumed_keys', set()))
            self.level.consumed_switches = copy.deepcopy(state.get('consumed_switches', set()))
            
            # Restore player positions
            if state['fire_pos'] and self.level.fire_player:
                self.level.fire_player.row = state['fire_pos'][0]
                self.level.fire_player.col = state['fire_pos'][1]
            if state['water_pos'] and self.level.water_player:
                self.level.water_player.row = state['water_pos'][0]
                self.level.water_player.col = state['water_pos'][1]
            
            self.refresh_display()
            self.set_feedback_message("Redone!")

    def show_level_editor(self):
        """Open the level editor window to create custom levels."""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Level Editor")
        editor_window.geometry("700x700")
        editor_window.resizable(False, False)
        editor_window.transient(self.root)
        editor_window.grab_set()

        # Title
        ttk.Label(editor_window, text="Create a Custom Level", 
                 font=("Arial", 14, "bold")).pack(pady=10)

        # Instructions
        instructions = ttk.Label(editor_window, 
            text="Enter your level map below. Use: F=Fire Start, W=Water Start, A=Fire Exit, B=Water Exit\n"
                 "K=Key, D=Door, S=Switch, X=Fire Hazard, O=Water Hazard, #=Wall, .=Empty\n"
                 "Advanced: T=Teleporter In, E=Teleporter Out, I=Ice Tile, 1=One-Time Switch, C=Conditional Door",
            font=("Arial", 9), foreground="blue", justify=tk.LEFT)
        instructions.pack(padx=10, pady=5)

        # Level name
        name_frame = ttk.Frame(editor_window)
        name_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(name_frame, text="Level Name:").pack(side=tk.LEFT, padx=5)
        level_name_entry = ttk.Entry(name_frame, width=40)
        level_name_entry.pack(side=tk.LEFT, padx=5)

        # Level description
        desc_frame = ttk.Frame(editor_window)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(desc_frame, text="Description:").pack(side=tk.LEFT, padx=5)
        level_desc_entry = ttk.Entry(desc_frame, width=40)
        level_desc_entry.pack(side=tk.LEFT, padx=5)

        # Map text area
        map_frame = ttk.LabelFrame(editor_window, text="Level Map", padding=10)
        map_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        map_text = tk.Text(map_frame, height=15, width=60, font=("Courier", 10))
        map_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(map_frame, orient=tk.VERTICAL, command=map_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        map_text.config(yscrollcommand=scrollbar.set)

        # Example level template
        example_map = "###########\n#F.....A..#\n#.......#.#\n#.#####.#.#\n#.......#.#\n#W.....B..#\n###########"
        map_text.insert("1.0", example_map)

        # Save button
        def save_level():
            name = level_name_entry.get()
            description = level_desc_entry.get()
            map_content = map_text.get("1.0", tk.END).rstrip('\n')

            if not name:
                messagebox.showwarning("Error", "Please enter a level name.")
                return

            if not description:
                description = "A custom level."

            try:
                level = Level()
                level._parse_grid_from_lines(map_content.split('\n'))
                level.validate_grid_shape()
                level.find_players(mode='two')

                filename = f"{name.replace(' ', '_')}.txt"
                filepath = os.path.join(os.getcwd(), filename)

                with open(filepath, 'w') as f:
                    f.write(map_content)

                messagebox.showinfo("Success", 
                    f"Level saved as '{filename}'!\n\n"
                    f"You can load it using 'Load Custom Level'.")
                editor_window.destroy()
            except ValueError as e:
                messagebox.showerror("Invalid Level", f"Error: {str(e)}")

        ttk.Button(editor_window, text="Save Level", command=save_level).pack(pady=10)

        # Close button
        ttk.Button(editor_window, text="Close", command=editor_window.destroy).pack(pady=5)

    def start_timer(self):
        """Start or resume the level timer."""
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
        self.timer_id = self.root.after(1000, self.update_timer)

    def stop_timer(self):
        """Stop the timer update loop."""
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def update_timer(self):
        """Update the timer display every second."""
        self.refresh_display()
        self.timer_id = self.root.after(1000, self.update_timer)

    def format_elapsed_time(self):
        """Format elapsed seconds in MM:SS style."""
        if self.start_time is None:
            return "00:00"
        elapsed = int(time.perf_counter() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02}:{seconds:02}"

    def refresh_display(self):
        """Redraw the game canvas and update all status information."""
        # Use a local reference and guard against missing canvas to satisfy static analysis.
        canvas = self.canvas
        if canvas is None:
            return

        canvas.delete("all")

        if not self.level.grid:
            return

        # Draw each tile on the canvas
        for row_idx, row in enumerate(self.level.grid):
            for col_idx, tile in enumerate(row):
                x1 = col_idx * self.TILE_SIZE
                y1 = row_idx * self.TILE_SIZE
                x2 = x1 + self.TILE_SIZE
                y2 = y1 + self.TILE_SIZE

                color = self.COLORS.get(tile, '#ffffff')
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='#000000')

                # Add text label for special tiles
                if tile not in ['.', '#']:
                    canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                       text=tile, font=("Arial", 12, "bold"),
                                       fill='white')

        # Draw Fire Spirit with circle and remember its ID for animation
        if self.level.fire_player:
            fp = self.level.fire_player
            x = fp.col * self.TILE_SIZE + self.TILE_SIZE / 2
            y = fp.row * self.TILE_SIZE + self.TILE_SIZE / 2
            outline_color = 'gold' if self.current_player_controlling == 'fire' else 'black'
            self.fire_sprite_id = canvas.create_oval(x - 10, y - 10, x + 10, y + 10,
                                   fill='#e74c3c', outline=outline_color, width=2)
            canvas.create_text(x, y, text='F', font=("Arial", 11, "bold"),
                               fill='white')

        # Draw Water Spirit with circle and remember its ID for animation
        if self.level.water_player:
            wp = self.level.water_player
            x = wp.col * self.TILE_SIZE + self.TILE_SIZE / 2
            y = wp.row * self.TILE_SIZE + self.TILE_SIZE / 2
            outline_color = 'gold' if self.current_player_controlling == 'water' else 'black'
            self.water_sprite_id = canvas.create_oval(x - 10, y - 10, x + 10, y + 10,
                                   fill='#3498db', outline=outline_color, width=2)
            canvas.create_text(x, y, text='W', font=("Arial", 11, "bold"),
                               fill='white')

        # Resize canvas to fit the grid
        width = len(self.level.grid[0]) * self.TILE_SIZE
        height = len(self.level.grid) * self.TILE_SIZE
        canvas.config(width=width, height=height)

        # Update status information
        current_control = self.current_player_controlling.capitalize() if self.mode == 'two' else self.controlled_spirit.capitalize()
        level_display = self.level_name or "No Level"
        diff_display = self.current_difficulty.upper() if self.current_difficulty != 'custom' else 'CUSTOM'
        time_display = self.format_elapsed_time()
        status_text = f"Level: {level_display} | Difficulty: {diff_display} | Moves: {self.moves} | Time: {time_display}"
        if self.mode == 'two':
            status_text += f" | Controlling: {current_control} Spirit"
        if self.level.has_key:
            status_text += " | Key: ✓"
        if self.status_label is not None:
            self.status_label.config(text=status_text)

        # Update level description
        if self.custom_level_path:
            if self.description_label is not None:
                self.description_label.config(text=self.custom_description)
        else:
            desc = Level.get_default_description(self.current_difficulty, self.level_name)
            if self.description_label is not None:
                self.description_label.config(text=desc)
        
        # Update progress display
        self.update_progress_display()

    def restart_level(self):
        """Restart the current level by resetting the map and moves."""
        self.current_player_controlling = self.controlled_spirit
        self.load_level()
        self.set_feedback_message("Level restarted. Use the arrows or W/A/S/D to try again.")

    def show_help(self):
        """Display help information about the game."""
        help_text = """
ELEMENT ESCAPE: TWIN SPIRITS

OBJECTIVE:
Guide the Fire Spirit to the orange exit (A) and the Water Spirit to the purple exit (B).

GAME MECHANICS - BASIC:
- Each spirit must reach its designated exit to complete the level.
- Collect keys (yellow) to open doors (gray).
- Press switches (green) to activate puzzle elements.
- Avoid hazards: Fire Spirit avoids water (cyan), Water Spirit avoids fire (orange).

ADVANCED MECHANICS:
- Teleporters (purple T = entrance, orange E = exit): Step on entrance to instantly move to exit
- Ice Tiles (light blue I): Slide automatically until hitting a wall or other obstacle
- One-Time Switches (green 1): Can only be pressed once - use strategically!
- Conditional Doors (dark red C): Need two different switches pressed to open

CONTROLS:
- Click arrow buttons or use W/A/S/D keys to move.
- Press SPACE or click "Switch Spirit" to switch control between spirits.
- Click "Restart Level" to reset the current level.
- Click "Change Level" to select a built-in level.
- Undo (Ctrl+Z) and Redo (Ctrl+Y) to explore different strategies.
- Click "Load Custom Level" to open your own level file.
- Click "Level Editor" to create custom levels.

DIFFICULTY LEVELS:
- Easy: Perfect for learning the game and basic mechanics.
- Medium: Standard puzzles with advanced mechanics like ice and teleporters.
- Hard: Expert challenges with complex mazes, hazards, and conditional doors!

TIPS:
- Plan your moves carefully before moving, especially on ice tiles!
- Sometimes you need to move one spirit to clear a path for the other.
- Use switches and keys strategically to solve puzzles.
- Watch out for hazards specific to each spirit.
- On ice tiles, you will slide in the same direction until you hit something.
- Teleporters can help you bypass large areas quickly.

Good luck, and have fun exploring these challenging puzzles!
        """
        messagebox.showinfo("Help", help_text)


# Main function to run the game
def main():
    """Launch the game application."""
    root = tk.Tk()
    GUIGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
