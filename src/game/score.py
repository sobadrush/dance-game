"""
計分系統
管理遊戲分數、連擊和統計資訊
"""

from typing import Dict, List, Tuple, Union
import time


class Score:
    """計分系統類別"""

    def __init__(self):
        self.total_score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfect_count = 0
        self.good_count = 0
        self.miss_count = 0

        # 分數歷史記錄
        self.score_history: List[Dict] = []

        # 連擊獎勵設定
        self.combo_bonus_threshold = 10  # 每10連擊給予獎勵
        self.combo_bonus_score = 50  # 連擊獎勵分數

        # 統計資訊
        self.total_arrows = 0
        self.hit_arrows = 0

        # 特殊效果
        self.last_combo_time = 0
        self.combo_effects = []

    def add_score(
        self, judgment: str, base_score: int, current_game_time: float
    ) -> Tuple[int, bool]:
        """
        添加分數並處理連擊計算

        Args:
            judgment: 判定等級 (PERFECT, GOOD, MISS)
            base_score: 基礎分數
            current_game_time: 當前遊戲時間

        Returns:
            Tuple[int, bool]: (實際獲得的分數, 是否觸發連擊獎勵里程碑)
        """
        actual_score = base_score
        combo_milestone = False

        # 更新統計
        self.total_arrows += 1

        if judgment == "PERFECT":
            self.perfect_count += 1
            self.hit_arrows += 1
            self.combo += 1
        elif judgment == "GOOD":
            self.good_count += 1
            self.hit_arrows += 1
            self.combo += 1
        elif judgment == "MISS" or judgment == "MISS_FAR":
            self.miss_count += 1
            self._reset_combo()
            return (0, False)

        # 更新總分
        self.total_score += actual_score

        # 連擊獎勵計算
        if self.combo > 0 and self.combo % self.combo_bonus_threshold == 0:
            self.total_score += self.combo_bonus_score
            combo_milestone = True

        # 每次正向連擊都觸發特效
        self._trigger_combo_effect(current_game_time)

        # 更新最大連擊
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        # 記錄分數歷史
        self._record_score_history(judgment, actual_score, current_game_time)

        return (actual_score, combo_milestone)

    def _reset_combo(self) -> None:
        """重置連擊計數"""
        self.combo = 0

    def _trigger_combo_effect(self, current_time: float) -> None:
        """觸發連擊特效"""
        self.last_combo_time = current_time
        self.combo_effects.append({"time": current_time, "combo": self.combo})

    def _record_score_history(
        self, judgment: str, score: int, current_time: float
    ) -> None:
        """記錄分數歷史"""
        self.score_history.append(
            {
                "judgment": judgment,
                "score": score,
                "combo": self.combo,
                "total_score": self.total_score,
                "time": current_time,
            }
        )

        # 限制歷史記錄長度
        if len(self.score_history) > 100:
            self.score_history = self.score_history[-50:]

    def get_accuracy(self) -> float:
        """計算準確率"""
        if self.total_arrows == 0:
            return 0.0
        return (self.hit_arrows / self.total_arrows) * 100.0

    def get_score_breakdown(self) -> Dict[str, Union[int, float]]:
        """取得分數詳細資訊"""
        return {
            "total_score": self.total_score,
            "combo": self.combo,
            "max_combo": self.max_combo,
            "perfect_count": self.perfect_count,
            "good_count": self.good_count,
            "miss_count": self.miss_count,
            "accuracy": round(self.get_accuracy(), 2),
        }

    def reset(self) -> None:
        """重置計分系統"""
        self.total_score = 0
        self.combo = 0
        self.max_combo = 0
        self.perfect_count = 0
        self.good_count = 0
        self.miss_count = 0
        self.score_history.clear()
        self.total_arrows = 0
        self.hit_arrows = 0
        self.combo_effects.clear()

    def update_combo_effects(self, current_time: float) -> None:
        """更新連擊特效，移除過期效果"""
        self.combo_effects = [
            effect
            for effect in self.combo_effects
            if current_time - effect["time"] < 2.0  # 2秒後移除特效
        ]
