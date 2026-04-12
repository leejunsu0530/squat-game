from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.box import DOUBLE
from rich.live import Live
import pyfiglet  # type: ignore
import time
import random


def interpolate_color(color1, color2, factor: float) -> str:
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip("#")
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    interpolated = tuple(int(a + (b - a) * factor) for a, b in zip(rgb1, rgb2))
    return rgb_to_hex(interpolated)


def generate_glitched_text(text: str, gradient: list[str], factor: float) -> Text:
    figlet = pyfiglet.Figlet(font="slant")
    output_lines = figlet.renderText(text).splitlines()

    max_len = max(len(line) for line in output_lines)
    output_lines = [line.ljust(max_len) for line in output_lines]
    num_columns = max_len

    styled_lines = []
    glitch_chars = ["#", "%", "$", "!", "@", "&", "*"]

    glitch_strength = max(0, min(1.0, (0.5 - factor) / 0.5)) * 0.5

    for row in output_lines:
        styled_line = Text()
        for i, char in enumerate(row):
            base_color = gradient[i * len(gradient) // num_columns]
            start_color = "#202020"
            color = interpolate_color(start_color, base_color, factor)

            if char != " " and random.random() < glitch_strength:
                char = random.choice(glitch_chars)

            if char != " " and random.random() < glitch_strength * 0.6:
                char = (" " if random.choice(
                    [True, False]) else "") + char + (" " if random.choice([True, False]) else "")

            styled_line.append(char, style=f"bold {color}")
        styled_lines.append(styled_line)

    combined = Text()
    for line in styled_lines:
        combined.append(line)
        combined.append("\n")
    return combined


def animate_title_with_glitch(console: Console, text: str):
    colors = ["#FF6C00", "#FFA200", "#FFD700", "#FFF380", "#FFFFFF"]
    steps = 60
    delay = 0.05

    def render(factor: float):
        styled = generate_glitched_text(text, colors, factor)
        panel = Panel(
            Align.center(styled),
            border_style="white",
            padding=(0, 4),
            box=DOUBLE
        )
        return panel

    with Live(render(0), console=console, refresh_per_second=60, transient=True) as live:
        for i in range(steps):
            factor = i / steps
            live.update(render(factor))
            time.sleep(delay)

    # Live 종료 후 바로 고정된 최종 텍스트 출력 (깜빡임 없음)
    final_panel = render(1.0)
    console.print(final_panel)
    time.sleep(2.0)


def print_title(console):
    animate_title_with_glitch(console, "Ring  Fit\n   adventure")


if __name__ == "__main__":
    import os
    con = Console()
    print_title(con)
    os.system("pause")
