"""
箭頭物件類別
管理箭頭的生成、移動和狀態
"""

import pygame
from typing import Tuple, Optional
from .constants import ARROW_WIDTH, ARROW_HEIGHT, GAME_AREA_X, GAME_AREA_WIDTH


class Arrow:
    """跳舞機遊戲中的箭頭物件"""

    def __init__(
        self,
        direction: str,
        x: float,
        y: float,
        speed: float,
        image: Optional[pygame.Surface] = None,
    ):
        self.direction = direction  # LEFT, DOWN, UP, RIGHT
        self.x = x
        self.y = y
        self.speed = speed  # 像素/秒
        self.width = ARROW_WIDTH
        self.height = ARROW_HEIGHT
        self.hit = False  # 是否已被擊中
        self.missed = False  # 是否已錯過

        # 圖片處理
        self.image = None
        if image:
            self.image = pygame.transform.scale(image, (self.width, self.height))

        # 根據方向設定回退顏色
        self.colors = {
            "LEFT": (64, 128, 255),  # 藍色
            "DOWN": (255, 255, 64),  # 黃色
            "UP": (64, 255, 128),  # 綠色
            "RIGHT": (192, 64, 255),  # 紫色
        }
        self.color = self.colors.get(direction, (255, 255, 255))

    def update(self, dt: float) -> None:
        """更新箭頭位置"""
        if not self.hit and not self.missed:
            self.y -= self.speed * dt

    def draw(self, screen: pygame.Surface) -> None:
        """繪製箭頭"""
        if not self.hit:
            if self.image:
                # 繪製圖片
                screen.blit(
                    self.image,
                    (self.x - self.width // 2, self.y - self.height // 2),
                )
            else:
                # 繪製回退矩形
                pygame.draw.rect(
                    screen,
                    self.color,
                    (
                        self.x - self.width // 2,
                        self.y - self.height // 2,
                        self.width,
                        self.height,
                    ),
                )
                # 繪製方向指示
                self._draw_arrow_indicator(screen)

    def _draw_arrow_indicator(self, screen: pygame.Surface) -> None:
        """繪製箭頭方向指示符號"""
        center_x = int(self.x)
        center_y = int(self.y)

        if self.direction == "LEFT":
            # 向左箭頭
            points = [
                (center_x + 20, center_y),
                (center_x - 20, center_y),
                (center_x - 5, center_y - 15),
                (center_x - 5, center_y + 15),
            ]
        elif self.direction == "RIGHT":
            # 向右箭頭
            points = [
                (center_x - 20, center_y),
                (center_x + 20, center_y),
                (center_x + 5, center_y - 15),
                (center_x + 5, center_y + 15),
            ]
        elif self.direction == "UP":
            # 向上箭頭
            points = [
                (center_x, center_y + 20),
                (center_x, center_y - 20),
                (center_x - 15, center_y - 5),
                (center_x + 15, center_y - 5),
            ]
        else:  # DOWN
            # 向下箭頭
            points = [
                (center_x, center_y - 20),
                (center_x, center_y + 20),
                (center_x - 15, center_y + 5),
                (center_x + 15, center_y + 5),
            ]

        pygame.draw.polygon(screen, (0, 0, 0), points)

    def get_rect(self) -> pygame.Rect:
        """取得箭頭的矩形碰撞區域"""
        return pygame.Rect(
            self.x - self.width // 2, self.y - self.height // 2, self.width, self.height
        )

    def is_out_of_bounds(self, screen_height: int) -> bool:
        """檢查箭頭是否超出螢幕範圍"""
        arrow_top = self.y - self.height // 2
        return arrow_top < 0 or self.y > screen_height
