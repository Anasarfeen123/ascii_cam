from PIL import Image # type: ignore
import colorama
from colorama import Fore, Back, Style


im = Image.open(r"pill/assets/images.jpeg")

new_width = 100
aspect_ratio = im.height / im.width
new_height = int(aspect_ratio * new_width * 0.55)
im = im.resize((new_width, new_height))

pixels = list(im.getdata())
width, height = im.size

pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

inp = input("Enter a character (Press enter for default): ")
if inp=="" or inp[0].strip() == "":
    val = "█"
else: val = inp[0]

for row in pixels:
    for value in row:
        r,g,b = value
        brightness = 0.299*r + 0.587*g + 0.114*b
        if brightness<30:
            print(Fore.BLACK+val,end="")
        elif brightness > 240 and abs(r - g) < 20 and abs(g - b) < 20:
            print(Fore.WHITE+val,end="")
        elif r > 180 and g > 180 and b < 100:
            print(Fore.YELLOW+val,end="")
        elif r > 180 and b > 180 and g < 150:
            print(Fore.MAGENTA+val,end="")
        elif g > 180 and b > 180 and r < 150:
            print(Fore.CYAN+val,end="")
        elif r > g + 40 and r > b + 40:
            print(Fore.RED+val,end="")
        elif b > r + 40 and b > g + 40:
            print(Fore.BLUE+val,end="")
        elif g > r + 40 and g > b + 40:
            print(Fore.GREEN+val,end="")
        else:
            print(Fore.LIGHTBLACK_EX+val, end="")
    print(Style.RESET_ALL)
            
        
             
    #     if value[0]>200:
    #         if value[1]>200:
    #             if value[2]>200:
    #             else:
    #         else:
    #             if value[2]>200:
    #             else:
    #     else:
    #         if value[1]>200:
    #             if value[2]>200:
    #                 print(Fore.CYAN+"█",end="")
    #             else:
    #                 print(Fore.GREEN+"█",end="")
    #         elif value[2]>200:
    #             print(Fore.BLUE+"█",end="")
    #         else:
    #             print(Fore.BLACK+"█",end="")




# with open("ascii_output.txt", "w") as f:
#     for row in pixels:
#         for value in row:
#             idx = int(value / 255 * (len(gradient) - 1))
#             f.write(gradient[idx])
#         f.write('\n')
