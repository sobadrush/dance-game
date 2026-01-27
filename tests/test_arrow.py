"""
箭頭系統測試
"""

import unittest
import sys
from pathlib import Path

# 添加src目錄到Python路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from game.arrow import Arrow


class TestArrow(unittest.TestCase):
    """箭頭類別測試"""

    def setUp(self):
        """測試設定"""
        self.arrow = Arrow("LEFT", 400, 500, 100)

    def test_arrow_initialization(self):
        """測試箭頭初始化"""
        self.assertEqual(self.arrow.direction, "LEFT")
        self.assertEqual(self.arrow.x, 400)
        self.assertEqual(self.arrow.y, 500)
        self.assertEqual(self.arrow.speed, 100)
        self.assertFalse(self.arrow.hit)
        self.assertFalse(self.arrow.missed)

    def test_arrow_update(self):
        """測試箭頭更新"""
        initial_y = self.arrow.y
        dt = 0.016  # 約60FPS

        self.arrow.update(dt)

        expected_y = initial_y - (100 * dt)
        self.assertAlmostEqual(self.arrow.y, expected_y, places=5)

    def test_arrow_get_rect(self):
        """測試箭頭矩形碰撞區域"""
        rect = self.arrow.get_rect()

        self.assertEqual(rect.x, 400 - 30)  # x - width/2
        self.assertEqual(rect.y, 500 - 30)  # y - height/2
        self.assertEqual(rect.width, 60)
        self.assertEqual(rect.height, 60)

    def test_arrow_out_of_bounds(self):
        """測試箭頭超出邊界檢查"""
        # 箭頭在螢幕內
        self.assertFalse(self.arrow.is_out_of_bounds(600))

        # 箭頭超出螢幕上方
        self.arrow.y = -5
        self.assertTrue(self.arrow.is_out_of_bounds(600))

        # 箭頭超出螢幕下方
        self.arrow.y = 700
        self.assertTrue(self.arrow.is_out_of_bounds(600))

    def test_hit_and_missed_flags(self):
        """測試擊中和錯過標記"""
        # 初始狀態
        self.assertFalse(self.arrow.hit)
        self.assertFalse(self.arrow.missed)

        # 設定為擊中
        self.arrow.hit = True
        self.assertTrue(self.arrow.hit)
        self.assertFalse(self.arrow.missed)

        # 設定為錯過
        self.arrow.missed = True
        self.assertTrue(self.arrow.missed)


if __name__ == "__main__":
    unittest.main()
