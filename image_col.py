import os
import shutil
from PIL import Image
import colorama
from colorama import Fore, Style

colorama.init()

def rgb_fg(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def color_for_pixel_ansi(r, g, b):
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    if brightness < 30: return Fore.BLACK
    if brightness > 230: return Fore.WHITE
    if r > g + 40 and r > b + 40: return Fore.RED
    if g > r + 40 and g > b + 40: return Fore.GREEN
    if b > r + 40 and b > g + 40: return Fore.BLUE
    if r > 180 and g > 180 and b < 100: return Fore.YELLOW
    return Fore.LIGHTBLACK_EX

def supports_truecolor():
    cterm = os.environ.get("COLORTERM", "").lower()
    term = os.environ.get("TERM", "").lower()
    return "truecolor" in cterm or "24bit" in cterm or "truecolor" in term

def get_image_ascii(path="diwali.jpg", char="█"):
    """
    Processes the image and returns the ASCII representation as a single string.
    """
    if not os.path.exists(path):
        return f"Error: {path} not found."

    # 1. Load and Resize
    im = Image.open(path).convert("RGB")
    term_width = shutil.get_terminal_size().columns
    new_width = min(term_width - 2, 100)
    
    aspect_ratio = im.height / im.width
    new_height = int(aspect_ratio * new_width * 0.55)
    im = im.resize((new_width, max(1, new_height)), Image.Resampling.LANCZOS)
    
    # 2. Setup
    pixels = list(im.getdata())
    use_true = supports_truecolor()
    output_lines = []

    # 3. Build the rows
    for y in range(im.height):
        row_str = ""
        for x in range(im.width):
            r, g, b = pixels[y * im.width + x]
            
            if use_true:
                row_str += rgb_fg(r, g, b, char)
            else:
                row_str += color_for_pixel_ansi(r, g, b) + char
        
        if not use_true:
            row_str += Style.RESET_ALL
            
        output_lines.append(row_str)

    # 4. Join and Return
    return "\n".join(output_lines)

if __name__ == "__main__":
    # Get user input outside the logic function
    char_choice = input("Enter character (default '█'): ") or "█"
    
    # Call function and store the result
    ascii_result = get_image_ascii("diwali.jpg", char_choice)
    
    # Now you can do whatever you want with the string!
    # For example, print it:
    print(ascii_result)