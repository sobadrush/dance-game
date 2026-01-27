"""
計分系統測試
"""

import unittest
import sys
import time
from pathlib import Path

# 添加src目錄到Python路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.score import Score


class TestScore(unittest.TestCase):
    """計分系統測試"""

    def setUp(self):
        """測試設定"""
        self.score = Score()

    def test_perfect_score(self):
        """測試完美分數計算"""
        added_score, combo_milestone = self.score.add_score("PERFECT", 100)

        self.assertEqual(self.score.total_score, 100)
        self.assertEqual(self.score.perfect_count, 1)
        self.assertEqual(self.score.good_count, 0)
        self.assertEqual(self.score.miss_count, 0)
        self.assertEqual(self.score.combo, 1)
        self.assertEqual(added_score, 100)
        self.assertFalse(combo_milestone)

    def test_good_score(self):
        """測試良好分數計算"""
        added_score, combo_milestone = self.score.add_score("GOOD", 50)

        self.assertEqual(self.score.total_score, 50)
        self.assertEqual(self.score.perfect_count, 0)
        self.assertEqual(self.score.good_count, 1)
        self.assertEqual(self.score.miss_count, 0)
        self.assertEqual(self.score.combo, 1)
        self.assertEqual(added_score, 50)
        self.assertFalse(combo_milestone)

    def test_miss_reset_combo(self):
        """測試Miss重置連擊"""
        self.score.add_score("PERFECT", 100)
        self.assertEqual(self.score.combo, 1)

        added_score, combo_milestone = self.score.add_score("MISS", 0)

        self.assertEqual(self.score.combo, 0)
        self.assertEqual(self.score.miss_count, 1)
        self.assertEqual(added_score, 0)
        self.assertFalse(combo_milestone)

    def test_accuracy_calculation(self):
        """測試準確率計算"""
        # 添加一些測試資料
        self.score.add_score("PERFECT", 100)  # hit
        self.score.add_score("GOOD", 50)  # hit
        self.score.add_score("MISS", 0)  # miss

        # 準確率應該是 2/3 = 66.67%
        accuracy = self.score.get_accuracy()
        self.assertAlmostEqual(accuracy, 66.67, places=1)

    def test_combo_bonus(self):
        """測試連擊獎勵"""
        total_added = 0
        combo_milestone_triggered = False
        for i in range(10):
            added, milestone = self.score.add_score("PERFECT", 100)
            total_added += added
            if milestone:
                combo_milestone_triggered = True

        self.assertEqual(self.score.total_score, 1050)
        self.assertTrue(combo_milestone_triggered)

    def test_score_breakdown(self):
        """測試分數詳細資訊"""
        self.score.add_score("PERFECT", 100)
        self.score.add_score("GOOD", 50)
        self.score.add_score("MISS", 0)

        breakdown = self.score.get_score_breakdown()

        self.assertEqual(breakdown["total_score"], 150)
        self.assertEqual(breakdown["perfect_count"], 1)
        self.assertEqual(breakdown["good_count"], 1)
        self.assertEqual(breakdown["miss_count"], 1)
        self.assertEqual(breakdown["combo"], 0)

    def test_reset(self):
        """測試重置功能"""
        # 添加一些分數
        self.score.add_score("PERFECT", 100)
        self.score.add_score("MISS", 0)

        # 重置
        self.score.reset()

        self.assertEqual(self.score.total_score, 0)
        self.assertEqual(self.score.combo, 0)
        self.assertEqual(self.score.perfect_count, 0)
        self.assertEqual(self.score.good_count, 0)
        self.assertEqual(self.score.miss_count, 0)
        self.assertEqual(len(self.score.score_history), 0)


if __name__ == "__main__":
    unittest.main()
