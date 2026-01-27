"""
時機判定系統
處理Perfect/Good/Miss判定的核心邏輯
"""

from typing import Tuple, Optional
from .constants import (
    PERFECT_RANGE,
    GOOD_RANGE,
    MISS_RANGE,
    PERFECT_SCORE,
    GOOD_SCORE,
    MISS_SCORE,
    JUDGMENT_LINE_Y,
)


class Timing:
    """時機判定系統類別"""

    def __init__(self):
        self.judgment_line_y = JUDGMENT_LINE_Y  # 判定線Y座標
        self.last_judgment_time = {}  # 記錄上次判定時間，防止重複判定
        self.cooldown_time = 0.1  # 判定冷卻時間（秒）

        # 判定回饋效果
        self.feedback_messages = []
        self.feedback_duration = 0.5  # 回饋顯示時間（秒）

    def check_timing(
        self, arrow_y: float, current_time: float, direction: str
    ) -> Tuple[str, int]:
        """
        檢查時機判定

        Args:
            arrow_y: 箭頭Y座標
            current_time: 當前時間
            direction: 箭頭方向

        Returns:
            Tuple[判定等級, 分數]
        """
        # 檢查冷卻時間
        if direction in self.last_judgment_time:
            if current_time - self.last_judgment_time[direction] < self.cooldown_time:
                return "COOLDOWN", 0

        # 計算距離判定線的距離
        distance = abs(arrow_y - self.judgment_line_y)

        # 判定邏輯
        if distance <= PERFECT_RANGE:
            judgment = "PERFECT"
            score = PERFECT_SCORE
        elif distance <= GOOD_RANGE:
            judgment = "GOOD"
            score = GOOD_SCORE
        elif distance <= MISS_RANGE:
            judgment = "MISS"
            score = MISS_SCORE
        else:
            judgment = "MISS"
            score = MISS_SCORE

        # 更新最後判定時間
        self.last_judgment_time[direction] = current_time

        # 添加回饋訊息
        self.add_feedback(judgment, current_time)

        return judgment, score

    def add_feedback(self, judgment: str, current_time: float) -> None:
        """添加判定回饋訊息"""
        self.feedback_messages.append(
            {
                "text": judgment,
                "time": current_time,
                "color": self._get_judgment_color(judgment),
            }
        )

    def _get_judgment_color(self, judgment: str) -> Tuple[int, int, int]:
        """取得判定等級對應的顏色"""
        colors = {
            "PERFECT": (255, 215, 0),  # 金色
            "GOOD": (0, 255, 0),  # 綠色
            "MISS": (255, 0, 0),  # 紅色
            "MISS_FAR": (128, 0, 0),  # 深紅色
        }
        return colors.get(judgment, (255, 255, 255))

    def update_feedback(self, current_time: float) -> None:
        """更新回饋訊息，移除過期的訊息"""
        self.feedback_messages = [
            msg
            for msg in self.feedback_messages
            if current_time - msg["time"] < self.feedback_duration
        ]

    def should_remove_arrow(self, arrow_y: float, arrow_hit: bool) -> bool:
        """
        判斷是否應該移除箭頭

        Args:
            arrow_y: 箭頭Y座標
            arrow_hit: 箭頭是否已被擊中

        Returns:
            bool: 是否應該移除
        """
        # 如果箭頭已被擊中，且超出判定範圍，則移除
        if arrow_hit:
            return arrow_y < self.judgment_line_y - MISS_RANGE

        # 如果箭頭未被擊中，且完全超出判定範圍，則移除
        return arrow_y < self.judgment_line_y - MISS_RANGE
