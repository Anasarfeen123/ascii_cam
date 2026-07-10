// --- State Management ---
const state = {
    sourceType: 'upload', // 'upload', 'webcam', 'url'
    activeImage: null,    // HTMLImageElement
    webcamStream: null,
    isWebcamRunning: false,
    colorMode: 'color',   // 'color', 'bw'
    renderStyle: 'char',  // 'char', 'bg'
    charPreset: 'blocks', // 'blocks', 'standard', '1', 'custom'
    customChar: '█',
    width: 100,
    charAspect: 0.55,
    brightness: 1.0,
    contrast: 1.0,
    invert: false,
    lastFrameTime: 0,
    animationFrameId: null
};

// --- Character Gradients ---
const GRADIENTS = {
    blocks: ["█", "▓", "▒", "░", " "],
    standard: ["@", "#", "%", "*", "+", "=", "-", ":", ".", " "],
    1: ["N", "K", "0", "O", "d", "X", "k", "o", "x", "l", "c", ";", ":", ",", "'", ".", " "],
    custom: ["█"]
};

// --- DOM Elements ---
const el = {
    tabs: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    webcamVideo: document.getElementById('webcam-video'),
    webcamPlaceholder: document.getElementById('webcam-placeholder'),
    toggleWebcamBtn: document.getElementById('toggle-webcam-btn'),
    cameraStatus: document.getElementById('camera-status'),
    urlInput: document.getElementById('url-input'),
    loadUrlBtn: document.getElementById('load-url-btn'),
    
    // Settings
    colorModeGroup: document.getElementById('color-mode-group'),
    renderStyleGroup: document.getElementById('render-style-group'),
    outputTypeItem: document.getElementById('output-type-item'),
    charPresetItem: document.getElementById('char-preset-item'),
    charPreset: document.getElementById('char-preset'),
    customCharItem: document.getElementById('custom-char-item'),
    customChar: document.getElementById('custom-char'),
    resolutionRange: document.getElementById('resolution-range'),
    resolutionValue: document.getElementById('resolution-value'),
    aspectRange: document.getElementById('aspect-range'),
    aspectValue: document.getElementById('aspect-value'),
    brightnessRange: document.getElementById('brightness-range'),
    brightnessValue: document.getElementById('brightness-value'),
    contrastRange: document.getElementById('contrast-range'),
    contrastValue: document.getElementById('contrast-value'),
    invertCheckbox: document.getElementById('invert-checkbox'),
    
    // Output & Overlay
    asciiOutput: document.getElementById('ascii-output'),
    statusOverlay: document.getElementById('status-overlay'),
    statusMessage: document.getElementById('status-message'),
    copyBtn: document.getElementById('copy-btn'),
    downloadTxtBtn: document.getElementById('download-txt-btn'),
    downloadHtmlBtn: document.getElementById('download-html-btn'),
    
    // Stats
    statDim: document.getElementById('stat-dim'),
    statFps: document.getElementById('stat-fps'),
    statChars: document.getElementById('stat-chars'),
    
    // Processing Canvas
    canvas: document.getElementById('proc-canvas'),
};
const ctx = el.canvas.getContext('2d', { willReadFrequently: true });

// --- Tab Switching ---
el.tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        el.tabs.forEach(t => t.classList.remove('active'));
        el.tabContents.forEach(c => c.classList.add('hidden'));
        
        tab.classList.add('active');
        const tabId = `tab-${tab.dataset.tab}`;
        document.getElementById(tabId).classList.remove('hidden');
        
        state.sourceType = tab.dataset.tab;
        
        // Handle webcam shutdown if switching away
        if (state.sourceType !== 'webcam' && state.isWebcamRunning) {
            stopWebcam();
        }
        
        triggerRender();
    });
});

// --- Upload Handler ---
el.dropZone.addEventListener('click', () => el.fileInput.click());
el.dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    el.dropZone.classList.add('dragover');
});
el.dropZone.addEventListener('dragleave', () => {
    el.dropZone.classList.remove('dragover');
});
el.dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    el.dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        processUploadedFile(e.dataTransfer.files[0]);
    }
});
el.fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        processUploadedFile(e.target.files[0]);
    }
});

function processUploadedFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file.');
        return;
    }
    showLoader('Reading image file...');
    const reader = new FileReader();
    reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
            state.activeImage = img;
            hideLoader();
            triggerRender();
        };
        img.onerror = () => {
            hideLoader();
            alert('Failed to load image.');
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

// --- Webcam Handler ---
el.toggleWebcamBtn.addEventListener('click', () => {
    if (state.isWebcamRunning) {
        stopWebcam();
    } else {
        startWebcam();
    }
});

async function startWebcam() {
    showLoader('Accessing camera...');
    try {
        const constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            },
            audio: false
        };
        state.webcamStream = await navigator.mediaDevices.getUserMedia(constraints);
        el.webcamVideo.srcObject = state.webcamStream;
        el.webcamVideo.onloadedmetadata = () => {
            el.webcamVideo.play();
            state.isWebcamRunning = true;
            el.toggleWebcamBtn.innerHTML = '<i data-lucide="square"></i> Stop Camera Feed';
            el.toggleWebcamBtn.classList.remove('btn-primary');
            el.toggleWebcamBtn.classList.add('btn-secondary');
            el.cameraStatus.style.display = 'inline-flex';
            el.webcamPlaceholder.classList.add('hidden');
            hideLoader();
            lucide.createIcons();
            
            // Start render loop
            state.lastFrameTime = performance.now();
            webcamRenderLoop();
        };
    } catch (err) {
        hideLoader();
        console.error('Webcam Access Error:', err);
        alert('Could not access webcam. Please verify camera permissions.');
    }
}

function stopWebcam() {
    state.isWebcamRunning = false;
    if (state.animationFrameId) {
        cancelAnimationFrame(state.animationFrameId);
        state.animationFrameId = null;
    }
    if (state.webcamStream) {
        state.webcamStream.getTracks().forEach(track => track.stop());
        state.webcamStream = null;
    }
    el.webcamVideo.srcObject = null;
    el.toggleWebcamBtn.innerHTML = '<i data-lucide="play"></i> Start Camera Feed';
    el.toggleWebcamBtn.classList.remove('btn-secondary');
    el.toggleWebcamBtn.classList.add('btn-primary');
    el.cameraStatus.style.display = 'none';
    el.webcamPlaceholder.classList.remove('hidden');
    lucide.createIcons();
    triggerRender();
}

function webcamRenderLoop() {
    if (!state.isWebcamRunning) return;
    
    const t0 = performance.now();
    renderASCII(el.webcamVideo);
    const t1 = performance.now();
    
    el.statFps.textContent = `${Math.round(t1 - t0)} ms`;
    
    state.animationFrameId = requestAnimationFrame(webcamRenderLoop);
}

// --- URL Handler ---
el.loadUrlBtn.addEventListener('click', loadUrlImage);
el.urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') loadUrlImage();
});

function loadUrlImage() {
    const url = el.urlInput.value.trim();
    if (!url) return;
    
    showLoader('Fetching image from URL (requires CORS support)...');
    
    const img = new Image();
    img.crossOrigin = 'anonymous'; // Request CORS permissions
    img.onload = () => {
        state.activeImage = img;
        hideLoader();
        triggerRender();
    };
    img.onerror = () => {
        hideLoader();
        alert('Failed to load image from URL. This is likely due to CORS restrictions on the hosting server. Try copying/saving the image and dragging it to the File upload area.');
    };
    img.src = url;
}

// --- Settings Listeners ---
// Color mode buttons
el.colorModeGroup.querySelectorAll('.group-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        el.colorModeGroup.querySelectorAll('.group-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.colorMode = btn.dataset.value;
        
        // Hide/show render styles since grayscale does not need solid block
        if (state.colorMode === 'bw') {
            el.outputTypeItem.classList.add('hidden');
            el.charPresetItem.classList.remove('hidden');
        } else {
            el.outputTypeItem.classList.remove('hidden');
            if (state.renderStyle === 'bg') {
                el.charPresetItem.classList.add('hidden');
            } else {
                el.charPresetItem.classList.remove('hidden');
            }
        }
        triggerRender();
    });
});

// Render style buttons
el.renderStyleGroup.querySelectorAll('.group-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        el.renderStyleGroup.querySelectorAll('.group-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.renderStyle = btn.dataset.value;
        
        // Hide presets if solid block mode is selected (which doesn't use characters)
        if (state.renderStyle === 'bg') {
            el.charPresetItem.classList.add('hidden');
            el.customCharItem.classList.add('hidden');
        } else {
            el.charPresetItem.classList.remove('hidden');
            if (state.charPreset === 'custom') {
                el.customCharItem.classList.remove('hidden');
            }
        }
        triggerRender();
    });
});

// Presets Select
el.charPreset.addEventListener('change', (e) => {
    state.charPreset = e.target.value;
    if (state.charPreset === 'custom') {
        el.customCharItem.classList.remove('hidden');
    } else {
        el.customCharItem.classList.add('hidden');
    }
    triggerRender();
});

// Custom Character Input
el.customChar.addEventListener('input', (e) => {
    state.customChar = e.target.value || ' ';
    GRADIENTS.custom = state.customChar.split('');
    triggerRender();
});

// Resolution range
el.resolutionRange.addEventListener('input', (e) => {
    state.width = parseInt(e.target.value);
    el.resolutionValue.textContent = `${state.width} chars`;
    triggerRender();
});

// Aspect range
el.aspectRange.addEventListener('input', (e) => {
    state.charAspect = parseFloat(e.target.value);
    el.aspectValue.textContent = state.charAspect.toFixed(2);
    triggerRender();
});

// Brightness range
el.brightnessRange.addEventListener('input', (e) => {
    state.brightness = parseFloat(e.target.value);
    el.brightnessValue.textContent = state.brightness.toFixed(2);
    triggerRender();
});

// Contrast range
el.contrastRange.addEventListener('input', (e) => {
    state.contrast = parseFloat(e.target.value);
    el.contrastValue.textContent = state.contrast.toFixed(2);
    triggerRender();
});

// Invert checkbox
el.invertCheckbox.addEventListener('change', (e) => {
    state.invert = e.target.checked;
    triggerRender();
});

// --- Core ASCII Rendering Engine ---
function triggerRender() {
    if (state.sourceType === 'webcam') {
        // Handled by requestAnimationFrame loop
        return;
    }
    
    if (state.sourceType === 'upload' || state.sourceType === 'url') {
        if (state.activeImage) {
            const t0 = performance.now();
            renderASCII(state.activeImage);
            const t1 = performance.now();
            el.statFps.textContent = `${Math.round(t1 - t0)} ms`;
        } else {
            showOverlayMessage('Load an image to begin conversion...');
        }
    }
}

function renderASCII(source) {
    // 1. Calculate dimensions
    let srcW = source.videoWidth || source.width || 100;
    let srcH = source.videoHeight || source.height || 100;
    
    const aspect = srcH / srcW;
    const destW = state.width;
    const destH = Math.max(1, Math.round(aspect * destW * state.charAspect));
    
    // 2. Setup canvas
    el.canvas.width = destW;
    el.canvas.height = destH;
    
    // 3. Apply CSS-like visual filters to canvas context
    let filterStr = '';
    if (state.brightness !== 1.0) filterStr += `brightness(${state.brightness}) `;
    if (state.contrast !== 1.0) filterStr += `contrast(${state.contrast}) `;
    if (state.invert) filterStr += `invert(1) `;
    ctx.filter = filterStr.trim() || 'none';
    
    // 4. Draw image/video to canvas
    ctx.drawImage(source, 0, 0, destW, destH);
    
    // 5. Read pixels
    const imgData = ctx.getImageData(0, 0, destW, destH);
    const pixels = imgData.data;
    
    // 6. Build ASCII art representation
    let characterSet = GRADIENTS[state.charPreset] || GRADIENTS.blocks;
    
    // Handle reverse shading if invert is selected (or normal gradients)
    if (state.invert) {
        // Copy and reverse character set if it is a list
        characterSet = [...characterSet].reverse();
    }
    const numChars = characterSet.length;
    
    let htmlOutput = '';
    let textOutput = '';
    
    for (let y = 0; y < destH; y++) {
        let rowHtml = '';
        let rowText = '';
        
        for (let x = 0; x < destW; x++) {
            const idx = (y * destW + x) * 4;
            const r = pixels[idx];
            const g = pixels[idx + 1];
            const b = pixels[idx + 2];
            
            // Calculate grayscale value
            const gray = 0.299 * r + 0.587 * g + 0.114 * b;
            
            // Character matching
            const charIdx = Math.min(Math.floor((gray / 256) * numChars), numChars - 1);
            const c = characterSet[charIdx];
            
            if (state.colorMode === 'bw') {
                // Grayscale mode - plain text representation
                rowText += c;
                // Escape characters for HTML output
                let escapedC = c.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/ /g, '&nbsp;');
                rowHtml += escapedC;
            } else {
                // Color modes
                if (state.renderStyle === 'bg') {
                    // Solid Background blocks
                    rowText += ' ';
                    rowHtml += `<span style="background-color: rgb(${r},${g},${b});">&nbsp;</span>`;
                } else {
                    // Colored Foreground characters
                    rowText += c;
                    let escapedC = c.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/ /g, '&nbsp;');
                    rowHtml += `<span style="color: rgb(${r},${g},${b});">${escapedC}</span>`;
                }
            }
        }
        htmlOutput += rowHtml + '\n';
        textOutput += rowText + '\n';
    }
    
    // 7. Render output to screen
    el.asciiOutput.innerHTML = htmlOutput;
    
    // Save plain text representation on element dataset for copying/saving
    el.asciiOutput.dataset.plainText = textOutput;
    
    // 8. Update Stats
    el.statDim.textContent = `${destW} x ${destH}`;
    el.statChars.textContent = destW * destH;
    
    hideOverlay();
}

// --- Clipboard & Download Triggers ---
el.copyBtn.addEventListener('click', () => {
    const text = el.asciiOutput.dataset.plainText;
    if (!text) return;
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = el.copyBtn.innerHTML;
        el.copyBtn.innerHTML = '<i data-lucide="check"></i> Copied!';
        el.copyBtn.classList.remove('btn-secondary');
        el.copyBtn.classList.add('btn-primary');
        lucide.createIcons();
        
        setTimeout(() => {
            el.copyBtn.innerHTML = originalText;
            el.copyBtn.classList.remove('btn-primary');
            el.copyBtn.classList.add('btn-secondary');
            lucide.createIcons();
        }, 2000);
    }).catch(err => {
        console.error('Clipboard Error:', err);
        alert('Could not copy to clipboard automatically.');
    });
});

el.downloadTxtBtn.addEventListener('click', () => {
    const text = el.asciiOutput.dataset.plainText;
    if (!text) return;
    
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ascii-art-${Date.now()}.txt`;
    link.click();
    URL.revokeObjectURL(url);
});

el.downloadHtmlBtn.addEventListener('click', () => {
    const htmlContent = el.asciiOutput.innerHTML;
    if (!htmlContent) return;
    
    const doc = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ASCII Studio Export</title>
    <style>
        body {
            background-color: #000000;
            color: #ffffff;
            margin: 0;
            padding: 24px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        pre {
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 8px;
            line-height: 1;
            letter-spacing: 0;
            margin: 0;
            padding: 20px;
            background: #000;
            border-radius: 8px;
            overflow-x: auto;
            white-space: pre;
        }
    </style>
</head>
<body>
    <pre>${htmlContent}</pre>
</body>
</html>`;
    
    const blob = new Blob([doc], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ascii-art-${Date.now()}.html`;
    link.click();
    URL.revokeObjectURL(url);
});

// --- Helper Functions ---
function showLoader(message) {
    el.statusMessage.textContent = message;
    el.statusOverlay.querySelector('.spinner').style.display = 'block';
    el.statusOverlay.classList.remove('hidden');
}

function hideLoader() {
    el.statusOverlay.classList.add('hidden');
}

function showOverlayMessage(message) {
    el.statusMessage.textContent = message;
    el.statusOverlay.querySelector('.spinner').style.display = 'none';
    el.statusOverlay.classList.remove('hidden');
}

function hideOverlay() {
    el.statusOverlay.classList.add('hidden');
}
