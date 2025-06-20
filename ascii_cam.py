# ASCII Camera Feed
from PIL import Image # type: ignore
from cv2 import COLOR_BGR2RGB, VideoCapture, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, imshow
import cv2, time, os
from colorama import Fore, Style

cam = VideoCapture(0)
frame_width = int(cam.get(CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(CAP_PROP_FRAME_HEIGHT))
frame_rate = 0.1

def get_rcb(value):
    r, g, b = value
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    if brightness < 45:
        return Fore.BLACK
    elif brightness > 200 and abs(r - g) < 25 and abs(g - b) < 25:
        return Fore.WHITE
    elif (
        50 < r < 130 and 
        20 < g < 120 and 
        20 < b < 120):
        return Fore.YELLOW
    elif r > 180 and b > 180 and g < 140:
        return Fore.MAGENTA
    elif g > 180 and b > 180 and r < 140:
        return Fore.CYAN
    elif r > g + 40 and r > b + 40:
        return Fore.RED
    elif g > r + 40 and g > b + 40:
        return Fore.GREEN
    elif b > r + 40 and b > g + 40:
        return Fore.BLUE
    else:
        return Fore.LIGHTBLACK_EX

def resize_frame(frame_height=frame_height, new_width=80):
    aspect_ratio = frame_height / frame_width
    new_height = int(aspect_ratio * new_width * 0.55)
    return [new_width, new_height]

def get_gradient(inp=1):
    inp = str(inp)
    if inp == "1":
        gradient = ' .\',:;clxokXdO0KN'
    elif inp == "2":
        gradient = "█▓▓▒▒░░ "
    elif inp == "3":
        gradient = " `´¨·¸˜':~‹°—÷¡|/+}?1u@VY©4ÐŽÂMÆ"
    elif inp == "4":
        gradient = " .-+o$#8"
    else:
        gradient = ' .\',:;clxokXdO0KN'
    return gradient

new_size = tuple(resize_frame())

def frame_to_ascii(frame, gradient, colr, val="█"):
    im = Image.fromarray(frame)
    im = im.resize(new_size)
    pixels = list(im.getdata())
    width, height = im.size
    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
    
    if colr == "bw":
        for row in pixels:
            for value in row:
                idx = int(value / 255 * (len(gradient) - 1))
                print(gradient[idx], end='')
            print()
    elif colr == "clr":
        for row in pixels:
            for value in row:
                print(get_rcb(value) + val, end="")
            print(Style.RESET_ALL)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    x = True
    print('''
 WELCOME
 Controls:
 [q] Quit
 [+] Increase delay (slower)
 [-] Decrease delay (faster)
 [v] Toggle original camera view
''')
    
    col = input('''
 Choose color:
 1) Color
 2) Black and White
 Enter option [1-2]: ''')

    if col == "1":
        col = "clr"
    else:
        col = "bw"
    if col == "bw":
        g = input('''
        Choose gradient:
        1) ' .\',:;clxokXdO0KN'
        2) "█▓▓▒▒░░ "
        3) " `´¨·¸˜':~‹°—÷¡|/+}?1u@VY©4ÐŽÂMÆ"
        4) " .-+o$#8"
        Enter option [1-4]: ''')
        grad = get_gradient(g)
    
    elif col == "clr":
        val = input("Enter character to render (default '█'): ").strip() or "█"
        grad = ""
    
    while True:
        ret, frame = cam.read()
        if ret:
            clear_terminal()
            if col == "bw":
                bw_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_to_ascii(bw_frame, grad, col, 0)
            else:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_to_ascii(rgb_frame, grad, col, val)
            
            time.sleep(frame_rate)
            
            if x:
                imshow('Camera', frame)
            
            r = cv2.waitKey(1)
            if r == ord('q'):
                break
            elif r == ord('+') and frame_rate < 1.0:
                frame_rate += 0.03
            elif r == ord('-') and frame_rate >= 0.04:
                frame_rate -= 0.03
            elif r == ord('v'):
                x = not x
                if not x:
                    cv2.destroyAllWindows()
    
    cam.release()
    cv2.destroyAllWindows()