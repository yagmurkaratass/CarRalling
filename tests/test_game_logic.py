import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import car_ralling as game


class SilentSounds:
    def play(self, _name):
        pass


class GameLogicTests(unittest.TestCase):
    def setUp(self):
        self.profile = game.DEFAULT_SAVE.copy()
        self.state = game.reset_game(0, 0, 0, 0)
        self.sounds = SilentSounds()

    def test_career_contains_twenty_complete_stages(self):
        required = {
            "chapter", "name", "biome", "effect", "speaker", "dialogue",
            "description", "key", "target", "reward", "special",
        }
        self.assertEqual(len(game.MISSION_DEFS), 20)
        self.assertTrue(all(required <= mission.keys() for mission in game.MISSION_DEFS))

    def test_first_stage_is_beginner_friendly(self):
        mission = game.MISSION_DEFS[0]
        self.assertEqual(mission["key"], "distance")
        self.assertLessEqual(mission["target"], 0.5)
        self.assertEqual(self.state["fuel"], 100.0)

    @patch.object(game, "save_progress", return_value=True)
    def test_stage_completion_awards_gold_and_joker(self, _save):
        self.state["distance"] = 0.5
        self.assertTrue(game.check_missions(self.state, self.profile, self.sounds))
        self.assertEqual(self.profile["story_stage"], 1)
        self.assertEqual(self.profile["rewards"], 1)
        self.assertEqual(self.profile["jokers"], 2)
        self.assertTrue(self.state["chapter_complete"])

    @patch.object(game, "save_progress", return_value=True)
    def test_joker_is_persistent_and_cannot_go_negative(self, _save):
        self.profile["jokers"] = 1
        self.assertTrue(game.use_joker(self.profile, self.state, self.sounds))
        self.assertEqual(self.profile["jokers"], 0)
        self.assertFalse(game.use_joker(self.profile, self.state, self.sounds))

    def test_final_changes_biome_by_distance(self):
        self.profile["story_stage"] = len(game.MISSION_DEFS) - 1
        biomes = [game.active_biome(self.profile, distance) for distance in (0.1, 1.1, 2.1, 3.1)]
        self.assertEqual(biomes, ["İLKBAHAR", "YAZ", "SONBAHAR", "KIŞ"])


if __name__ == "__main__":
    unittest.main()

