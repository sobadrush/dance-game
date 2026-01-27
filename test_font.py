#!/usr/bin/env python3
"""
測試字體渲染問題
"""

import pygame
import sys
from pathlib import Path

# 添加src目錄到Python路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.asset_loader import AssetLoader


def test_font_rendering():
    """測試字體渲染"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    asset_loader = AssetLoader()

    # 測試不同字體
    fonts = {
        "default": asset_loader.load_font(None, 32),
        "default_size_24": asset_loader.load_font(None, 24),
        "default_size_48": asset_loader.load_font(None, 48),
    }

    # 測試文字
    test_texts = [
        "Dance Game",
        "Press 1 for Easy",
        "Score: 0",
        "Perfect",
        "Good",
        "Miss",
    ]

    running = True
    y_offset = 50

    print("測試字體渲染...")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((0, 0, 0))

        # 渲染測試文字
        y = 50
        for font_name, font in fonts.items():
            title = f"Font: {font_name}"
            try:
                surface = font.render(title, True, (255, 255, 255))
                screen.blit(surface, (50, y))
                print(f"✓ {font_name}: '{title}' 渲染成功")
                y += 40
            except Exception as e:
                error_text = f"✗ {font_name}: '{title}' 渲染失敗: {e}"
                print(error_text)
                try:
                    surface = fonts["default"].render(error_text, True, (255, 0, 0))
                    screen.blit(surface, (50, y))
                    y += 40
                except:
                    y += 40

        # 渲染測試文字
        for text in test_texts:
            try:
                surface = fonts["default"].render(text, True, (255, 255, 255))
                screen.blit(surface, (50, y))
                print(f"✓ Text: '{text}' 渲染成功")
                y += 30
            except Exception as e:
                error_text = f"✗ '{text}' 渲染失敗: {e}"
                print(error_text)
                try:
                    surface = fonts["default"].render(error_text, True, (255, 0, 0))
                    screen.blit(surface, (50, y))
                    y += 30
                except:
                    y += 30

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    test_font_rendering()
