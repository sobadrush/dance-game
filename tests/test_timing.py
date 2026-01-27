"""
時機判定系統測試
"""

import unittest
import sys
import time
from pathlib import Path

# 添加src目錄到Python路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.timing import Timing


class TestTiming(unittest.TestCase):
    """時機判定系統測試"""

    def setUp(self):
        """測試設定"""
        self.timing = Timing()

    def test_perfect_timing(self):
        """測試完美判定"""
        arrow_y = 150  # 剛好在判定線上
        current_time = time.time()

        judgment, score = self.timing.check_timing(arrow_y, current_time, "LEFT")

        self.assertEqual(judgment, "PERFECT")
        self.assertEqual(score, 100)

    def test_good_timing(self):
        """測試良好判定"""
        arrow_y = 180  # 在良好判定範圍內
        current_time = time.time()

        judgment, score = self.timing.check_timing(arrow_y, current_time, "LEFT")

        self.assertEqual(judgment, "GOOD")
        self.assertEqual(score, 50)

    def test_miss_timing(self):
        """測試失誤判定"""
        arrow_y = 200  # 超出良好判定範圍
        current_time = time.time()

        judgment, score = self.timing.check_timing(arrow_y, current_time, "LEFT")

        self.assertEqual(judgment, "MISS")
        self.assertEqual(score, 0)

    def test_cooldown_prevention(self):
        """測試冷卻時間防止重複判定"""
        current_time = time.time()
        arrow_y = 150

        # 第一次判定
        judgment1, score1 = self.timing.check_timing(arrow_y, current_time, "LEFT")

        # 立即第二次判定（應該被冷卻阻止）
        judgment2, score2 = self.timing.check_timing(arrow_y, current_time, "LEFT")

        self.assertEqual(judgment1, "PERFECT")
        self.assertEqual(judgment2, "COOLDOWN")

    def test_feedback_system(self):
        """測試回饋系統"""
        current_time = time.time()

        # 添加判定回饋
        self.timing.add_feedback("PERFECT", current_time)

        self.assertEqual(len(self.timing.feedback_messages), 1)
        self.assertEqual(self.timing.feedback_messages[0]["text"], "PERFECT")
        self.assertEqual(self.timing.feedback_messages[0]["color"], (255, 215, 0))

    def test_feedback_cleanup(self):
        """測試回饋清理"""
        current_time = time.time()

        # 添加回饋訊息
        self.timing.add_feedback("PERFECT", current_time - 1.0)  # 1秒前的訊息
        self.timing.add_feedback("GOOD", current_time)  # 現在的訊息

        # 更新回饋（應該移除舊訊息）
        self.timing.update_feedback(current_time)

        self.assertEqual(len(self.timing.feedback_messages), 1)
        self.assertEqual(self.timing.feedback_messages[0]["text"], "GOOD")

    def test_should_remove_arrow(self):
        """測試箭頭移除判定"""
        # 未擊中的箭頭超出範圍
        should_remove1 = self.timing.should_remove_arrow(50, False)
        self.assertTrue(should_remove1)

        # 已擊中的箭頭超出範圍
        should_remove2 = self.timing.should_remove_arrow(50, True)
        self.assertTrue(should_remove2)

        # 未擊中的箭頭在範圍內
        should_remove3 = self.timing.should_remove_arrow(150, False)
        self.assertFalse(should_remove3)

        # 已擊中的箭頭在範圍內
        should_remove4 = self.timing.should_remove_arrow(150, True)
        self.assertFalse(should_remove4)


if __name__ == "__main__":
    unittest.main()
