"""跳舞機遊戲常數設定與配置值"""

# 遊戲視窗設定
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# 遊戲區域設定
GAME_AREA_X = 300
GAME_AREA_WIDTH = 200
JUDGMENT_LINE_Y = 150
ARROW_START_Y = WINDOW_HEIGHT

# 箭頭設定
ARROW_WIDTH = 60
ARROW_HEIGHT = 60
ARROW_SPEED_EASY = 100  # 像素/秒
ARROW_SPEED_NORMAL = 150  # 像素/秒

# 判定範圍設定
PERFECT_RANGE = 20  # 完美判定範圍（像素）
GOOD_RANGE = 40  # 良好判定範圍（像素）
MISS_RANGE = 80  # 失誤判定範圍（像素）

# 分數設定
PERFECT_SCORE = 100
GOOD_SCORE = 50
MISS_SCORE = 0

# 顏色定義
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# 箭頭方向對應
ARROW_DIRECTIONS = {"LEFT": 0, "DOWN": 1, "UP": 2, "RIGHT": 3}

# 按鍵對應 - 延遲導入pygame以避免循環依賴
KEY_MAPPINGS = {"LEFT": "K_LEFT", "DOWN": "K_DOWN", "UP": "K_UP", "RIGHT": "K_RIGHT"}


def get_key_code(direction: str):
    """取得方向鍵對應的pygame按鍵碼"""
    import pygame

    return getattr(pygame, KEY_MAPPINGS[direction])


# 音效設定
MASTER_VOLUME = 0.7
SFX_VOLUME = 0.8
MUSIC_VOLUME = 0.6

# 遊戲狀態
GameState = {
    "MENU": "menu",
    "PLAYING": "playing",
    "PAUSED": "paused",
    "GAME_OVER": "game_over",
}

# 遊戲結束條件
GAME_DURATION_SECONDS = 90
MAX_MISSES = 20

# 難度等級
DifficultyLevel = {"EASY": "easy", "NORMAL": "normal"}
