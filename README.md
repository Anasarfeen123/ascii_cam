# 🎥 ASCII Camera Feed

A terminal-based camera display using ASCII characters — supports both black & white gradient mode and color mode using custom characters.

---

## 🚀 Features

- Live webcam feed in ASCII
- Black & white mode with 4 gradient options
- Color mode with custom character rendering
- Frame rate control (`+` / `-`)
- Optionally toggle original webcam preview (`v`)
- Smooth terminal clearing and rendering

---

## 🗂️ Files Overview

| File           | Description |
|----------------|-------------|
| `ascii_cam.py` | 🔴 **Main script**: Live webcam ASCII renderer with real-time color & grayscale modes |
| `test_bw.py`   | 🖼️ Static image to **B/W ASCII art** using grayscale gradients |
| `test_col.py`  | 🎨 Static image to **colored ASCII art** using RGB to ANSI Fore color mapping |

---

## 🔧 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

2. **Run Live Camera ASCII**

```
python ascii_cam.py
```

You’ll be prompted to select:

Color or Black & White mode

Custom character (for color)

Gradient set (for B/W)

Use these keys during runtime:
Key	Action
q	Quit
/+ / -	Adjust delay (speed)
v	Toggle webcam preview

3. **Convert Static Image to ASCII**

`python test_bw.py`
`python test_col.py`

📌 **Note:** Currently, test_bw.py and test_col.py use a sample image hardcoded in the script. You can replace the path manually for now. Support for custom paths will be added in the next version.


