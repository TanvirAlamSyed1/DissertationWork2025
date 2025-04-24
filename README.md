# 🖍️ Image Annotation Tool

A cross-platform desktop application for annotating images with bounding boxes, ellipses, polygons, freehand lines, and keypoints — built with **Python + Tkinter**.

---

## 🚀 Features

- 📂 Load a folder of images
- 🖼️ Annotate using:
  - Rectangles
  - Ellipses
  - Freehand lines
  - Polygons
  - Keypoints
- 💾 Save annotations per image (JSON)
- 📷 Export annotated images (PNG)
- 🔁 Undo/redo support
- 🔍 Zoom in/out using mouse scroll
- 🔎 Search by image name
- 🎨 Color-coded visual feedback on canvas
- ✅ Bound-checking ensures annotations stay inside image
- 🧭 Keyboard shortcut to finalize annotations (`f`)
- 💬 Context menu to label/delete annotations
- 🙅 Option to turn off repeated confirmation messages

---

## 📦 Installation

1. clone this repo and install pillow - 'pip install pillow'
2. run main.py and let the application run

## 🛠️ How to Use
1. Run app 'Python main.py'
2. From the UI:
   - Click "Load Folder" to select your image folder.
   - Use the dropdown to select annotation type.
   - Annotate directly on the canvas using your mouse.
   - Save annotations with "Save Annotations" button.
   - Export the annotated image using "Export Annotated Image".

⌨️ Shortcuts
Finalize keypoint/polygon annotation -	f
Undo	Ctrl + Z
Redo	Ctrl + Y

📸 Supported Formats
- .jpg
- .jpeg
- .png
- .gif
- .bmp

✅ To-Do / Improvements
 - Semantic Segmentation
 - YOLO / COCO format export

👨‍💻 Author
Made with 💙 by Tanvir Alam Syed
Student ID: 21326844
Final Year Project @ Manchester Metropolitan University (2024–25)
Supervisor: Dr Indranath Chatterjee
