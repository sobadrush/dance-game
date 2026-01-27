"""
配置管理器
管理遊戲配置和設定
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """配置管理器類別"""

    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}

        # 預設配置
        self.default_config = {
            "display": {
                "window_width": 800,
                "window_height": 600,
                "fullscreen": False,
                "fps": 60,
            },
            "audio": {
                "master_volume": 0.7,
                "sfx_volume": 0.8,
                "music_volume": 0.6,
                "enabled": True,
            },
            "gameplay": {
                "default_difficulty": "EASY",
                "show_feedback": True,
                "auto_calibration": False,
            },
            "controls": {
                "key_bindings": {
                    "LEFT": "K_LEFT",
                    "DOWN": "K_DOWN",
                    "UP": "K_UP",
                    "RIGHT": "K_RIGHT",
                    "PAUSE": "K_ESCAPE",
                    "START": "K_RETURN",
                }
            },
        }

        self.load_config()

    def load_config(self) -> None:
        """載入配置檔案"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)

                # 合併載入的配置與預設配置
                self.config = self._deep_merge(
                    self.default_config.copy(), loaded_config
                )
            else:
                # 如果配置檔案不存在，使用預設配置
                self.config = self.default_config.copy()
                self.save_config()

        except Exception as e:
            print(f"載入配置失敗，使用預設配置: {e}")
            self.config = self.default_config.copy()

    def save_config(self) -> bool:
        """
        儲存配置到檔案

        Returns:
            bool: 儲存是否成功
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"儲存配置失敗: {e}")
            return False

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        深度合併兩個字典

        Args:
            base: 基礎字典
            update: 更新字典

        Returns:
            Dict: 合併後的字典
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        取得配置值

        Args:
            key_path: 配置鍵路徑（如 'audio.master_volume'）
            default: 預設值

        Returns:
            Any: 配置值
        """
        keys = key_path.split(".")
        value = self.config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """
        設定配置值

        Args:
            key_path: 配置鍵路徑（如 'audio.master_volume'）
            value: 要設定的值
        """
        keys = key_path.split(".")
        config = self.config

        # 導航到目標位置
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # 設定值
        config[keys[-1]] = value

    def get_display_config(self) -> Dict[str, Any]:
        """取得顯示配置"""
        return self.get("display", {})

    def get_audio_config(self) -> Dict[str, Any]:
        """取得音訊配置"""
        return self.get("audio", {})

    def get_gameplay_config(self) -> Dict[str, Any]:
        """取得遊戲配置"""
        return self.get("gameplay", {})

    def get_controls_config(self) -> Dict[str, Any]:
        """取得控制配置"""
        return self.get("controls", {})

    def reset_to_default(self) -> None:
        """重置為預設配置"""
        self.config = self.default_config.copy()
        self.save_config()

    def export_config(self, file_path: str) -> bool:
        """
        匯出配置到指定檔案

        Args:
            file_path: 匯出檔案路徑

        Returns:
            bool: 匯出是否成功
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"匯出配置失敗: {e}")
            return False

    def import_config(self, file_path: str) -> bool:
        """
        從指定檔案匯入配置

        Args:
            file_path: 匯入檔案路徑

        Returns:
            bool: 匯入是否成功
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported_config = json.load(f)

            self.config = self._deep_merge(self.default_config.copy(), imported_config)
            return self.save_config()
        except Exception as e:
            print(f"匯入配置失敗: {e}")
            return False
