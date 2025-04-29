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

```bash
git clone <your-repo-link>
pip install pillow
python main.py
```

---

## 🛠️ How to Use

1. Launch with:
   ```bash
   python main.py
   ```
2. In the app:
   - Click **"Load Folder"** to select images.
   - Select an annotation type from the dropdown.
   - Draw on the canvas.
   - Save or export annotations.

### ⌨️ Shortcuts

| Action                  | Shortcut   |
|--------------------------|------------|
| Finalize Polygon/Keypoints | Ctrl + D  |
| Undo                     | Ctrl + Z   |
| Redo                     | Ctrl + Y   |
| Save annotations         | Ctrl + S   |
| Load annotations         | Ctrl + L   |
| Load folder              | Ctrl + F   |
| Next image               | Ctrl + N   |
| Previous image           | Ctrl + P   |

---

## 📸 Supported Image Formats

- `.jpg`
- `.jpeg`
- `.png`
- `.gif`
- `.bmp`

---

## ✅ Planned Improvements

- [ ] Advanced Mask Editing (painting masks)
- [ ] Inter-annotator Agreement Tracking
- [ ] Assisted Annotation (AI suggestions)
- [ ] Customizable Keyboard Shortcuts
- [ ] Multi-language Support

---

## 👨‍💻 Author

- **Tanvir Alam Syed**
- Student ID: **21326844**
- BSc (Hons) Computer Science
- **Final Year Project** @ Manchester Metropolitan University (2024–2025)
- Supervisor: **Dr. Indranath Chatterjee**

---

## 📜 Academic Notice

This project was developed in full compliance with MMU academic integrity policies, without the use of generative AI.
