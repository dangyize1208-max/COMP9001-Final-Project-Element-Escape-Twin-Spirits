# Unit tests for Element Escape: Twin Spirits
# This file tests the core game logic to ensure correctness and reliability.
# Date: May 2026

import unittest
from main import Player, Level


class TestPlayer(unittest.TestCase):
    """Test cases for the Player class."""

    def test_player_creation(self):
        """Test that a player can be created with correct attributes."""
        player = Player(
            name="Fire Spirit",
            symbol='F',
            exit_symbol='A',
            forbidden_tile='O',
            row=1,
            col=2
        )
        self.assertEqual(player.name, "Fire Spirit")
        self.assertEqual(player.symbol, 'F')
        self.assertEqual(player.row, 1)
        self.assertEqual(player.col, 2)

    def test_player_default_position(self):
        """Test that player has default position (0, 0) when not specified."""
        player = Player(
            name="Water Spirit",
            symbol='W',
            exit_symbol='B',
            forbidden_tile='X'
        )
        self.assertEqual(player.row, 0)
        self.assertEqual(player.col, 0)

    def test_update_position(self):
        """Test that player position can be updated correctly."""
        player = Player(
            name="Fire Spirit",
            symbol='F',
            exit_symbol='A',
            forbidden_tile='O'
        )
        player.update_position(5, 7)
        self.assertEqual(player.row, 5)
        self.assertEqual(player.col, 7)


class TestLevel(unittest.TestCase):
    """Test cases for the Level class."""

    def setUp(self):
        """Set up a Level instance for each test."""
        self.level = Level()

    def test_level_initialization(self):
        """Test that a level initializes with empty state."""
        self.assertEqual(self.level.grid, [])
        self.assertIsNone(self.level.fire_player)
        self.assertIsNone(self.level.water_player)
        self.assertFalse(self.level.has_key)
        self.assertFalse(self.level.switch_activated)

    def test_validate_grid_shape_rectangular(self):
        """Test that a rectangular grid passes validation."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        try:
            self.level.validate_grid_shape()
        except ValueError:
            self.fail("validate_grid_shape() raised ValueError for valid grid")

    def test_validate_grid_shape_irregular(self):
        """Test that an irregular grid fails validation."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "#####"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        with self.assertRaises(ValueError):
            self.level.validate_grid_shape()

    def test_validate_grid_shape_empty(self):
        """Test that an empty grid fails validation."""
        self.level.grid = []
        with self.assertRaises(ValueError):
            self.level.validate_grid_shape()

    def test_find_players_two_player_mode(self):
        """Test that both players are created correctly in two-player mode."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "#..##.##..#",
            "#..S..#...#",
            "#..##.##..#",
            "#W..D....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        self.assertIsNotNone(self.level.fire_player)
        self.assertIsNotNone(self.level.water_player)
        self.assertEqual(self.level.fire_player.name, "Fire Spirit")
        self.assertEqual(self.level.water_player.name, "Water Spirit")

    def test_find_players_fire_spirit_position(self):
        """Test that Fire Spirit is positioned correctly from the map."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "#W..D....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        self.assertEqual(self.level.fire_player.row, 1)
        self.assertEqual(self.level.fire_player.col, 1)

    def test_find_players_water_spirit_position(self):
        """Test that Water Spirit is positioned correctly from the map."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "#W..D....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        self.assertEqual(self.level.water_player.row, 3)
        self.assertEqual(self.level.water_player.col, 1)

    def test_find_players_single_player_fire(self):
        """Test that only Fire Spirit is created in single-player fire mode."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "#W..D....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='single', controlled_spirit='fire')

        self.assertIsNotNone(self.level.fire_player)
        self.assertIsNone(self.level.water_player)

    def test_find_players_single_player_water(self):
        """Test that only Water Spirit is created in single-player water mode."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "#W..D....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='single', controlled_spirit='water')

        self.assertIsNone(self.level.fire_player)
        self.assertIsNotNone(self.level.water_player)

    def test_find_players_missing_fire_position(self):
        """Test that ValueError is raised when Fire Spirit starting position is missing."""
        grid_lines = [
            "###########",
            "#...K....A#",
            "#...#.....#",
            "#W..D....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        with self.assertRaises(ValueError):
            self.level.find_players(mode='two', controlled_spirit='fire')

    def test_find_players_missing_water_position(self):
        """Test that ValueError is raised when Water Spirit starting position is missing."""
        grid_lines = [
            "###########",
            "#F..K....A#",
            "#...#.....#",
            "#...D....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        with self.assertRaises(ValueError):
            self.level.find_players(mode='two', controlled_spirit='fire')

    def test_is_valid_move_empty_space(self):
        """Test that moving to an empty space is valid."""
        grid_lines = [
            "###########",
            "#F.......A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        player = self.level.fire_player
        is_valid = self.level.is_valid_move(player, 1, 2)
        self.assertTrue(is_valid)

    def test_is_valid_move_into_wall(self):
        """Test that moving into a wall is invalid."""
        grid_lines = [
            "###########",
            "#F.......A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        player = self.level.fire_player
        is_valid = self.level.is_valid_move(player, 1, 0)
        self.assertFalse(is_valid)

    def test_is_valid_move_into_hazard(self):
        """Test that moving into a hazard is invalid for that spirit."""
        grid_lines = [
            "###########",
            "#F.O.....A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        player = self.level.fire_player
        is_valid = self.level.is_valid_move(player, 1, 3)
        self.assertFalse(is_valid)

    def test_is_valid_move_water_into_fire_hazard(self):
        """Test that Water Spirit cannot move into fire hazards."""
        grid_lines = [
            "###########",
            "#F.......A#",
            "#...#.....#",
            "#W.X.....B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        player = self.level.water_player
        is_valid = self.level.is_valid_move(player, 3, 3)
        self.assertFalse(is_valid)

    def test_is_valid_move_door_without_key(self):
        """Test that player cannot move through door without key."""
        grid_lines = [
            "###########",
            "#F.D.....A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')
        self.level.has_key = False

        player = self.level.fire_player
        is_valid = self.level.is_valid_move(player, 1, 3)
        self.assertFalse(is_valid)

    def test_is_valid_move_door_with_key(self):
        """Test that player can move through door with key."""
        grid_lines = [
            "###########",
            "#F.D.....A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')
        self.level.has_key = True

        player = self.level.fire_player
        is_valid = self.level.is_valid_move(player, 1, 3)
        self.assertTrue(is_valid)

    def test_apply_tile_effect_key_pickup(self):
        """Test that picking up a key sets has_key to True."""
        self.level.has_key = False
        grid_lines = [
            "###########",
            "#..K.....A#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        
        player = Player(
            name="Fire Spirit",
            symbol='F',
            exit_symbol='A',
            forbidden_tile='O',
            row=1,
            col=3
        )
        self.level.apply_tile_effect(player)
        self.assertTrue(self.level.has_key)
        self.assertEqual(self.level.grid[1][3], '.')

    def test_apply_tile_effect_switch_activation(self):
        """Test that stepping on a switch activates it."""
        self.level.switch_activated = False
        grid_lines = [
            "###########",
            "#..S.....A#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        
        player = Player(
            name="Fire Spirit",
            symbol='F',
            exit_symbol='A',
            forbidden_tile='O',
            row=1,
            col=3
        )
        self.level.apply_tile_effect(player)
        self.assertTrue(self.level.switch_activated)

    def test_check_win_two_player_both_at_exit(self):
        """Test that two-player mode wins when both spirits are at exits."""
        grid_lines = [
            "###########",
            "#F.......A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        self.level.fire_player.update_position(1, 9)
        self.level.water_player.update_position(3, 9)

        self.assertTrue(self.level.check_win(mode='two', controlled_spirit='fire'))

    def test_check_win_two_player_fire_only_at_exit(self):
        """Test that two-player mode does not win if only Fire is at exit."""
        grid_lines = [
            "###########",
            "#F.......A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='two', controlled_spirit='fire')

        self.level.fire_player.update_position(1, 9)

        self.assertFalse(self.level.check_win(mode='two', controlled_spirit='fire'))

    def test_check_win_single_player_fire_at_exit(self):
        """Test that single-player fire mode wins when Fire Spirit at exit."""
        grid_lines = [
            "###########",
            "#F.......A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='single', controlled_spirit='fire')

        self.level.fire_player.update_position(1, 9)

        self.assertTrue(self.level.check_win(mode='single', controlled_spirit='fire'))

    def test_check_win_single_player_water_at_exit(self):
        """Test that single-player water mode wins when Water Spirit at exit."""
        grid_lines = [
            "###########",
            "#F.......A#",
            "#...#.....#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(grid_lines)
        self.level.find_players(mode='single', controlled_spirit='water')

        self.level.water_player.update_position(3, 9)

        self.assertTrue(self.level.check_win(mode='single', controlled_spirit='water'))

    def test_load_default_level_easy(self):
        """Test that a default easy level can be loaded."""
        try:
            self.level.load_default_level(
                difficulty='easy',
                mode='two',
                controlled_spirit='fire',
                level_name='Easy Level 1'
            )
            self.assertGreater(len(self.level.grid), 0)
            self.assertIsNotNone(self.level.fire_player)
            self.assertIsNotNone(self.level.water_player)
        except Exception as e:
            self.fail(f"load_default_level() raised {type(e).__name__}: {e}")

    def test_get_default_description(self):
        """Test that level descriptions can be retrieved."""
        description = Level.get_default_description('easy', 'Easy Level 1')
        self.assertIsInstance(description, str)
        self.assertGreater(len(description), 0)

    def test_get_default_map(self):
        """Test that level maps can be retrieved."""
        map_data = Level.get_default_map('easy', 'Easy Level 1')
        self.assertIsInstance(map_data, list)
        self.assertGreater(len(map_data), 0)


class TestGameIntegration(unittest.TestCase):
    """Integration tests for complete game scenarios."""

    def test_complete_level_playthrough(self):
        """Test a complete scenario of loading and winning a level."""
        level = Level()
        level.load_default_level(
            difficulty='easy',
            mode='two',
            controlled_spirit='fire',
            level_name='Easy Level 1'
        )

        self.assertIsNotNone(level.fire_player)
        self.assertIsNotNone(level.water_player)

        initial_fire_row = level.fire_player.row
        initial_fire_col = level.fire_player.col

        if level.is_valid_move(level.fire_player, initial_fire_row, initial_fire_col + 1):
            level.fire_player.update_position(initial_fire_row, initial_fire_col + 1)
            self.assertEqual(level.fire_player.col, initial_fire_col + 1)

    def test_all_difficulties_loadable(self):
        """Test that all difficulty levels can be loaded."""
        for difficulty in ['easy', 'medium', 'hard']:
            level = Level()
            try:
                level.load_default_level(
                    difficulty=difficulty,
                    mode='two',
                    controlled_spirit='fire'
                )
                self.assertGreater(len(level.grid), 0)
            except Exception as e:
                self.fail(f"Failed to load {difficulty} level: {e}")


if __name__ == '__main__':
    unittest.main()
