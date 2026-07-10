#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import urllib.request
import io
from PIL import Image
import numpy as np
import colorama
from colorama import Fore, Style

colorama.init()

# --- Config and gradients ---
DEFAULT_WIDTH = 80
CHAR_ASPECT = 0.55  # Character height/width aspect ratio correction

GRADIENTS = {
    "1": " .',:;clxokXdO0KN",
    "2": "█▓▓▒▒░░ ",
    "3": " `´¨·¸˜':~‹°—÷¡|/+}?1u@VY©4ÐŽÂMÆ",
    "4": " .-+o$#8",
    "standard": " .:-=+*#%@",
    "blocks": " ░▒▓█"
}

def get_gradient_string(choice, invert=False):
    grad = GRADIENTS.get(choice, choice)
    if invert:
        return grad[::-1]
    return grad

def rgb_fg(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def rgb_bg(r, g, b, text):
    return f"\033[48;2;{r};{g};{b}m{text}\033[0m"

def color_for_pixel_ansi(r, g, b):
    # Map RGB to 16-color ANSI code
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    if brightness < 30: return Fore.BLACK
    if brightness > 220: return Fore.WHITE
    if r > g + 40 and r > b + 40: return Fore.RED
    if g > r + 40 and g > b + 40: return Fore.GREEN
    if b > r + 40 and b > g + 40: return Fore.BLUE
    if r > 180 and g > 180 and b < 100: return Fore.YELLOW
    if r > 150 and b > 150 and g < 100: return Fore.MAGENTA
    if g > 150 and b > 150 and r < 100: return Fore.CYAN
    return Fore.LIGHTBLACK_EX

def supports_truecolor():
    cterm = os.environ.get("COLORTERM", "").lower()
    term = os.environ.get("TERM", "").lower()
    return "truecolor" in cterm or "24bit" in cterm or "truecolor" in term

def load_image(path_or_url):
    """Loads image from local path or URL."""
    if path_or_url.startswith(("http://", "https://")):
        print(f"Downloading image from URL: {path_or_url}...", file=sys.stderr)
        req = urllib.request.Request(
            path_or_url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req) as response:
            img_data = response.read()
        return Image.open(io.BytesIO(img_data))
    else:
        if not os.path.exists(path_or_url):
            raise FileNotFoundError(f"Local file not found: {path_or_url}")
        return Image.open(path_or_url)

def image_to_ascii(im, width=None, mode="color", char="█", gradient_key="1", use_bg=False, invert=False):
    """
    Processes the image and returns:
      1. Display string (with ANSI color codes for terminal)
      2. Raw text string (no ANSI codes, standard characters)
      3. HTML formatted string (with colored inline styles)
    """
    # 1. Convert modes
    if mode == "bw":
        im_gray = im.convert("L")
        im_rgb = im.convert("RGB") # Keep RGB for width calculations / size matching
    else:
        im_rgb = im.convert("RGB")
        im_gray = im_rgb.convert("L")

    # 2. Handle scale & width
    term_width, _ = shutil.get_terminal_size((DEFAULT_WIDTH, 24))
    if width is None:
        # Auto-size to terminal width
        new_width = min(term_width - 2, 100)
    else:
        new_width = width

    aspect_ratio = im.height / im.width
    new_height = int(aspect_ratio * new_width * CHAR_ASPECT)
    new_height = max(1, new_height)

    # Resize
    im_rgb = im_rgb.resize((new_width, new_height), Image.Resampling.LANCZOS)
    im_gray = im_gray.resize((new_width, new_height), Image.Resampling.LANCZOS)

    pixels_rgb = np.array(im_rgb)
    pixels_gray = np.array(im_gray)

    gradient = get_gradient_string(gradient_key, invert)
    num_grad_chars = len(gradient)

    display_lines = []
    plain_lines = []
    html_lines = []

    use_true = supports_truecolor()

    # Pre-render HTML header style
    html_lines.append('<pre style="font-family: monospace; font-size: 8px; line-height: 1; letter-spacing: 0; background: #000; color: #fff; padding: 10px; border-radius: 4px; overflow-x: auto;">')

    for y in range(new_height):
        display_row = []
        plain_row = []
        html_row = []

        for x in range(new_width):
            r, g, b = pixels_rgb[y, x]
            gray_val = pixels_gray[y, x]

            # Determine the base character
            if mode == "bw":
                grad_idx = int((gray_val / 256.0) * num_grad_chars)
                grad_idx = min(grad_idx, num_grad_chars - 1)
                c = gradient[grad_idx]
            else:
                c = char

            plain_row.append(c)

            # Build colorized representations
            if mode == "bw":
                display_row.append(c)
                # Escaping HTML characters just in case
                html_c = c.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                html_row.append(html_c)
            else:
                # Color modes
                if use_bg:
                    # ANSI Terminal Background color
                    if use_true:
                        display_row.append(rgb_bg(r, g, b, " "))
                    else:
                        # Fallback for non-truecolor terminals
                        display_row.append(color_for_pixel_ansi(r, g, b).replace("38;2;", "48;2;").replace("38;5;", "48;5;") + " " + Style.RESET_ALL)
                    
                    # HTML representation
                    html_row.append(f'<span style="background-color: rgb({r},{g},{b});">&nbsp;</span>')
                else:
                    # ANSI Terminal Foreground color
                    if use_true:
                        display_row.append(rgb_fg(r, g, b, c))
                    else:
                        display_row.append(color_for_pixel_ansi(r, g, b) + c + Style.RESET_ALL)
                    
                    # HTML representation
                    html_c = c.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                    html_row.append(f'<span style="color: rgb({r},{g},{b});">{html_c}</span>')

        display_lines.append("".join(display_row))
        plain_lines.append("".join(plain_row))
        html_lines.append("".join(html_row))

    html_lines.append('</pre>')

    return (
        "\n".join(display_lines),
        "\n".join(plain_lines),
        "\n".join(html_lines)
    )

def main():
    parser = argparse.ArgumentParser(
        description="ASCII Art Image Generator - Accepts local images or URLs!"
    )
    parser.add_argument(
        "image_source",
        help="Path to local image file OR image URL (http/https)"
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=None,
        help="Width of ASCII art in characters (default: auto terminal width)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["color", "bw"],
        default="color",
        help="Output mode: color (ASCII with colors) or bw (grayscale gradient)"
    )
    parser.add_argument(
        "--char", "-c",
        default="█",
        help="Character to use for rendering in color mode (default: █)"
    )
    parser.add_argument(
        "--gradient", "-g",
        default="1",
        help="Gradient set index (1-4, 'blocks', 'standard') or custom string for BW mode (default: 1)"
    )
    parser.add_argument(
        "--bg",
        action="store_true",
        help="Color the background cells instead of characters (color block mode)"
    )
    parser.add_argument(
        "--invert", "-i",
        action="store_true",
        help="Invert the grayscale gradient for BW mode"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save output to a file. Saves plain text if file ends in .txt, or HTML if ends in .html"
    )

    args = parser.parse_args()

    try:
        im = load_image(args.image_source)
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)

    display_str, plain_str, html_str = image_to_ascii(
        im,
        width=args.width,
        mode=args.mode,
        char=args.char,
        gradient_key=args.gradient,
        use_bg=args.bg,
        invert=args.invert
    )

    # Output to screen
    print(display_str)

    # Save to file if specified
    if args.output:
        try:
            if args.output.endswith(".html"):
                with open(args.output, "w", encoding="utf-8") as f:
                    # Make it a complete HTML page
                    f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>ASCII Art - {os.path.basename(args.image_source)}</title>
    <style>
        body {{
            background: #121212;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            font-family: sans-serif;
        }}
        .container {{
            max-width: 95%;
            margin: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_str}
    </div>
</body>
</html>""")
                print(f"\n[Saved HTML ASCII art to {args.output}]", file=sys.stderr)
            else:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(plain_str)
                print(f"\n[Saved plain text ASCII art to {args.output}]", file=sys.stderr)
        except Exception as e:
            print(f"Error saving to file: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
