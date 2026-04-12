from random import randint
import cv2
import numpy as np
from typing import Any, Self
from .cooltime import CoolTime
from .textbox import Color


class BasicEntity:
    def __init__(self,
                 start: tuple[int, int], end: tuple[int, int],
                 body_color: tuple[int, int, int],
                 speed: float = 10.0,
                 hp: int = 100,
                 size: float = 1) -> None:
        self.hp = hp
        self.max_hp = hp
        self.x = start[0]
        self.y = start[1]
        self.body_color = body_color

        self.size = size
        self.head_radius = int(np.ceil(20 * self.size))
        self.body_length = int(np.ceil(50 * self.size))
        self.arm_length = int(np.ceil(30 * self.size))
        self.leg_length = int(np.ceil(40 * self.size))
        self.line_thickness = int(np.ceil(2 * self.size))

        self.health_bar_length = int(np.ceil(50 * self.size))
        self.health_bar_height = int(np.ceil(5 * self.size))

        # 이동 경로 생성
        steps = max(int(1000/speed), 1)  # 최소 1은 움직임
        self.path = np.linspace(start, end, steps)
        self.current_step = 0

    def __iter__(self) -> Self:
        """이터러블 객체로 설정"""
        self.current_step = 0
        return self

    def __next__(self) -> tuple[Any, Any]:
        """다음 좌표로 이동"""
        if self.current_step >= len(self.path):
            raise StopIteration
        self.x, self.y = self.path[self.current_step]
        self.current_step += 1
        return self.x, self.y

    def move(self) -> None:
        """다음 좌표로 이동, 체력 조건은 여기서 설정"""
        if self.hp <= 0:
            return
        try:
            next(self)
        except StopIteration:
            pass

    def draw_body(self, frame: cv2.typing.MatLike) -> None:
        """엔티티를 화면에 그리기. 체력 조건은 여기서 설정"""
        if self.hp <= 0:
            return
        # 머리 그리기
        cv2.circle(frame, (int(self.x), int(self.y - self.body_length // 2 -
                   self.head_radius)), self.head_radius, self.body_color, -1)

        # 몸통 그리기
        cv2.line(frame, (int(self.x), int(self.y - self.body_length // 2)),
                 (int(self.x), int(self.y + self.body_length // 2)), self.body_color, self.line_thickness)

        # 팔 그리기
        cv2.line(frame, (int(self.x - self.arm_length // 2), int(self.y)),
                 (int(self.x + self.arm_length // 2), int(self.y)), self.body_color, self.line_thickness)

        # 다리 그리기
        cv2.line(frame, (int(self.x), int(self.y + self.body_length // 2)),
                 (int(self.x - self.leg_length // 2),
                  int(self.y + self.body_length // 2 + self.leg_length)),
                 self.body_color, self.line_thickness)
        cv2.line(frame, (int(self.x), int(self.y + self.body_length // 2)),
                 (int(self.x + self.leg_length // 2),
                  int(self.y + self.body_length // 2 + self.leg_length)),
                 self.body_color, self.line_thickness)

    def draw_hp_bar(self, frame: cv2.typing.MatLike) -> None:
        """체력바 그리기, 체력 조건은 여기서 설정"""
        if self.hp <= 0:
            return
        # 체력바 색상 설정
        hp_bar_color = Color.GREEN.value if self.hp > 0.5 * \
            self.max_hp else Color.YELLOW.value if self.hp > 0.2 * self.max_hp else Color.RED.value

        # 체력바의 y 좌표를 머리 위쪽으로 올리기
        bar_top_y = int(self.y - self.body_length // 2 -
                        self.head_radius - 20)  # 기존보다 10px 위로 올림
        bar_bottom_y = bar_top_y + self.health_bar_height

        # 체력 비율 계산
        hp_ratio = max(self.hp, 0) / self.max_hp if self.max_hp > 0 else 0

        # 머리 위에 체력바 그리기
        cv2.rectangle(frame, (int(self.x - self.health_bar_length // 2), bar_top_y),
                      (int(self.x - self.health_bar_length //
                       2 + self.health_bar_length), bar_bottom_y),
                      (200, 200, 200), -1)  # 연한 회색 배경
        cv2.rectangle(frame, (int(self.x - self.health_bar_length // 2), bar_top_y),
                      (int(self.x - self.health_bar_length // 2 +
                           int(hp_ratio * self.health_bar_length)), bar_bottom_y),
                      hp_bar_color, -1)  # 체력바

    def _attack(self, other: "BasicEntity", min_: int, max_: int) -> None:
        other.hp -= randint(min_, max_)
        if other.hp < 0 and self.hp > 0:  # 살아있어야만 공격가능
            other.hp = 0


class Character(BasicEntity):
    def __init__(self, start: tuple[int, int], hp: int = 200) -> None:
        super().__init__(start, start, Color.WHITE.value, hp=hp)
        self.full_hp = hp
        self.can_attack = False

    def attack(self, enemies: list["Enemy"]) -> None:
        """적 리스트에서 체력 없는 건 밖에서 처리함. 스쿼트 동안에 계속 피해들어가는 건 밖에서 처리함"""
        # 가장 가까운 적 찾기
        if not enemies:
            return
        closest_enemy = min(
            enemies,
            key=lambda enemy: (self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)

        super()._attack(closest_enemy, 20, 60)
        self.can_attack = False  # 스쿼드 안하는 상태가 되면 다시 true로
        if closest_enemy.hp <= 0:
            self.hp += randint(10, 20)  # 죽이면 체력 회복
            if self.hp > self.full_hp:
                self.hp = self.full_hp


class Enemy(BasicEntity):
    def __init__(self, starts: tuple[tuple[int, int], tuple[int, int]], end: tuple[int, int],
                 character: Character, attack_cooltime: float = 5, collision_distance: float = 10) -> None:
        """hp가 클수록 속도 감소, 크기 증가. 색은 랜덤\n
        starts: ((x,y), (x,y))
        """
        start_min, start_max = starts
        start = (randint(start_min[0], start_max[0]),
                 randint(start_min[1], start_max[1]))
        body_color = (randint(50, 200), randint(50, 200), randint(50, 200))
        hp = randint(50, 150)
        speed = 10 / (hp / 100) + 1
        size = hp / 100
        super().__init__(start, end, body_color, speed, hp, size)

        self.character = character
        self.collision_distance = collision_distance
        self.attack_cooltime = CoolTime(attack_cooltime)

    def is_collision(self) -> bool:
        """충돌 여부 확인"""
        other = self.character
        d = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        return d < self.collision_distance

    def move(self) -> None:
        if not self.is_collision():
            super().move()

    def attack(self) -> None:
        if self.is_collision() and self.attack_cooltime.is_ready():
            super()._attack(self.character, 5, 10)
