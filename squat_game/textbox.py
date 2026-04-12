import cv2
from typing import Literal
from enum import Enum


class Color(Enum):
    """BGR로 정의. value로 사용"""
    BLACK = (0, 0, 0)
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    YELLOW = (0, 255, 255)
    CYAN = (255, 255, 0)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (192, 192, 192)
    DARK_GRAY = (64, 64, 64)
    ORANGE = (0, 165, 255)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)
    BROWN = (42, 42, 165)
    LIGHT_BLUE = (255, 143, 0)  # 008fff
    LIGHT_GREEN = (0, 255, 127)
    LIGHT_RED = (0, 100, 255)
    WHITE = (255, 255, 255)


class TextBox:
    def __init__(
        self,
        frame_width: int,
        frame_height: int,
        anchor: Literal["righttop", "lefttop",
                        "leftbottom", "rightbottom"] = "righttop",
        margin: int = 10,
        padding: int = 20,
        font=cv2.FONT_HERSHEY_DUPLEX,
        font_scale: float = 1,
        thickness: int = 2,
        bg_color: tuple[int, int, int] = Color.LIGHT_GRAY.value
    ) -> None:
        """
        화면에 위치와 스타일을 지정해서 텍스트 박스를 그릴 수 있는 클래스입니다.

        Args:
            frame_width (int): 전체 프레임(이미지)의 가로 크기.
            frame_height (int): 전체 프레임(이미지)의 세로 크기.
            anchor (Literal): 박스의 기준 위치 ("righttop", "lefttop", "leftbottom", "rightbottom").
            margin (int): 박스와 프레임(화면) 끝 사이의 바깥 여백(픽셀).
            padding (int): 박스 내부에서 텍스트와 박스 테두리 사이의 안쪽 여백(픽셀).
            font: 텍스트 폰트 (cv2.FONT_HERSHEY_SIMPLEX 등).
            font_scale (float): 텍스트 크기 배율.
            thickness (int): 텍스트 두께.
            bg_color (tuple): 박스 배경 색상(BGR 튜플).
        """

        self.frame_width = frame_width
        self.frame_height = frame_height
        self.anchor = anchor
        self.margin = margin
        self.padding = padding
        self.font = font
        self.font_scale = font_scale
        self.thickness = thickness
        self.bg_color = bg_color

    def draw(self, frame, lines: list[str], text_colors: list[tuple[int, int, int]]):
        """
        지정한 위치에 여러 줄의 텍스트와 배경 박스를 그립니다.

        Args:
            frame: 텍스트 박스를 그릴 대상 프레임(이미지).
            lines (list[str]): 표시할 텍스트(여러 줄 가능).
            text_colors (list[tuple[int, int, int]]): 각 줄별 텍스트 색상(BGR 튜플).
        """
        # 각 줄의 크기 측정
        sizes = [cv2.getTextSize(line, self.font, self.font_scale, self.thickness)[
            0] for line in lines]
        max_width = max(w for w, h in sizes)
        total_height = sum(h for w, h in sizes) + \
            self.padding * (len(lines) + 1)

        # 사각형 위치 계산
        if self.anchor == "righttop":
            rect_x2 = self.frame_width - self.margin
            rect_x1 = rect_x2 - max_width - 2 * self.padding
            rect_y1 = self.margin
            rect_y2 = rect_y1 + total_height
        elif self.anchor == "lefttop":
            rect_x1 = self.margin
            rect_x2 = rect_x1 + max_width + 2 * self.padding
            rect_y1 = self.margin
            rect_y2 = rect_y1 + total_height
        elif self.anchor == "leftbottom":
            rect_x1 = self.margin
            rect_x2 = rect_x1 + max_width + 2 * self.padding
            rect_y2 = self.frame_height - self.margin
            rect_y1 = rect_y2 - total_height
        elif self.anchor == "rightbottom":
            rect_x2 = self.frame_width - self.margin
            rect_x1 = rect_x2 - max_width - 2 * self.padding
            rect_y2 = self.frame_height - self.margin
            rect_y1 = rect_y2 - total_height
        else:
            # 기본값: 오른쪽 상단
            rect_x2 = self.frame_width - self.margin
            rect_x1 = rect_x2 - max_width - 2 * self.padding
            rect_y1 = self.margin
            rect_y2 = rect_y1 + total_height

        # 배경 사각형
        cv2.rectangle(frame, (rect_x1, rect_y1),
                      (rect_x2, rect_y2), self.bg_color, -1)

        # 각 줄을 정렬해서 그림
        y = rect_y1 + self.padding
        for i, (line, (w, h)) in enumerate(zip(lines, sizes)):
            if self.anchor.endswith("right"):
                x = rect_x2 - self.padding - w
            else:
                x = rect_x1 + self.padding
            color = text_colors[i] if i < len(
                text_colors) else Color.WHITE.value
            cv2.putText(frame, line, (x, y + h), self.font,
                        self.font_scale, color, self.thickness, cv2.LINE_AA)
            y += h + self.padding


if __name__ == "__main__":
    import numpy as np
    import time

    # 더미 프레임 생성 (예: 800x600)
    FRAME_WIDTH = 800
    FRAME_HEIGHT = 600
    test_frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)

    # 예시 텍스트
    dead_enemies: int = 7
    elapsed_time: int = 123
    dead_text: str = f"Dead Enemies: {dead_enemies}"
    time_text: str = f"Survival Time: {elapsed_time}s"

    # TextBox 인스턴스 생성 (anchor 위치 변경 가능)
    textbox = TextBox(
        FRAME_WIDTH, FRAME_HEIGHT, anchor="righttop", margin=0, padding=20, font_scale=0.5, thickness=1, bg_color=(255, 255, 255))
    textbox.draw(test_frame, [dead_text, time_text],
                 [(0, 0, 255), (100, 100, 100)])

    # 다른 위치 예시
    textbox_leftbottom = TextBox(
        FRAME_WIDTH, FRAME_HEIGHT, anchor="leftbottom")
    textbox_leftbottom.draw(test_frame, ["left bottom!", "Hello World!"], [
                            (0, 255, 0), (255, 255, 0)])

    # 결과 확인
    cv2.imshow("Textbox Example", test_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
