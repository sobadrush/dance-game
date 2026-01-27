"""
遊戲引擎主類別
協調所有遊戲系統的運作
"""

import pygame
import time
import random
from typing import List, Optional

from .constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    GameState,
    GAME_DURATION_SECONDS,
    MAX_MISSES,
    JUDGMENT_LINE_Y,
    ARROW_START_Y,
    ARROW_WIDTH,
    ARROW_HEIGHT,
    BLACK,
    WHITE,
    GRAY,
    YELLOW,
)
from .arrow import Arrow
from .timing import Timing
from .score import Score
from .difficulty import Difficulty
from .audio_manager import AudioManager
from utils.asset_loader import AssetLoader
from utils.config import Config


class GameEngine:
    """遊戲引擎主類別"""

    def __init__(self):
        pygame.init()

        # 初始化視窗
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("跳舞機遊戲")
        self.clock = pygame.time.Clock()

        # 初始化系統
        self.asset_loader = AssetLoader()
        self.config = Config()
        self.timing = Timing()
        self.score = Score()
        self.difficulty = Difficulty()
        self.audio_manager = AudioManager(self.asset_loader)

        # 遊戲狀態
        self.running = True
        self.game_state = GameState["MENU"]
        self.current_time = 0.0
        self.game_start_time = 0.0

        # 箭頭管理
        self.arrows: List[Arrow] = []
        self.last_spawn_time = 0.0

        # 輸入狀態
        self.keys_pressed = set()
        self.last_key_press_time = {}

        # 字體
        self.font_large = self.asset_loader.load_font(size=48)
        self.font_medium = self.asset_loader.load_font(size=32)
        self.font_small = self.asset_loader.load_font(size=24)

        # 設定音量
        audio_config = self.config.get_audio_config()
        master_volume = audio_config.get("master_volume", 0.7)
        self.asset_loader.set_master_volume(master_volume)
        self.audio_manager.set_master_volume(master_volume)

        # 預載入箭頭圖片
        self.arrow_images = {
            "LEFT": self.asset_loader.load_image("arrow_left.png", subfolder="arrows"),
            "DOWN": self.asset_loader.load_image("arrow_down.png", subfolder="arrows"),
            "UP": self.asset_loader.load_image("arrow_up.png", subfolder="arrows"),
            "RIGHT": self.asset_loader.load_image(
                "arrow_right.png", subfolder="arrows"
            ),
        }

    def run(self) -> None:
        """執行遊戲主循環"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # 轉換為秒
            self.current_time += dt

            self._handle_events()
            self._update(dt)
            self._draw()

        self._cleanup()

    def _handle_events(self) -> None:
        """處理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)

            elif event.type == pygame.KEYUP:
                self._handle_key_up(event.key)

    def _handle_key_down(self, key: int) -> None:
        """處理按鍵按下事件"""
        self.keys_pressed.add(key)

        # 根據遊戲狀態處理按鍵
        if self.game_state == GameState["MENU"]:
            self._handle_menu_key(key)
        elif self.game_state == GameState["PLAYING"]:
            self._handle_game_key(key)
        elif self.game_state == GameState["PAUSED"]:
            self._handle_pause_key(key)
        elif self.game_state == GameState["GAME_OVER"]:
            self._handle_game_over_key(key)

    def _handle_key_up(self, key: int) -> None:
        """處理按鍵釋放事件"""
        self.keys_pressed.discard(key)

    def _handle_menu_key(self, key: int) -> None:
        """處理選單狀態的按鍵"""
        if key == pygame.K_RETURN:
            self._start_game()
        elif key == pygame.K_1:
            self.difficulty.set_difficulty("EASY")
            self._start_game()
        elif key == pygame.K_2:
            self.difficulty.set_difficulty("NORMAL")
            self._start_game()
        elif key == pygame.K_ESCAPE:
            self.running = False

    def _handle_game_key(self, key: int) -> None:
        """處理遊戲狀態的按鍵"""
        if key == pygame.K_ESCAPE:
            self.game_state = GameState["PAUSED"]
            self.audio_manager.pause_music()
        else:
            self._check_arrow_hit(key)

    def _handle_pause_key(self, key: int) -> None:
        """處理暫停狀態的按鍵"""
        if key == pygame.K_ESCAPE:
            self.game_state = GameState["PLAYING"]
            self.audio_manager.resume_music()
        elif key == pygame.K_q:
            self.audio_manager.stop_music()
            self.game_state = GameState["MENU"]

    def _handle_game_over_key(self, key: int) -> None:
        """處理遊戲結束狀態的按鍵"""
        if key == pygame.K_RETURN:
            self._start_game()
        elif key == pygame.K_ESCAPE:
            self.audio_manager.stop_music()
            self.game_state = GameState["MENU"]

    def _check_arrow_hit(self, key: int) -> None:
        """檢查箭頭擊中判定"""
        # 防止重複觸發
        current_time = time.time()
        if key in self.last_key_press_time:
            if current_time - self.last_key_press_time[key] < 0.1:
                return
        self.last_key_press_time[key] = current_time

        # 對應按鍵到方向
        direction_map = {
            pygame.K_LEFT: "LEFT",
            pygame.K_DOWN: "DOWN",
            pygame.K_UP: "UP",
            pygame.K_RIGHT: "RIGHT",
        }

        if key not in direction_map:
            return

        direction = direction_map[key]

        # 尋找最近的箭頭
        closest_arrow = None
        closest_distance = float("inf")

        for arrow in self.arrows:
            if arrow.direction == direction and not arrow.hit and not arrow.missed:
                distance = abs(arrow.y - JUDGMENT_LINE_Y)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_arrow = arrow

        # 判定時機
        if closest_arrow and closest_distance <= 80:
            judgment, base_score = self.timing.check_timing(
                closest_arrow.y, self.current_time, direction
            )

            # 標記箭頭為已擊中
            closest_arrow.hit = True

            # 計算分數
            adjusted_score = self.difficulty.calculate_adjusted_score(base_score)
            actual_score, combo_milestone = self.score.add_score(
                judgment, adjusted_score, self.current_time
            )

            # 播放音效
            self._play_hit_sound(judgment)
            if combo_milestone:
                self.audio_manager.play_sfx("combo")

    def _play_hit_sound(self, judgment: str) -> None:
        """播放擊中音效"""
        self.audio_manager.play_sfx(judgment.lower())

    def _update(self, dt: float) -> None:
        """更新遊戲狀態"""
        if self.game_state == GameState["PLAYING"]:
            self._update_game(dt)

        # 更新時機系統
        self.timing.update_feedback(self.current_time)

        # 更新分數系統
        self.score.update_combo_effects(self.current_time)

    def _update_game(self, dt: float) -> None:
        """更新遊戲邏輯"""
        # 生成新箭頭
        self._spawn_arrows(dt)

        # 更新箭頭位置
        for arrow in self.arrows:
            arrow.update(dt)

        # 移除超出範圍的箭頭
        self._remove_out_of_bounds_arrows()

        # 檢查遊戲結束條件
        self._check_game_over()

    def _spawn_arrows(self, dt: float) -> None:
        """生成新箭頭"""
        spawn_interval = self.difficulty.get_spawn_interval()

        if self.current_time - self.last_spawn_time >= spawn_interval:
            # 隨機選擇方向
            directions = ["LEFT", "DOWN", "UP", "RIGHT"]
            direction = random.choice(directions)

            # 取得位置
            x, _ = self.difficulty.get_arrow_position(direction)
            y = ARROW_START_Y
            speed = self.difficulty.get_arrow_speed()

            # 建立箭頭
            arrow_image = self.arrow_images.get(direction)
            arrow = Arrow(direction, x, y, speed, image=arrow_image)
            self.arrows.append(arrow)

            self.last_spawn_time = self.current_time

    def _remove_out_of_bounds_arrows(self) -> None:
        """移除超出範圍的箭頭"""
        arrows_to_remove = []

        for arrow in self.arrows:
            if self.timing.should_remove_arrow(arrow.y, arrow.hit):
                arrows_to_remove.append(arrow)

                # 如果箭頭未被擊中且超出範圍，記錄為Miss
                if not arrow.hit and not arrow.missed:
                    self.score.add_score("MISS", 0)

        for arrow in arrows_to_remove:
            self.arrows.remove(arrow)

    def _check_game_over(self) -> None:
        """檢查遊戲結束條件"""
        if self.game_state != GameState["PLAYING"]:
            return

        elapsed = self.current_time - self.game_start_time
        if elapsed >= GAME_DURATION_SECONDS or self.score.miss_count >= MAX_MISSES:
            self.audio_manager.stop_music()
            self.game_state = GameState["GAME_OVER"]

    def _draw(self) -> None:
        """繪製遊戲畫面"""
        self._draw_background()

        if self.game_state == GameState["MENU"]:
            self._draw_menu()
        elif self.game_state == GameState["PLAYING"]:
            self._draw_game()
        elif self.game_state == GameState["PAUSED"]:
            self._draw_game()
            self._draw_pause_overlay()
        elif self.game_state == GameState["GAME_OVER"]:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_menu(self) -> None:
        """繪製選單"""
        # 標題
        title_text = "Dance Game"
        title_surface = self.font_large.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_surface, title_rect)

        # 難度選擇
        easy_text = "1. Easy Mode"
        easy_surface = self.font_medium.render(easy_text, True, WHITE)
        easy_rect = easy_surface.get_rect(center=(WINDOW_WIDTH // 2, 300))
        self.screen.blit(easy_surface, easy_rect)

        normal_text = "2. Normal Mode"
        normal_surface = self.font_medium.render(normal_text, True, WHITE)
        normal_rect = normal_surface.get_rect(center=(WINDOW_WIDTH // 2, 350))
        self.screen.blit(normal_surface, normal_rect)

        # 操作說明
        instructions = ["Use Arrow Keys to Play", "ESC to Pause", "ESC in Menu to Quit"]

        y_offset = 450
        for instruction in instructions:
            inst_surface = self.font_small.render(instruction, True, GRAY)
            inst_rect = inst_surface.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(inst_surface, inst_rect)
            y_offset += 30

    def _draw_game(self) -> None:
        """繪製遊戲畫面"""
        # 繪製判定線與背景箭頭
        pygame.draw.line(
            self.screen, GRAY, (250, JUDGMENT_LINE_Y), (550, JUDGMENT_LINE_Y), 1
        )
        for direction, img in self.arrow_images.items():
            if img:
                x, _ = self.difficulty.get_arrow_position(direction)
                # 建立半透明的背景箭頭
                ghost_img = pygame.transform.scale(
                    img, (ARROW_WIDTH, ARROW_HEIGHT)
                ).copy()
                ghost_img.fill(
                    (100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT
                )
                self.screen.blit(
                    ghost_img,
                    (x - ARROW_WIDTH // 2, JUDGMENT_LINE_Y - ARROW_HEIGHT // 2),
                )

        # 繪製箭頭
        for arrow in self.arrows:
            arrow.draw(self.screen)

        # 繪製判定回饋
        self._draw_feedback()

        # 繪製UI
        self._draw_ui()

    def _draw_feedback(self) -> None:
        """繪製判定回饋"""
        for feedback in self.timing.feedback_messages:
            age = self.current_time - feedback["time"]
            alpha = max(0, 1 - age / 0.5)  # 淡出效果

            if alpha > 0:
                text = feedback["text"]
                color = feedback["color"]

                # 建立半透明表面
                text_surface = self.font_large.render(text, True, color)
                text_surface.set_alpha(int(alpha * 255))

                # 繪製在判定線附近
                text_rect = text_surface.get_rect(
                    center=(WINDOW_WIDTH // 2, JUDGMENT_LINE_Y - 50)
                )
                self.screen.blit(text_surface, text_rect)

    def _draw_ui(self) -> None:
        """繪製UI介面"""
        # 分數
        score_text = f"Score: {self.score.total_score}"
        score_surface = self.font_medium.render(score_text, True, WHITE)
        self.screen.blit(score_surface, (50, 50))

        # 連擊
        combo_text = f"Combo: {self.score.combo}"
        combo_surface = self.font_medium.render(combo_text, True, YELLOW)
        self.screen.blit(combo_surface, (50, 90))

        # 難度
        difficulty_text = f"Difficulty: {self.difficulty.get_difficulty_name()}"
        difficulty_surface = self.font_small.render(difficulty_text, True, WHITE)
        self.screen.blit(difficulty_surface, (50, 130))

        # 準確率
        accuracy = self.score.get_accuracy()
        accuracy_text = f"Accuracy: {accuracy:.1f}%"
        accuracy_surface = self.font_small.render(accuracy_text, True, WHITE)
        self.screen.blit(accuracy_surface, (50, 160))

        self._draw_combo_effects()

    def _draw_combo_effects(self) -> None:
        for effect in self.score.combo_effects:
            age = self.current_time - effect["time"]
            alpha = max(0, 1 - age / 2.0)

            if alpha > 0:
                text = f"{effect['combo']} COMBO!"
                text_surface = self.font_medium.render(text, True, YELLOW)
                text_surface.set_alpha(int(alpha * 255))

                y_offset = int(age * 20)
                text_rect = text_surface.get_rect(
                    center=(WINDOW_WIDTH - 120, 80 - y_offset)
                )
                self.screen.blit(text_surface, text_rect)

    def _draw_background(self) -> None:
        """繪製復古像素背景"""
        self.screen.fill(BLACK)
        line_spacing = 6
        pulse = int(self.current_time * 8)
        for y in range(0, WINDOW_HEIGHT, line_spacing):
            shade = 16 if ((y // line_spacing + pulse) % 2 == 0) else 8
            pygame.draw.line(
                self.screen,
                (shade, shade, shade),
                (0, y),
                (WINDOW_WIDTH, y),
                1,
            )

    def _draw_pause_overlay(self) -> None:
        """繪製暫停覆蓋層"""
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 暫停文字
        pause_text = "GAME PAUSED"
        pause_surface = self.font_large.render(pause_text, True, WHITE)
        pause_rect = pause_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        )
        self.screen.blit(pause_surface, pause_rect)

        # 操作提示
        resume_text = "ESC to Resume"
        resume_surface = self.font_medium.render(resume_text, True, WHITE)
        resume_rect = resume_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
        )
        self.screen.blit(resume_surface, resume_rect)

        quit_text = "Q to Menu"
        quit_surface = self.font_medium.render(quit_text, True, WHITE)
        quit_rect = quit_surface.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60)
        )
        self.screen.blit(quit_surface, quit_rect)

    def _draw_game_over(self) -> None:
        """繪製遊戲結束畫面"""
        # 遊戲結束文字
        game_over_text = "GAME OVER"
        game_over_surface = self.font_large.render(game_over_text, True, WHITE)
        game_over_rect = game_over_surface.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(game_over_surface, game_over_rect)

        # 最終分數
        final_score_text = f"Final Score: {self.score.total_score}"
        final_score_surface = self.font_medium.render(final_score_text, True, YELLOW)
        final_score_rect = final_score_surface.get_rect(center=(WINDOW_WIDTH // 2, 280))
        self.screen.blit(final_score_surface, final_score_rect)

        # 統計資訊
        stats = self.score.get_score_breakdown()
        stats_text = [
            f"Max Combo: {stats['max_combo']}",
            f"Perfect: {stats['perfect_count']}",
            f"Good: {stats['good_count']}",
            f"Miss: {stats['miss_count']}",
            f"Accuracy: {stats['accuracy']:.1f}%",
        ]

        y_offset = 340
        for stat in stats_text:
            stat_surface = self.font_small.render(stat, True, WHITE)
            stat_rect = stat_surface.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(stat_surface, stat_rect)
            y_offset += 30

        # 操作提示
        restart_text = "ENTER to Restart"
        restart_surface = self.font_medium.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH // 2, 500))
        self.screen.blit(restart_surface, restart_rect)

        menu_text = "ESC to Menu"
        menu_surface = self.font_medium.render(menu_text, True, WHITE)
        menu_rect = menu_surface.get_rect(center=(WINDOW_WIDTH // 2, 540))
        self.screen.blit(menu_surface, menu_rect)

    def _start_game(self) -> None:
        """開始新遊戲"""
        self.game_state = GameState["PLAYING"]
        self.arrows.clear()
        self.score.reset()
        self.timing = Timing()
        self.last_spawn_time = 0.0
        self.last_key_press_time.clear()
        self.game_start_time = self.current_time

        # 播放背景音樂
        self.audio_manager.play_music("background.wav")

    def _cleanup(self) -> None:
        """清理資源"""
        self.audio_manager.cleanup()
        self.asset_loader.cleanup()
        pygame.quit()
