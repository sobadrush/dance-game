"""
跳舞機遊戲主程式入口
"""

import sys
import os
import pygame
from pathlib import Path

# 添加src目錄到Python路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from game.engine import GameEngine


def main():
    """主程式入口"""
    try:
        # 建立並執行遊戲引擎
        game = GameEngine()
        game.run()
    except KeyboardInterrupt:
        print("遊戲被中斷")
    except Exception as e:
        print(f"遊戲執行錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
