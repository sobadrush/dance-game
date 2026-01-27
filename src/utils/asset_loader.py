"""
資源載入器
管理遊戲資源的載入和快取
"""

import pygame
import os
from typing import Dict, Optional
from pathlib import Path


class AssetLoader:
    """資源載入器類別"""

    def __init__(self, base_path: str = "src/assets"):
        self.base_path = Path(base_path)
        self.loaded_images: Dict[str, pygame.Surface] = {}
        self.loaded_sounds: Dict[str, pygame.mixer.Sound] = {}
        self.loaded_fonts: Dict[str, pygame.font.Font] = {}

        # 初始化pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    def load_image(
        self, filename: str, subfolder: str = ""
    ) -> Optional[pygame.Surface]:
        """
        載入圖片資源

        Args:
            filename: 檔案名稱
            subfolder: 子資料夾名稱

        Returns:
            pygame.Surface or None: 載入的圖片表面
        """
        cache_key = f"{subfolder}/{filename}" if subfolder else filename

        if cache_key in self.loaded_images:
            return self.loaded_images[cache_key]

        try:
            file_path = self.base_path / "images"
            if subfolder:
                file_path = file_path / subfolder
            file_path = file_path / filename

            if not file_path.exists():
                # 建立預設圖片
                surface = self._create_default_image(filename)
            else:
                surface = pygame.image.load(str(file_path)).convert_alpha()

            self.loaded_images[cache_key] = surface
            return surface

        except Exception as e:
            print(f"載入圖片失敗 {filename}: {e}")
            surface = self._create_default_image(filename)
            self.loaded_images[cache_key] = surface
            return surface

    def _create_default_image(self, filename: str) -> pygame.Surface:
        """
        建立預設圖片

        Args:
            filename: 檔案名稱（用於決定預設圖片類型）

        Returns:
            pygame.Surface: 預設圖片表面
        """
        surface = pygame.Surface((60, 20))

        # 根據檔名決定顏色
        if "left" in filename.lower():
            surface.fill((255, 0, 0))  # 紅色
        elif "right" in filename.lower():
            surface.fill((255, 255, 0))  # 黃色
        elif "up" in filename.lower():
            surface.fill((0, 0, 255))  # 藍色
        elif "down" in filename.lower():
            surface.fill((0, 255, 0))  # 綠色
        else:
            surface.fill((128, 128, 128))  # 灰色

        return surface

    def load_sound(self, filename: str, subfolder: str = "") -> pygame.mixer.Sound:
        """
        載入音效資源

        Args:
            filename: 檔案名稱
            subfolder: 子資料夾名稱

        Returns:
            pygame.mixer.Sound or None: 載入的音效
        """
        cache_key = f"{subfolder}/{filename}" if subfolder else filename

        if cache_key in self.loaded_sounds:
            return self.loaded_sounds[cache_key]

        try:
            file_path = self.base_path / "sounds"
            if subfolder:
                file_path = file_path / subfolder
            file_path = file_path / filename

            if not file_path.exists():
                # 建立預設音效（靜音）
                sound = self._create_default_sound()
            else:
                sound = pygame.mixer.Sound(str(file_path))

            self.loaded_sounds[cache_key] = sound
            return sound

        except Exception as e:
            print(f"載入音效失敗 {filename}: {e}")
            sound = self._create_default_sound()
            self.loaded_sounds[cache_key] = sound
            return sound

    def _create_default_sound(self) -> pygame.mixer.Sound:
        """建立預設音效（無聲音效）"""
        try:
            # 建立空的音效資料
            sample_rate = 22050
            duration = 0.1  # 0.1秒
            samples = int(sample_rate * duration)

            # 建立無聲的bytearray
            sound_data = bytearray(samples * 2)  # 16-bit音訊

            # 使用bytearray直接建立音效
            sound = pygame.mixer.Sound(buffer=sound_data)

            return sound
        except Exception:
            # 如果失敗，建立一個極短的靜音音效
            return pygame.mixer.Sound(buffer=bytearray(100))

    def load_font(
        self, filename: Optional[str] = None, size: int = 24
    ) -> pygame.font.Font:
        """
        載入字體

        Args:
            filename: 字體檔案名稱，為None時使用預設字體
            size: 字體大小

        Returns:
            pygame.font.Font: 載入的字體
        """
        cache_key = f"{filename}_{size}"

        if cache_key in self.loaded_fonts:
            return self.loaded_fonts[cache_key]

        try:
            if filename:
                file_path = self.base_path / "fonts" / filename
                if file_path.exists():
                    font = pygame.font.Font(str(file_path), size)
                else:
                    # 如果指定的字體檔案不存在，嘗試載入系統字體
                    font = self._load_fallback_font(size)
            else:
                # 未指定字體，載入支援中文的系統字體
                font = self._load_fallback_font(size)

            self.loaded_fonts[cache_key] = font
            return font

        except Exception as e:
            print(f"載入字體失敗 {filename}: {e}")
            font = self._load_fallback_font(size)
            self.loaded_fonts[cache_key] = font
            return font

    def _load_fallback_font(self, size: int) -> pygame.font.Font:
        """載入支援中文的回退系統字體"""
        cjk_font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "C:\\Windows\\Fonts\\msjh.ttc",
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\simsun.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansTC-Regular.otf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]

        for font_path in cjk_font_paths:
            try:
                path_obj = Path(font_path)
                if path_obj.exists():
                    font = pygame.font.Font(str(path_obj), size)
                    return font
            except Exception:
                pass

        fallback_fonts = [
            "notosanscjk",
            "pingfangtc",
            "pingfanghk",
            "microsoftjhenghei",
            "stheitimedium",
            "stheitilight",
            "microsoftyahei",
            "notosanssc",
            "notosanstc",
            "notosansmonoCJK",
            "wenquanyi",
            "droidsansfallback",
            "heiti",
            "simhei",
        ]

        for font_name in fallback_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                if font:
                    return font
            except Exception:
                pass

        for font_name in fallback_fonts:
            try:
                font_path = pygame.font.match_font(font_name)
                if font_path:
                    return pygame.font.Font(font_path, size)
            except Exception:
                pass

        return pygame.font.Font(None, size)

    def set_master_volume(self, volume: float) -> None:
        """
        設定主音量

        Args:
            volume: 音量值 (0.0 - 1.0)
        """
        pygame.mixer.music.set_volume(volume)
        for sound in self.loaded_sounds.values():
            if sound:
                sound.set_volume(volume)

    def cleanup(self) -> None:
        """清理已載入的資源"""
        self.loaded_images.clear()
        self.loaded_sounds.clear()
        self.loaded_fonts.clear()
        pygame.mixer.quit()
