import numpy as np
import cv2

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

    def show(self):
        cv2.imshow("screen", self.screen)
        cv2.waitKey(0)
