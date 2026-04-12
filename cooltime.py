import time


class CoolTime:
    def __init__(self, cooldown: float) -> None:
        self.COOLDOWN = cooldown  # pylint: disable=invalid-name
        self.current_left_cooldown = cooldown
        self.last_used_time = time.time()

    def is_ready(self) -> bool:
        """쿨타임이 끝났는지 확인 및 쿨타임 업데이트."""
        current_time = time.time()
        self.current_left_cooldown = self.COOLDOWN - \
            (current_time - self.last_used_time)
        if self.current_left_cooldown <= 0:
            # 현 시간 기록, 남은 쿨타임 초기화
            self.last_used_time = time.time()
            self.current_left_cooldown = self.COOLDOWN
            return True
        else:
            return False


if __name__ == '__main__':
    t = CoolTime(5)
    while True:
        print(f"남은 쿨: {t.current_left_cooldown:.2f}", end=" ")
        if t.is_ready():
            print("쿨타임 끝")
        else:
            print("쿨타임 중")
        time.sleep(0.2)
