from PIL import Image # type: ignore
import shutil

im = (Image.open("assets/image.png")).convert("L")
pixels = list(im.getdata())

columns = shutil.get_terminal_size().columns
new_width = min(columns, 120)
aspect_ratio = im.height / im.width
new_height = int(aspect_ratio * new_width * 0.55)
im = im.resize((new_width, new_height))

pixels = list(im.getdata())
width, height = im.size
pixels = [pixels[i * new_width:(i + 1) * new_width] for i in range(new_height)]


gradient = "█▓▓▒▒░░   "

for row in pixels:
    for value in row:
        idx = int(value / 325 * (len(gradient) - 1))
        print(gradient[idx], end='')

    print()