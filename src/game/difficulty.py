"""
難度管理系統
處理遊戲難度設定和參數調整
"""

from typing import Dict, Tuple, Optional
from .constants import ARROW_SPEED_EASY, ARROW_SPEED_NORMAL, GAME_AREA_X


class Difficulty:
    """難度管理系統類別"""

    DEFAULT_DIFFICULTY = "EASY"
    LANE_OFFSETS = {
        "LEFT": 30,
        "DOWN": 80,
        "UP": 130,
        "RIGHT": 180,
    }

    def __init__(self):
        self.current_difficulty = self.DEFAULT_DIFFICULTY

        # 難度設定
        self.difficulties = {
            "EASY": {
                "name": "Easy",
                "arrow_speed": ARROW_SPEED_EASY,
                "spawn_interval": 1.5,  # 箭頭生成間隔（秒）
                "judgment_window": 1.2,  # 判定窗口倍率
                "arrow_density": 0.7,  # 箭頭密度
                "score_multiplier": 1.0,  # 分數倍率
            },
            "NORMAL": {
                "name": "Normal",
                "arrow_speed": ARROW_SPEED_NORMAL,
                "spawn_interval": 1.0,  # 箭頭生成間隔（秒）
                "judgment_window": 1.0,  # 判定窗口倍率
                "arrow_density": 1.0,  # 箭頭密度
                "score_multiplier": 1.2,  # 分數倍率
            },
        }

        # 箭頭生成位置設定
        self.arrow_positions = {
            direction: (GAME_AREA_X + offset, 0)
            for direction, offset in self.LANE_OFFSETS.items()
        }

    def get_current_settings(self) -> Dict:
        """取得當前難度設定"""
        return self.difficulties[self.current_difficulty]

    def set_difficulty(self, difficulty: str) -> bool:
        """
        設定難度

        Args:
            difficulty: 難度名稱 ("EASY" 或 "NORMAL")

        Returns:
            bool: 設定是否成功
        """
        if difficulty in self.difficulties:
            self.current_difficulty = difficulty
            return True
        return False

    def get_arrow_speed(self) -> float:
        """取得當前難度的箭頭速度"""
        return self.difficulties[self.current_difficulty]["arrow_speed"]

    def get_spawn_interval(self) -> float:
        """取得當前難度的箭頭生成間隔"""
        return self.difficulties[self.current_difficulty]["spawn_interval"]

    def get_judgment_window_multiplier(self) -> float:
        """取得當前難度的判定窗口倍率"""
        return self.difficulties[self.current_difficulty]["judgment_window"]

    def get_score_multiplier(self) -> float:
        """取得當前難度的分數倍率"""
        return self.difficulties[self.current_difficulty]["score_multiplier"]

    def get_arrow_position(self, direction: str) -> Tuple[int, int]:
        """
        取得指定方向的箭頭位置

        Args:
            direction: 箭頭方向

        Returns:
            Tuple[int, int]: (x, y) 座標
        """
        return self.arrow_positions[direction]

    def calculate_adjusted_score(self, base_score: int) -> int:
        """
        根據難度計算調整後的分數

        Args:
            base_score: 基礎分數

        Returns:
            int: 調整後的分數
        """
        multiplier = self.get_score_multiplier()
        return int(base_score * multiplier)

    def get_difficulty_name(self) -> str:
        """取得當前難度的顯示名稱"""
        return self.difficulties[self.current_difficulty]["name"]

    def is_difficulty_available(self, difficulty: str) -> bool:
        """檢查難度是否可用"""
        return difficulty in self.difficulties

    def get_all_difficulties(self) -> Dict:
        """取得所有可用難度"""
        return self.difficulties.copy()

    def get_difficulty_description(self, difficulty: Optional[str] = None) -> str:
        """
        取得難度描述

        Args:
            difficulty: 難度名稱，若為None則使用當前難度

        Returns:
            str: 難度描述
        """
        if difficulty is None:
            difficulty = self.current_difficulty

        if difficulty not in self.difficulties:
            return "Unknown Difficulty"

        settings = self.difficulties[difficulty]
        return (
            f"Difficulty: {settings['name']}\n"
            f"Speed: {settings['arrow_speed']}\n"
            f"Interval: {settings['spawn_interval']}s\n"
            f"Multiplier: {settings['score_multiplier']}x"
        )
