from PIL import Image
import shutil
import os

def get_image_to_ascii_bw(path="diwali.jpg"):
    """
    Converts an image to a grayscale ASCII string and returns it.
    """
    if not os.path.exists(path):
        return f"Error: {path} not found."

    try:
        # 1. Open and convert to Grayscale
        im = Image.open(path).convert("L")
    except Exception as e:
        return f"Error: Could not process image. {e}"

    # 2. Dimensions
    columns = shutil.get_terminal_size().columns
    new_width = min(columns, 120)
    
    aspect_ratio = im.height / im.width
    new_height = int(aspect_ratio * new_width * 0.55)
    
    im = im.resize((new_width, max(1, new_height)), Image.Resampling.LANCZOS)

    # 3. Process Pixels
    pixels = list(im.getdata())
    gradient = "█▓▓▒▒░░   "
    num_chars = len(gradient)

    # 4. Build String
    output_rows = []
    for y in range(im.height):
        row_chars = []
        for x in range(im.width):
            pixel_val = pixels[y * im.width + x]
            # Map 0-255 to gradient index
            idx = int(pixel_val / 256 * num_chars)
            row_chars.append(gradient[idx])
        
        output_rows.append("".join(row_chars))

    # Return the final multi-line string
    return "\n".join(output_rows)

if __name__ == "__main__":
    # Example usage:
    ascii_art = get_image_to_ascii_bw("diwali.jpg")
    
    # Now you can print it, save it, or send it elsewhere
    print(ascii_art)