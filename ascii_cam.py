#!/usr/bin/env python3
# ascii_cam_headless_friendly.py
from cv2 import VideoCapture, imshow, destroyAllWindows, waitKey, cvtColor, COLOR_BGR2GRAY, COLOR_BGR2RGB, resize, INTER_AREA
import cv2, time, os, sys
import numpy as np
from colorama import Style
import shutil

# --- config defaults ---
DEFAULT_WIDTH = 80            # width in characters
CHAR_ASPECT = 0.55            # tweak if chars look stretched
FRAME_RATE = 0.08             # seconds between frames (smaller -> faster)
USE_TRUECOLOR_ENV = True      # attempt truecolor by env check

# --- helpers ---
def supports_truecolor():
    colorterm = os.environ.get("COLORTERM", "").lower()
    term = os.environ.get("TERM", "").lower()
    return ("truecolor" in colorterm) or ("24bit" in colorterm) or ("truecolor" in term)

def rgb_fg_escape(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

def rgb_bg_escape(r, g, b, text):
    return f"\033[48;2;{r};{g};{b}m{text}\033[0m"

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_gradient_string(choice):
    if choice == "1":
        return " .',:;clxokXdO0KN"
    if choice == "2":
        return "█▓▓▒▒░░ "
    if choice == "3":
        return " `´¨·¸˜':~‹°—÷¡|/+}?1u@VY©4ÐŽÂMÆ"
    if choice == "4":
        return " .-+o$#8"
    return " .',:;clxokXdO0KN"

def pixel_to_ansi_name(r,g,b):
    brightness = 0.299*r + 0.587*g + 0.114*b
    if brightness < 40:
        return "\033[30m"   # black
    if brightness > 230 and abs(r-g)<30 and abs(g-b)<30:
        return "\033[97m"   # bright white
    if r > g + 40 and r > b + 40: return "\033[31m"
    if g > r + 40 and g > b + 40: return "\033[32m"
    if b > r + 40 and b > g + 40: return "\033[34m"
    if r > 180 and g > 180 and b < 120: return "\033[33m"
    if r > 180 and b > 180 and g < 150: return "\033[35m"
    if g > 180 and b > 180 and r < 150: return "\033[36m"
    return "\033[90m"

# ---------- GUI detection + nonblocking stdin helpers ----------
import select, tty, termios

def detect_cv_gui():
    """Return True if OpenCV highgui appears usable (won't crash)."""
    try:
        tmp = np.zeros((10, 10, 3), dtype=np.uint8)
        cv2.namedWindow(".__cv_test__", cv2.WINDOW_NORMAL)
        cv2.imshow(".__cv_test__", tmp)
        cv2.waitKey(1)
        cv2.destroyWindow(".__cv_test__")
        return True
    except Exception:
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        return False

GUI_AVAILABLE = detect_cv_gui()

_old_term_settings = None
def enable_raw_mode():
    global _old_term_settings
    if sys.stdin and sys.stdin.isatty():
        _old_term_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

def disable_raw_mode():
    global _old_term_settings
    if _old_term_settings and sys.stdin and sys.stdin.isatty():
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _old_term_settings)
        _old_term_settings = None

def stdin_key_pressed():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return ord(sys.stdin.read(1))
    return None
# -----------------------------------------------------------------

# --- main logic (unchanged algorithmic parts) ---
def frame_to_ascii_cv(frame, new_size, gradient, mode_color, char="█", use_truecolor=True, use_bg=False):
    w_chars, h_chars = new_size
    small = resize(frame, (w_chars, h_chars), interpolation=INTER_AREA)

    if mode_color == "bw":
        gray = cvtColor(small, COLOR_BGR2GRAY)
        max_idx = len(gradient) - 1
        rows = []
        for row in gray:
            idxs = (row.astype(np.float32) / 255.0 * max_idx).astype(int)
            rows.append("".join(gradient[i] for i in idxs))
        return "\n".join(rows)

    else:
        rgb = cvtColor(small, COLOR_BGR2RGB)
        rows = []
        if use_truecolor:
            if use_bg:
                for row in rgb:
                    row_str = "".join(rgb_bg_escape(int(r),int(g),int(b), " ") for (r,g,b) in row)
                    rows.append(row_str + Style.RESET_ALL)
            else:
                for row in rgb:
                    row_str = "".join(rgb_fg_escape(int(r),int(g),int(b), char) for (r,g,b) in row)
                    rows.append(row_str + Style.RESET_ALL)
        else:
            if use_bg:
                for row in rgb:
                    row_str = "".join(pixel_to_ansi_name(int(r),int(g),int(b)) + " " for (r,g,b) in row)
                    rows.append(row_str + Style.RESET_ALL)
            else:
                for row in rgb:
                    row_str = "".join(pixel_to_ansi_name(int(r),int(g),int(b)) + char for (r,g,b) in row)
                    rows.append(row_str + Style.RESET_ALL)
        return "\n".join(rows)

def main():
    cam = VideoCapture(0)
    if not cam.isOpened():
        print("Can't open camera.")
        return

    global FRAME_RATE
    FRAME_RATE = FRAME_RATE

    clear_terminal()
    print("WELCOME — ASCII CAMERA\nControls: q=quit | +=slower | -=faster | v=toggle original camera view | b=toggle background mode\n")
    col_choice = input("Color mode? [1] Color  [2] BW  (default 1): ").strip() or "1"
    mode_color = "clr" if col_choice == "1" else "bw"

    gradient = get_gradient_string(input("Choose gradient 1-4 (only used for BW). default 1: ").strip() or "1")
    char = "█"
    if mode_color == "clr":
        char = input("Character to render (default '█'): ").strip() or "█"

    term_width = shutil.get_terminal_size((120, 25)).columns
    max_width = max(20, min(160, term_width - 4))
    w_chars = min(DEFAULT_WIDTH, max_width)

    ret, frame_sample = cam.read()
    if not ret:
        print("Camera read failed.")
        cam.release()
        return
    frame_h, frame_w = frame_sample.shape[:2]
    aspect = frame_h / frame_w
    h_chars = max(1, int(aspect * w_chars * CHAR_ASPECT))

    use_true = supports_truecolor() if USE_TRUECOLOR_ENV else False
    use_bg = False
    show_original = GUI_AVAILABLE  # only show preview if GUI works

    # enable terminal raw mode for stdin key reads if GUI is unavailable or to support keys alongside GUI
    enable_raw_mode()

    try:
        while True:
            t0 = time.time()
            ret, frame = cam.read()
            if not ret:
                break

            new_size = (w_chars, h_chars)
            ascii_frame = frame_to_ascii_cv(frame, new_size, gradient, mode_color, char, use_true, use_bg)

            clear_terminal()
            print(ascii_frame)

            key = None
            if GUI_AVAILABLE and show_original:
                # try to show preview window; catch exceptions and fall back if necessary
                try:
                    imshow("Camera", frame)
                    key = waitKey(1) & 0xFF
                except Exception:
                    # GUI broke mid-run -> disable it
                    show_original = False
                    try:
                        destroyAllWindows()
                    except Exception:
                        pass
                    key = stdin_key_pressed()
            else:
                # no GUI: read keys from stdin
                key = stdin_key_pressed()

            if key == ord('q'):
                break
            elif key == ord('+'):
                FRAME_RATE = min(1.0, FRAME_RATE + 0.03)
            elif key == ord('-'):
                FRAME_RATE = max(0.01, FRAME_RATE - 0.03)
            elif key == ord('v'):
                if GUI_AVAILABLE:
                    show_original = not show_original
                    if not show_original:
                        try:
                            destroyAllWindows()
                        except Exception:
                            pass
            elif key == ord('b'):
                use_bg = not use_bg

            elapsed = time.time() - t0
            to_sleep = FRAME_RATE - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)

    finally:
        disable_raw_mode()
        cam.release()
        try:
            destroyAllWindows()
        except Exception:
            pass
        print(Style.RESET_ALL)

if __name__ == "__main__":
    main()
