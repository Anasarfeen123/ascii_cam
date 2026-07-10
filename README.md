# 🎥 ASCII Camera Feed

A terminal-based camera display using ASCII characters — supports both black & white gradient mode and color mode using custom characters.

---

## 📸 Demo

### Black & White ASCII Mode
![ASCII Black & White Demo](ascii_bw_demo.png)

### Color ASCII Mode
![ASCII Color Demo](ascii_clr_demo.jpeg)

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

| File / Folder | Description |
|---|---|
| `ascii_cam.py` | 🔴 **Live webcam feed**: Main webcam ASCII renderer with real-time color & grayscale modes |
| `ascii_image.py` | 🖼️ **Advanced Image CLI**: Convert static images (local or URLs) with full CLI args, HTML/TXT exports |
| `image_bw.py` | 🖼️ Static image to **B/W ASCII art** using grayscale gradients (legacy) |
| `image_col.py` | 🎨 Static image to **colored ASCII art** using RGB to ANSI Fore color mapping (legacy) |
| `web/` | 🌐 **Web Studio**: A stunning glassmorphic web application for webcam, upload, and URL ASCII rendering |

---

## 🔧 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Live Camera ASCII (Terminal)
```bash
python ascii_cam.py
```

Use these keys during runtime:

| Key | Action |
|-----|--------|
| `q` | Quit |
| `+` / `-` | Adjust speed / delay |
| `b` | Toggle block background mode |
| `v` | Toggle original webcam preview |

### 3. Convert Static Image / URL to ASCII (CLI)
Use the advanced `ascii_image.py` utility which supports both local images and URLs:
```bash
# Basic conversion (auto terminal width)
python ascii_image.py diwali.jpg

# Fetch from URL, specify custom width & color mode
python ascii_image.py https://example.com/logo.png --width 80 --mode color

# Grayscale / Black & White with customized gradient sets
python ascii_image.py Anas.jpg --mode bw --gradient blocks --invert

# Export to colored HTML or plain TXT file
python ascii_image.py diwali.jpg --output art.html
python ascii_image.py diwali.jpg --output art.txt --width 120
```

Run `python ascii_image.py --help` to see all available CLI options.

### 4. Run the Web Studio
The project includes a gorgeous web interface for real-time ASCII conversion (Webcam, Upload, URL).

You can open the web app instantly:
- Simply double-click/open [web/index.html](file:///home/anasa/Projects/ascii_cam/web/index.html) in any modern browser.
- **Or** run a local web server:
  ```bash
  python -m http.server 8000 --directory web
  ```
  Then visit `http://localhost:8000` in your browser.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas to improve the project — whether it's a bug fix, new feature, or a cool optimization — feel free to share.

### To Contribute:

1. Fork the repository
2. Clone your fork
   ```bash
   git clone https://github.com/Anasarfeen123/ascii_cam.git
   ```
3. Create a new branch
   ```bash
   git checkout -b your-feature-name
   ```
4. Make your changes 🚀
5. Commit and push
   ```bash
   git add .
   git commit -m "Add: your awesome feature"
   git push origin your-feature-name
   ```
6. Open a Pull Request on the main repo

Please make sure your code is clean and documented. If you're adding something major, open an issue first so we can discuss it.

---

## 🧪 Suggestions for Contribution Ideas

- Add CLI image path input support to `test_bw.py` / `test_col.py`
- Add `.txt` export support for ASCII frames
- Add a GIF recorder mode (ASCII to animated `.txt`)
- Add TUI (Terminal UI) with options for real-time settings
- Implement different ASCII character sets for various styles
- Add support for different image formats
- Create configuration file support for default settings
- Add performance optimizations for larger terminal windows

---

## 📋 Requirements

Create a `requirements.txt` file with:
```
opencv-python
numpy
colorama
pillow
```

---

## 🎮 Usage Examples

### Basic Usage
```bash
# Start with default settings
python ascii_cam.py

# Convert a static image to B/W ASCII
python test_bw.py

# Convert a static image to colored ASCII
python test_col.py
```

### Runtime Controls
- Press `+` to increase frame rate (decrease delay)
- Press `-` to decrease frame rate (increase delay)
- Press `v` to toggle the original webcam preview window
- Press `q` to quit the application

---

## 🐛 Troubleshooting

**Camera not detected:**
- Make sure your webcam is not being used by another application
- Try running with administrator/sudo privileges
- Check if OpenCV can access your camera device

**Performance issues:**
- Reduce terminal window size for better performance
- Use the frame rate controls (`+`/`-`) to adjust speed
- Close other applications that might be using system resources

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute as needed.

---

## 🙏 Acknowledgments

- OpenCV for camera capture functionality
- Colorama for terminal color support
- The ASCII art community for inspiration
