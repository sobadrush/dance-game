"""
音效管理器
處理背景音樂和音效播放
"""

import pygame
from typing import Optional
from utils.asset_loader import AssetLoader


class AudioManager:
    """音效管理器類別"""

    def __init__(self, asset_loader: AssetLoader):
        self.asset_loader = asset_loader
        self.current_music = None
        self.music_volume = 0.6
        self.sfx_volume = 0.8

        # 預載入音效檔案
        self._load_sfx()

    def _load_sfx(self) -> None:
        """預載入音效檔案"""
        self.sfx = {
            "perfect": self.asset_loader.load_sound("perfect.wav", "effects"),
            "good": self.asset_loader.load_sound("good.wav", "effects"),
            "miss": self.asset_loader.load_sound("miss.wav", "effects"),
            "combo": self.asset_loader.load_sound("combo.wav", "effects"),
        }

        # 設定音效音量（載入成功才設定）
        for sfx in self.sfx.values():
            if sfx:
                sfx.set_volume(self.sfx_volume)

    def play_music(self, music_file: str, loop: bool = True) -> bool:
        """
        播放背景音樂

        Args:
            music_file: 音樂檔案名稱
            loop: 是否循環播放

        Returns:
            bool: 播放是否成功
        """
        try:
            music_path = self.asset_loader.base_path / "sounds" / "music" / music_file
            if music_path.exists():
                pygame.mixer.music.load(str(music_path))
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = music_file
                return True
            return False
        except Exception as e:
            print(f"載入音樂失敗 {music_file}: {e}")
            return False

    def stop_music(self) -> None:
        """停止背景音樂"""
        pygame.mixer.music.stop()
        self.current_music = None

    def pause_music(self) -> None:
        """暫停背景音樂"""
        pygame.mixer.music.pause()

    def resume_music(self) -> None:
        """恢復背景音樂"""
        if self.current_music:
            pygame.mixer.music.unpause()

    def play_sfx(self, sfx_name: str) -> None:
        """
        播放音效

        Args:
            sfx_name: 音效名稱
        """
        if sfx_name in self.sfx and self.sfx[sfx_name]:
            self.sfx[sfx_name].play()

    def set_music_volume(self, volume: float) -> None:
        """
        設定音樂音量

        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        """
        設定音效音量

        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sfx in self.sfx.values():
            if sfx:
                sfx.set_volume(self.sfx_volume)

    def set_master_volume(self, volume: float) -> None:
        """
        設定主音量

        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        normalized_volume = max(0.0, min(1.0, volume))

        # 設定音樂音量
        self.set_music_volume(normalized_volume)

        # 設定音效音量
        self.set_sfx_volume(normalized_volume)

        # 更新asset_loader的主音量
        self.asset_loader.set_master_volume(normalized_volume)

    def get_music_status(self) -> dict:
        """取得音樂播放狀態"""
        return {
            "is_playing": pygame.mixer.music.get_busy() != 0,
            "is_paused": pygame.mixer.music.get_busy() == 0
            and self.current_music is not None,
            "current_music": self.current_music,
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
        }

    def cleanup(self) -> None:
        """清理音效資源"""
        self.stop_music()

        # 清理音效
        for sfx in self.sfx.values():
            if sfx:
                sfx.stop()
