# https://github.com/Pradnya1208/Squats-angle-detection-using-OpenCV-and-mediapipe_v1
# https://drive.google.com/file/d/1ACjsHBJfy-20Sx7Q1KpTrpscgf8cCXrH/view
import time
import random
import cv2
import mediapipe as mp  # type: ignore
from rich.console import Console
from rich.panel import Panel
from .squat import SquatAnalyzer
from .entity import Character, Enemy
from .cooltime import CoolTime
from .textbox import TextBox, Color
from .make_title import print_title
from .util_func import ask_choice_num

console = Console()

FPS = 30
frame_timer = CoolTime(1 / FPS)

# 제목 출력
print_title(console)


# 목표 점수 정하기
console.print("[bold blink bright_green]목표 점수를 정하세요[/]", end=' ')
goal_score = int(input())

# 난이도
DIFFICULTY = ask_choice_num(
    "[bold magenta]난이도를 정하세요[/]", ("쉬움", "보통", "어려움"), 0) * 0.5 + 1


# 게임 설명 표시
TEXT = ("1 ) [bold bright_green]스쿼트[/]를 하면 적을 공격함. \n"
        "2 ) [bold magenta]적[/]은 랜덤한 위치에서 [bold blue]쿨타임[/]마다 스폰됨. \n"
        "3 ) [bold magenta]적[/]이 스폰될 때마다 [bold blue]적 스폰 쿨타임[/]이 감소함. \n"
        "4 ) [bold magenta]적[/]을 죽이면 [bold red]체력[/]이 10 만큼 회복됨.")
console.print(Panel(TEXT, title="게임 설명", style="bright_white", expand=False))

with console.status("[bold green]Game Loading...", spinner="pong") as status:
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)

FRAME_WIDTH = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
FRAME_HEIGHT = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
console.print("[yellow]카메라 가져오기 완료[/yellow]")

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

mp_drawig = mp.solutions.drawing_utils
line_style = mp_drawig.DrawingSpec(
    color=(220, 220, 220),
    thickness=3)
circle_style = mp_drawig.DrawingSpec(
    color=(166, 114, 31),
    thickness=2,
    circle_radius=3)
cv2.namedWindow("Pose")


# 기본 설정
character = Character((100, FRAME_HEIGHT//2), 100)
enemies: list[Enemy] = []
died_enemies: list[Enemy] = []
start_points_enemy = ((FRAME_WIDTH-200, 0), (FRAME_WIDTH, FRAME_HEIGHT))
end_point_enemy = (character.x, character.y)
enemy_cooltime = CoolTime(10 / DIFFICULTY)

game_over: bool = False
squat_count: int = 0

game_start_time = time.time()
while cv2.getWindowProperty("Pose", cv2.WND_PROP_VISIBLE):
    ret, frame = cam.read()
    if not ret:
        break
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # SquatAnalyzer 인스턴스 생성
        analyzer = SquatAnalyzer(landmarks, mp_pose)
        # 각도 등 프레임에 표시
        analyzer.draw_pose_info(frame)
        # 스쿼트 여부 확인 (필요시 활용)
        is_squat = analyzer.is_squat()

        # 테스트용으로 스쿼트를 하지 않을 때도 스페이스바를 누르면 스쿼트로 인식되게 함
        if not is_squat and cv2.waitKey(1) & 0xFF == ord(' '):
            is_squat = True  # pylint: disable=invalid-name

        # 적 엔티티 만들기: 렌덤한 쿨타임마다 생성되고 데큐에 넣어서 생성, 관리. hp<=0이면 제거
        if enemy_cooltime.is_ready():
            enemy_cooltime.COOLDOWN -= 0.5  # 쿨타임 감소: 0.5초씩
            if enemy_cooltime.COOLDOWN <= 1:
                enemy_cooltime.COOLDOWN = 1
            # 적 엔티티 생성
            enemy = Enemy(start_points_enemy, end_point_enemy, character,
                          attack_cooltime=5 / DIFFICULTY, collision_distance=50)
            enemies.append(enemy)
        new_died_enemies = [
            enemy for enemy in enemies if enemy.hp <= 0]  # 이번 프레임에 죽은 적
        died_enemies.extend(new_died_enemies)  # 전체 죽은 적 리스트에 추가
        enemies = [enemy for enemy in enemies if enemy.hp > 0]  # 살아있는 적만 남김

        for enemy in enemies:
            enemy.move()
            enemy.draw_body(frame)
            enemy.draw_hp_bar(frame)
            enemy.attack()

        # 캐릭터 그리기
        character.draw_body(frame)
        character.draw_hp_bar(frame)

        # 스쿼드 여부 감지 후 에너미 공격
        if is_squat and character.can_attack:
            character.attack(enemies)
            squat_count += 1
        if not is_squat:
            character.can_attack = True

        # 랜드마크 그리기
        mp_drawig.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            line_style,
            circle_style
        )

        # 각종 정보 창 표시
        # 스쿼트 여부 좌상단에 표시
        squat_textbox = TextBox(
            FRAME_WIDTH, FRAME_HEIGHT, anchor="lefttop", margin=0, padding=20,
            font_scale=0.5, thickness=1, bg_color=Color.DARK_GRAY.value)
        if is_squat:
            squat_textbox.draw(frame, ["Squat", f"Count: {squat_count}"], [
                               Color.GREEN.value, Color.MAGENTA.value])
        else:
            squat_textbox.draw(frame, ["not Squat", f"Count: {squat_count}"], [
                               Color.RED.value, Color.MAGENTA.value])

        # 화면 좌하단에 캐릭터 체력 표시
        character_textbox = TextBox(
            FRAME_WIDTH, FRAME_HEIGHT, anchor="leftbottom", margin=0, padding=20,
            font_scale=0.5, thickness=1, bg_color=Color.LIGHT_GRAY.value)
        character_textbox.draw(frame, [f"Character HP: {character.hp}"],
                               [Color.RED.value])

        # 적 스폰 쿨타임 오른쪽 아래에 표시
        enemy_cooltime_textbox = TextBox(
            FRAME_WIDTH, FRAME_HEIGHT, anchor="rightbottom", margin=0, padding=20,
            font_scale=0.5, thickness=1, bg_color=Color.LIGHT_GRAY.value)
        enemy_cooltime_textbox.draw(frame, [f"Current Spawn Rate: {enemy_cooltime.COOLDOWN}s",
                                            f"New Enemy Spawns In {enemy_cooltime.current_left_cooldown:.2f}s"],
                                    [Color.CYAN.value, Color.LIGHT_BLUE.value])

        # 화면 오른쪽 상단에 적 수, 생존 시간 표시
        elapsed_time = time.time() - game_start_time
        score = len(died_enemies) * 10 + int(elapsed_time) * 2
        count_textbox = TextBox(
            FRAME_WIDTH, FRAME_HEIGHT, anchor="righttop", margin=0, padding=20,
            font_scale=0.5, thickness=1, bg_color=Color.DARK_GRAY.value)
        count_textbox.draw(frame, [f"Live Enemies: {len(enemies)}",
                                   f"Dead Enemies: {len(died_enemies)}",
                                   f"Survival Time: {int(elapsed_time)}s",
                                   f"Score: {score}"],
                           [Color.MAGENTA.value, Color.LIGHT_BLUE.value, Color.GREEN.value, Color.CYAN.value])

    # 종료 조건: q키 또는 ESC키
    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == 27:
        break

    # FPS 조절
    if frame_timer.is_ready():
        cv2.imshow("Pose", frame)

    if character.hp <= 0:
        game_over = True  # pylint: disable=invalid-name
        break
    if score >= goal_score:
        break

cam.release()
cv2.destroyAllWindows()

if game_over:
    style: str = 'red'
    title: str = 'Game Over'
else:
    style = 'green'  # pylint: disable=invalid-name
    title = 'Game Finished'  # pylint: disable=invalid-name
title = f"[{style}]{title}"  # pylint: disable=invalid-name

console.print(Panel(
    (f"[bold magenta]Live Enemies[/]: {len(enemies)}\n"
     f"[bold blue]Dead Enemies[/]: {len(died_enemies)}\n"
     f"[bold green]Survival Time[/]: {int(elapsed_time)} s\n"
     f"[bold cyan]Score[/]: {score}"),
    title=title, style=style, expand=True))

time.sleep(3)
