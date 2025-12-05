from PIL import Image  # type: ignore
import colorama
from colorama import Fore, Style
import shutil
import os

colorama.init()

def rgb_fg(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def color_for_pixel_ansi(r, g, b):
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    if brightness < 30:
        return Fore.BLACK
    elif brightness > 240 and abs(r - g) < 20 and abs(g - b) < 20:
        return Fore.WHITE
    elif r > 180 and g > 180 and b < 100:
        return Fore.YELLOW
    elif r > 180 and b > 180 and g < 150:
        return Fore.MAGENTA
    elif g > 180 and b > 180 and r < 150:
        return Fore.CYAN
    elif r > g + 40 and r > b + 40:
        return Fore.RED
    elif b > r + 40 and b > g + 40:
        return Fore.BLUE
    elif g > r + 40 and g > b + 40:
        return Fore.GREEN
    else:
        return Fore.LIGHTBLACK_EX

def supports_truecolor():
    colorterm = os.environ.get("COLORTERM", "").lower()
    term = os.environ.get("TERM", "").lower()
    if "truecolor" in colorterm or "24bit" in colorterm:
        return True
    if "direct" in os.environ.get("KONSOLE_PROFILE_NAME", "").lower():
        return True
    return "truecolor" in term or False

def main(path="diwali.jpg"):
    im = Image.open(path).convert("RGB")

    term_width = shutil.get_terminal_size((120, 25)).columns
    max_width = min(160, term_width - 4)
    new_width = max(40, min(100, max_width))

    aspect_ratio = im.height / im.width
    char_aspect = 0.55
    new_height = int(aspect_ratio * new_width * char_aspect) or 1

    im = im.resize((new_width, new_height))

    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

    # Ask character once (keeps behaviour you had)
    inp = input("Enter a character (Press enter for default '█'): ")
    val = inp[0] if inp else "█"

    use_true = supports_truecolor()

    for row in pixels:
        if use_true:
            line = "".join(rgb_fg(r, g, b, val) for (r, g, b) in row)
            print(line)
        else:
            line_builder = []
            for r, g, b in row:
                line_builder.append(color_for_pixel_ansi(r, g, b) + val)
            print("".join(line_builder) + Style.RESET_ALL)

if __name__ == "__main__":
    main("diwali.jpg")
