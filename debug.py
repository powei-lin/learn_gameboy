import numpy as np
import cv2
from typing import List

COLORS_BGR = [(180, 119, 31), (14, 127, 255), (44, 160, 44), (40, 39, 214), (189, 103, 148),
              (75, 86, 140), (194, 119, 227), (127, 127, 127), (34, 189, 188), (207, 190, 23)]
SECTION_NAMES = [("ROM", 0x0000, 0x8000),
                 ("Video RAM", 0x8000, 0xa000),
                 ("Externel RAM", 0xa000, 0xc000),
                 ("RAM", 0xc000, 0xe000),
                 ("Other", 0xe000, 0xffff + 1)]


def debug_ram(ram: List[int]):
    ram_img = np.array(ram, np.uint8).reshape(256, -1, 1)
    ram_img = np.concatenate([ram_img for _ in range(3)], axis=2)
    ram_section_img = []
    for color, (name, start, end) in zip(COLORS_BGR, SECTION_NAMES):
        data_length = end - start
        rows = data_length // 256 - 10
        img = np.concatenate([np.ones(data_length, dtype=np.uint8).reshape(-1, 256, 1) * c for c in color], axis=2)
        # print(cv2.getTextSize(name, 1, 1.2, 1))
        # print(img.shape)
        img = cv2.putText(img, f"{name} {start:04X}", (10, rows), 1, 1.2, (0, 0, 0))
        # cv2.imshow("img", img)
        # cv2.waitKey(0)
        ram_section_img.append(img)
    return np.hstack((ram_img, np.vstack(ram_section_img)))
