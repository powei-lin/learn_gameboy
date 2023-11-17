import numpy as np
import cv2
from memory import Memory

CONTROL_ADDR_RW = 0xff40
STATUS_ADDR_RW = 0xff41
SCROLL_Y_RW = 0xff42
SCROLL_X_RW = 0xff43
Y_COORDINATE_R = 0xff44
LY_COMPARE_RW = 0xff45
WINDOW_Y_POSITION_RW = 0xff4a
WINDOW_X_POSITION_MINUS_7_RW = 0xff4b

LCD_WIDTH = 160
LCD_HEIGHT = 144


class LCD:
    def __init__(self):
        self.screen = np.ones((LCD_HEIGHT, LCD_WIDTH), np.uint8) * 255

        # FF40 (order bit 7 -> 0)
        self.lcd_display_enable = 0              # (0=Off, 1=On)
        self.window_tile_map_display_select = 0  # (0=9800-9BFF, 1=9C00-9FFF)
        self.window_display_enable = 0           # (0=Off, 1=On)
        self.bg_and_window_tile_data_select = 0  # (0=8800-97FF, 1=8000-8FFF)
        self.bg_tile_map_display_select = 0      # (0=9800-9BFF, 1=9C00-9FFF)
        self.sprite_size = 0                     # (0=8x8, 1=8x16)
        self.sprite_display_enable = 0           # (0=Off, 1=On)
        self.bg_display = 0                      # (0=Off, 1=On)

        # FF41 - STAT - LCDC Status (R/W)
        self.ly_coincidence_interrupt = 0  # Bit 6 - LYC=LY Coincidence Interrupt (1=Enable) (Read/Write)
        self.mode_2_oam_interrupt = 0      # Bit 5 - Mode 2 OAM Interrupt         (1=Enable) (Read/Write)
        self.mode_1_vblank_interrupt = 0   # Bit 4 - Mode 1 V-Blank Interrupt     (1=Enable) (Read/Write)
        self.mode_0_hblank_interrupt = 0   # Bit 3 - Mode 0 H-Blank Interrupt     (1=Enable) (Read/Write)
        self.coincidence_flag = 0          # Bit 2 - Coincidence Flag  (0:LYC<>LY, 1:LYC=LY) (Read Only)
        self.mode_flag = 0                 # Bit 1-0 - Mode Flag       (Mode 0-3, see below) (Read Only)
        # 0: During H-Blank
        # 1: During V-Blank
        # 2: During Searching OAM-RAM
        # 3: During Transfering Data to LCD Driver

    def show(self):
        cv2.imshow("screen", self.screen)
        cv2.waitKey(0)

    def tick(self, mem: Memory):
        pass
