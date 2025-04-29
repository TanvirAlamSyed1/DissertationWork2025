# 🖍️ Image Annotation Tool

A cross-platform desktop application for annotating images with bounding boxes, ellipses, circles, freehand lines, polygons, semantic segmentation masks, and keypoints — built with **Python + Tkinter**.

> Developed for the 6G6Z0019 Synoptic Project at **Manchester Metropolitan University (2024–2025)**.

---

## 🚀 Features

- 📂 Load a folder of images
- 🖼️ Annotate using:
  - Rectangles
  - Ellipses
  - Circles
  - Freehand lines
  - Polygons
  - Keypoints
  - Semantic Segmentation Masks
- 💾 Save annotations per image (JSON format)
- 📤 Export annotations in multiple formats:
  - **COCO** (bounding boxes, segmentation, keypoints)
  - **YOLO** (object detection)
  - **Pascal VOC** (XML format)
  - **Semantic Masks** (PNG images)
- 🖌️ Export annotated images (PNG)
- 🔁 Undo/redo actions
- 🧹 Clear annotations
- 🔎 Search by image name
- 🔄 Edit existing annotations (move, label, lock/unlock)
- 🎨 Visual colour cues:
  - Red = Standard annotation
  - Grey = Locked annotation
  - Blue = Selected annotation
  - Purple = Semantic segmentation mask
- 🔍 Smooth zooming with mouse scroll
- ⌨️ Keyboard shortcuts for faster workflow
- 🖱️ Context menu for labeling, deleting, masking, locking
- ✅ Bound-checking to prevent invalid annotations
- 🔒 Local-only operation (offline, no admin rights needed)
---
## 📦 Installation

1. clone this repo and install pillow - 'pip install pillow'
2. run main.py and let the application run
3. There is also a downloadable .exe file you can get from the dist folder ( Windows Only)

## 🛠️ How to Use
1. Run app 'Python main.py'
2. From the UI:
   - Click "Load Folder" to select your image folder.
   - Use the dropdown to select annotation type.
   - Annotate directly on the canvas using your mouse.
   - Save annotations with "Save Annotations" button.
   - Export the annotated image using "Export Annotated Image".

⌨️ Shortcuts
- Action | Shortcut
- Finalize polygon/keypoint | F
- Undo | Ctrl + Z
- Redo | Ctrl + Y
- Save annotations | Ctrl + S
- Load annotations | Ctrl + L
- Next image | Ctrl + N
- Previous image | Ctrl + P
- Load image folder | Ctrl + F

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
- Made with 💙 by Tanvir Alam Syed
- Student ID: 21326844
- Final Year Project @ Manchester Metropolitan University (2024–25)
- Supervisor: Dr Indranath Chatterjee
