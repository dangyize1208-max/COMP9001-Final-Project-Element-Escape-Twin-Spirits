# Test script for achievement system and animations
# This file tests the new achievements and animation functionality

import unittest
import os
import json
from main import Achievement, AchievementSystem, AnimationController, Level


class TestAchievementSystem(unittest.TestCase):
    """Test cases for the achievement system."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_file = 'test_achievements.json'
        # Clean up any existing test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.achievements = AchievementSystem(save_file=self.test_file)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_achievement_initialization(self):
        """Test that achievements are properly initialized."""
        self.assertEqual(len(self.achievements.achievements), 14)
        self.assertEqual(self.achievements.get_total_count(), 14)
        self.assertEqual(self.achievements.get_unlocked_count(), 0)

    def test_unlock_achievement(self):
        """Test that achievements can be unlocked."""
        result = self.achievements.unlock('first_step')
        self.assertTrue(result)
        self.assertTrue(self.achievements.achievements['first_step'].unlocked)
        self.assertEqual(self.achievements.get_unlocked_count(), 1)

    def test_cannot_unlock_twice(self):
        """Test that the same achievement cannot be unlocked twice."""
        self.achievements.unlock('first_step')
        result = self.achievements.unlock('first_step')
        self.assertFalse(result)
        self.assertEqual(self.achievements.get_unlocked_count(), 1)

    def test_get_newly_unlocked(self):
        """Test that newly unlocked achievements are tracked."""
        self.achievements.unlock('ice_breaker')
        newly = self.achievements.get_newly_unlocked()
        self.assertEqual(len(newly), 1)
        self.assertEqual(newly[0].achievement_id, 'ice_breaker')

        # Should be empty after getting
        newly = self.achievements.get_newly_unlocked()
        self.assertEqual(len(newly), 0)

    def test_achievement_persistence(self):
        """Test that achievements are saved and loaded correctly."""
        self.achievements.unlock('first_step')
        self.achievements.unlock('key_collector')

        # Create a new achievement system to test loading
        new_achievements = AchievementSystem(save_file=self.test_file)
        self.assertEqual(new_achievements.get_unlocked_count(), 2)
        self.assertTrue(new_achievements.achievements['first_step'].unlocked)
        self.assertTrue(new_achievements.achievements['key_collector'].unlocked)

    def test_all_achievement_ids_exist(self):
        """Test that all defined achievement IDs exist."""
        expected_ids = [
            'first_step', 'speed_demon', 'ice_breaker', 'teleport_traveler',
            'key_collector', 'switch_master', 'double_trouble', 'halfway_there',
            'completionist', 'perfect_moves', 'fire_walker', 'water_walker',
            'one_time_use', 'perfect_balance'
        ]
        for ach_id in expected_ids:
            self.assertIn(ach_id, self.achievements.achievements)

    def test_achievement_details(self):
        """Test that achievement details are correct."""
        ach = self.achievements.achievements['first_step']
        self.assertEqual(ach.name, 'First Step')
        self.assertEqual(ach.description, 'Complete your first level!')
        self.assertEqual(ach.icon, '🎯')
        self.assertFalse(ach.unlocked)


class TestAnimationController(unittest.TestCase):
    """Test cases for the animation controller."""

    def setUp(self):
        """Set up test fixtures."""
        self.animator = AnimationController()

    def test_animations_enabled_by_default(self):
        """Test that animations are enabled by default."""
        self.assertTrue(self.animator.animations_enabled)

    def test_can_disable_animations(self):
        """Test that animations can be disabled."""
        self.animator.animations_enabled = False
        self.assertFalse(self.animator.animations_enabled)

    def test_animation_speed(self):
        """Test animation speed setting."""
        self.assertEqual(self.animator.animation_speed, 1.0)
        self.animator.animation_speed = 2.0
        self.assertEqual(self.animator.animation_speed, 2.0)


class TestAchievementIntegration(unittest.TestCase):
    """Test cases for achievement integration with the game."""

    def setUp(self):
        """Set up test fixtures."""
        self.level = Level()
        self.test_map = [
            "###########",
            "#F.K.....A#",
            "#.........#",
            "#W.......B#",
            "###########"
        ]
        self.level._parse_grid_from_lines(self.test_map)
        self.level._setup_puzzle_mechanics()
        self.level.find_players(mode='single', controlled_spirit='fire')

    def test_level_has_required_players(self):
        """Test that the level has the required players."""
        self.assertIsNotNone(self.level.fire_player)

    def test_teleporter_level(self):
        """Test a level with teleporters for achievement testing."""
        teleporter_map = [
            "###########",
            "#F.T.....A#",
            "#.E.......#",
            "#W.......B#",
            "###########"
        ]
        level = Level()
        level._parse_grid_from_lines(teleporter_map)
        level._setup_puzzle_mechanics()
        level.find_players(mode='single', controlled_spirit='fire')

        self.assertEqual(len(level.teleporters), 1)

    def test_ice_level(self):
        """Test a level with ice tiles for achievement testing."""
        ice_map = [
            "###########",
            "#F.I.....A#",
            "#.........#",
            "#W.......B#",
            "###########"
        ]
        level = Level()
        level._parse_grid_from_lines(ice_map)
        level._setup_puzzle_mechanics()
        level.find_players(mode='single', controlled_spirit='fire')

        self.assertGreater(len(level.ice_tiles), 0)


if __name__ == '__main__':
    unittest.main()