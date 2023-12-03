import numpy as np
import cv2
from memory import Memory
from enum import IntEnum
from typing import List
from debug import integer_resize

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
BG_SIZE = 256

GRAY_SHADES = [255, 170, 85, 0]


def data_to_tile(data: List[int], palette: int = 0):
    if len(data) != 16:
        raise ValueError
    i = np.array(data, dtype=np.uint8).reshape(8, 2)
    i = np.unpackbits(i, axis=1)
    i = (i[:, :8] + i[:, 8:] * 2)
    p = [0b11 & (palette >> (j * 2)) for j in range(4)]
    p = [GRAY_SHADES[j] for j in p]
    return np.vectorize(p.__getitem__)(i).astype(np.uint8)


class PPUState(IntEnum):
    HBLANK = 0
    VBLANK = 1
    OAM = 2
    DRAWING = 3


class PixelFetcher:
    def __init__(self) -> None:
        self.buffer = []
        self.remain_ticks = 0
        self.tile_index = 0
        self.tile_line = 0

    def tick(self, mem: Memory, pixel_fifo: List[int]):
        pass


class LCD:
    def __init__(self):
        self.screen = np.ones((LCD_HEIGHT, LCD_WIDTH), np.uint8) * 255
        self.bg_map = np.ones((BG_SIZE, BG_SIZE), np.uint8) * 255
        self.screen_list = []
        self.pixel_fifo = []
        self.pixel_fetcher = PixelFetcher()
        self.current_state = PPUState.HBLANK
        self.remain_ticks = 0

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

        self.ly = 0
        self.lyc = 0

    def show(self):
        cv2.imshow("screen", self.screen)
        cv2.imshow("bg", self.bg_map)
        cv2.waitKey(0)

    def _check_control(self, value: int):
        self.lcd_display_enable = ((value >> 7) & 1)
        self.window_tile_map_display_select = ((value >> 6) & 1)
        self.window_display_enable = ((value >> 5) & 1)
        self.bg_and_window_tile_data_select = ((value >> 4) & 1)
        self.bg_tile_map_display_select = ((value >> 3) & 1)
        self.sprite_size = ((value >> 2) & 1)
        self.sprite_display_enable = ((value >> 1) & 1)
        self.bg_display = (value & 1)

    def show_bg_tiles(self, mem: Memory):
        bg = None
        tmp = []
        for i in range(0x8000, 0x9000, 16):
            # print(f"{i:04x}")
            data = [mem.get(i + j) for j in range(16)]
            # if i == 0x8190:
            # for d in data:
            # print(f"{d:02x}")
            # print(mem.get(0xff47))
            img = data_to_tile(data, mem.get(0xff47))
            img = integer_resize(img, 10, with_outline=True)
            tmp.append(img)
            if len(tmp) == 32:
                combined = np.hstack(tmp)
                if bg is not None:
                    bg = np.vstack((bg, combined))
                else:
                    bg = combined
                tmp = []
        cv2.imshow("bg", bg)
        cv2.waitKey(0)

    def show_bg_map(self, mem: Memory, resize_scale: int = 5):
        bg = None
        tmp = []
        for i in range(0x9800, 0x9c00):
            tile_idx = mem.get(i) * 16 + 0x8000
            img = data_to_tile([mem.get(tile_idx + j) for j in range(16)], mem.get(0xff47))
            img = integer_resize(img, resize_scale, with_outline=True)
            tmp.append(img)
            if len(tmp) == 32:
                combined = np.hstack(tmp)
                if bg is not None:
                    bg = np.vstack((bg, combined))
                else:
                    bg = combined
                tmp = []
        cv2.imshow("bg", bg)
        cv2.waitKey(0)

    def tick(self, mem: Memory, cpu_cycle: int = 1):
        self.remain_ticks += cpu_cycle
        self._check_control(mem.get(CONTROL_ADDR_RW))
        if self.lcd_display_enable > 0:

            while self.ly < 144:
                if self.current_state == PPUState.HBLANK:
                    if self.ly == 144:
                        self.current_state = PPUState.VBLANK
                    else:
                        self.current_state = PPUState.OAM
                    pass
                elif self.current_state == PPUState.VBLANK:
                    self.current_state = PPUState.OAM
                elif self.current_state == PPUState.OAM:
                    if self.remain_ticks >= 40:
                        self.current_state = PPUState.DRAWING
                elif self.current_state == PPUState.DRAWING:
                    # p.x = 0
                    # tileLine := p.LY % 8
                    # tileMapRowAddr := 0x9800 + (uint16(p.LY/8) * 32)
                    self.current_state = PPUState.HBLANK
                else:
                    raise ValueError
                break

            self.ly = mem.get(Y_COORDINATE_R)
            self.lyc = mem.get(LY_COMPARE_RW)
            print("ly", self.ly)
            scy = mem.get(0xff42)
            scx = mem.get(0xff43)
            for i in range(0xff40, 0xff4a):
                v = mem.get(i)
                print(f"{i:04x}, {v:08b}, {v}")
            print("LCD turned on")
            self.show_bg_tiles(mem)
            self.show_bg_map(mem)
            print(scx, scy)
            raise NotImplementedError
