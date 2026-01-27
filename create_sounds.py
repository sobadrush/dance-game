#!/usr/bin/env python3
"""
創建基本音效檔案的腳本
"""

import numpy as np
import pygame
from pathlib import Path


def create_tone(
    frequency: float, duration: float, sample_rate: int = 22050
) -> np.ndarray:
    """創建單音調"""
    frames = int(duration * sample_rate)
    arr = np.zeros(frames)
    for i in range(frames):
        arr[i] = np.sin(2 * np.pi * frequency * i / sample_rate)
    return arr


def create_perfect_sound() -> np.ndarray:
    """Perfect音效 - 高音調"""
    frequency = 880  # A5
    duration = 0.15
    tone = create_tone(frequency, duration)
    # 添加淡出效果
    fade_frames = int(0.05 * 22050)
    tone[-fade_frames:] *= np.linspace(1, 0, fade_frames)
    return tone


def create_good_sound() -> np.ndarray:
    """Good音效 - 中音調"""
    frequency = 660  # E5
    duration = 0.12
    tone = create_tone(frequency, duration)
    fade_frames = int(0.04 * 22050)
    tone[-fade_frames:] *= np.linspace(1, 0, fade_frames)
    return tone


def create_miss_sound() -> np.ndarray:
    """Miss音效 - 低音調，下降"""
    duration = 0.2
    frames = int(duration * 22050)
    arr = np.zeros(frames)
    for i in range(frames):
        # 從300Hz下降到100Hz
        frequency = 300 - (200 * i / frames)
        arr[i] = np.sin(2 * np.pi * frequency * i / 22050) * 0.3
    return arr


def create_combo_sound() -> np.ndarray:
    """Combo音效 - 上升音調"""
    duration = 0.25
    frames = int(duration * 22050)
    arr = np.zeros(frames)
    for i in range(frames):
        # 從440Hz上升到880Hz
        frequency = 440 + (440 * i / frames)
        arr[i] = np.sin(2 * np.pi * frequency * i / 22050) * 0.5
    return arr


def create_background_music() -> np.ndarray:
    """背景音樂 - 簡單的循環節奏"""
    duration = 4.0  # 4秒循環
    sample_rate = 22050
    frames = int(duration * sample_rate)
    arr = np.zeros(frames)

    # 創建簡單的鼓點節奏
    beat_interval = int(0.5 * sample_rate)  # 每0.5秒一拍

    for beat_start in range(0, frames, beat_interval):
        if beat_start + 100 < frames:
            # 低頻鼓點
            for i in range(100):
                arr[beat_start + i] = (
                    np.sin(2 * np.pi * 60 * i / sample_rate) * 0.3 * np.exp(-i / 20)
                )

    # 添加簡單的貝斯線
    bass_pattern = [220, 220, 165, 220]  # A3, A3, E3, A3
    note_duration = int(duration * sample_rate / 4)

    for i, freq in enumerate(bass_pattern):
        note_start = i * note_duration
        note_end = min(note_start + note_duration, frames)
        for j in range(note_start, note_end):
            arr[j] += np.sin(2 * np.pi * freq * (j - note_start) / sample_rate) * 0.1

    return arr


def save_wav(data: np.ndarray, filename: Path, sample_rate: int = 22050):
    """保存WAV檔案"""
    # 轉換為16-bit整數
    data_int = (data * 32767).astype(np.int16)

    # 使用pygame保存
    try:
        sound = pygame.sndarray.make_sound(data_int)
        pygame.mixer.init()

        # 創建臨時檔案
        temp_file = str(filename)

        # 使用簡單的方法保存
        with open(temp_file, "wb") as f:
            f.write(b"RIFF")
            f.write((36 + len(data_int) * 2).to_bytes(4, "little"))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write((16).to_bytes(4, "little"))
            f.write((1).to_bytes(2, "little"))  # PCM
            f.write((1).to_bytes(2, "little"))  # Mono
            f.write(sample_rate.to_bytes(4, "little"))
            f.write((sample_rate * 2).to_bytes(4, "little"))
            f.write((2).to_bytes(2, "little"))
            f.write((16).to_bytes(2, "little"))
            f.write(b"data")
            f.write((len(data_int) * 2).to_bytes(4, "little"))
            f.write(data_int.tobytes())

        print(f"成功創建 {filename}")
    except Exception as e:
        print(f"創建 {filename} 失敗: {e}")


def main():
    """主函數"""
    pygame.mixer.init()

    # 確保目錄存在
    assets_dir = Path("src/assets/sounds")
    effects_dir = assets_dir / "effects"
    music_dir = assets_dir / "music"

    effects_dir.mkdir(parents=True, exist_ok=True)
    music_dir.mkdir(parents=True, exist_ok=True)

    # 創建音效
    print("創建音效檔案...")
    save_wav(create_perfect_sound(), effects_dir / "perfect.wav")
    save_wav(create_good_sound(), effects_dir / "good.wav")
    save_wav(create_miss_sound(), effects_dir / "miss.wav")
    save_wav(create_combo_sound(), effects_dir / "combo.wav")

    # 創建背景音樂
    print("創建背景音樂...")
    save_wav(create_background_music(), music_dir / "background.wav")

    print("所有音效檔案創建完成！")


if __name__ == "__main__":
    main()
