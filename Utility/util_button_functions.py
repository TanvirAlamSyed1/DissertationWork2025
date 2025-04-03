import tkinter as tk
from tkinter import filedialog, messagebox,simpledialog
from Utility.annotation_classes import *
import json
import os
from Utility.util_export_functions import (
    load_all_annotations,
    export_to_coco,
    export_to_yolo,
    export_to_pascal_voc
)

def show_listbox_menu(self, event):
    widget = event.widget
    index = widget.nearest(event.y)
    if index < len(self.annotations):
        self.selected_annotation_index = index  # ✅ Store index for delete
        self.annotation_listbox.selection_clear(0, tk.END)
        self.annotation_listbox.selection_set(index)
        self.listbox_menu.post(event.x_root, event.y_root)


def load_folder(self, event=None):
    """Allows user to select an input folder and loads all image files."""
    self.input_folder = filedialog.askdirectory(title="Select Input Folder")
    
    if not self.input_folder:
        return  # User cancelled selection

    # Check for image files first
    self.image_files = [
        f for f in os.listdir(self.input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
    ]

    if not self.image_files:
        messagebox.showwarning("Warning", "No image files found in the selected folder.")
        return

    # ✅ Only create folders if images are found
    self.annotation_folder = os.path.join(self.input_folder, "annotations")
    self.annotated_image_folder = os.path.join(self.input_folder, "annotated_images")
    os.makedirs(self.annotation_folder, exist_ok=True)
    os.makedirs(self.annotated_image_folder, exist_ok=True)

    self.current_image_index = 0
    self.load_image()



def save_annotations(self, event=None):
    """Saves all annotations for the current image as a JSON file."""
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.basename(current_image)

    # ✅ Save to annotation folder, not output_folder
    annotations_file = os.path.join(self.annotation_folder, f"{os.path.splitext(image_name)[0]}_annotations.json")

    if not self.image:
        messagebox.showerror("Error", "No image loaded.")
        return

    img_width, img_height = self.image.width, self.image.height

    annotations_data = {
        "image_name": image_name,
        "image_width": img_width,
        "image_height": img_height,
        "annotations": [a.to_dict(img_width, img_height) for a in self.annotations],
    }

    try:
        with open(annotations_file, "w") as f:
            json.dump(annotations_data, f, indent=4)
        messagebox.showinfo("Saved", f"Annotations saved to {annotations_file}")
    except IOError as e:
        messagebox.showerror("Error", f"Failed to save annotations: {e}")


def load_annotations(self,event=None):
    """Loads annotations for the currently displayed image."""
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.basename(current_image)
    annotations_file = os.path.join(self.annotation_folder, f"{os.path.splitext(image_name)[0]}_annotations.json")

    if not os.path.exists(annotations_file):
        messagebox.showwarning("Not Found", f"No annotations found for {image_name}")
        return
    try:
        with open(annotations_file, "r") as f:
            annotations_data = json.load(f)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Failed to load JSON. The file might be corrupted.")
        return

    if "annotations" not in annotations_data or "image_name" not in annotations_data:
        messagebox.showwarning("Error", "No annotations found in the file or missing image reference.")
        return

    # Validate that the annotation file matches the current image
    if annotations_data["image_name"] != image_name:
        messagebox.showwarning("Mismatch", f"Annotations belong to {annotations_data['image_name']}, not {image_name}.")
        return

    self.annotations.clear()  # Clear existing annotations
    self.canvas.update_idletasks()
    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()

    for ann in annotations_data["annotations"]:
        ann_type = ann.get("type")
        rel_coords = ann.get("coordinates", [])
        label = ann.get("label", "No Label")

        if ann_type and rel_coords:
            if ann_type == "Rectangle" and len(rel_coords) == 4:
                abs_coords = [
                    rel_coords[0] * self.image.width,
                    rel_coords[1] * self.image.height,
                    rel_coords[2] * self.image.width,
                    rel_coords[3] * self.image.height
                ]
                annotation = RectangleAnnotation(*abs_coords)

            elif ann_type == "Ellipse" and len(rel_coords) == 4:
                abs_coords = [
                    rel_coords[0] * self.image.width,
                    rel_coords[1] * self.image.height,
                    rel_coords[2] * self.image.width,
                    rel_coords[3] * self.image.height
                ]
                annotation = EllipseAnnotation(*abs_coords)

            elif ann_type == "Freehand" and len(rel_coords) % 2 == 0:
                abs_coords = []
                for i in range(0, len(rel_coords), 2):
                    x = rel_coords[i] * self.image.width
                    y = rel_coords[i + 1] * self.image.height
                    abs_coords.extend([x, y])  # ✅ creates flat list

                annotation = FreehandAnnotation(abs_coords)
            
            elif ann_type == "Circle" and len(rel_coords) == 4:
                abs_coords = [
                    rel_coords[0] * self.image.width,
                    rel_coords[1] * self.image.height,
                    rel_coords[2] * self.image.width,
                    rel_coords[3] * self.image.height
                ]
                annotation = CircleAnnotation(*abs_coords)

            
            elif ann_type == "Keypoint" and isinstance(rel_coords, list):
                abs_coords = []
                for kp in rel_coords:
                    if not isinstance(kp, (list, tuple)) or len(kp) < 2:
                        continue

                    x_norm = kp[0]
                    y_norm = kp[1]
                    v = kp[2] if len(kp) > 2 else 2

                    abs_coords.append((x_norm, y_norm, v))

                annotation = KeypointAnnotation(abs_coords)


            elif ann_type == "Polygon" and len(rel_coords) % 2 == 0:
                abs_coords = []
                for i in range(0, len(rel_coords), 2):
                    x = rel_coords[i] * self.image.width
                    y = rel_coords[i + 1] * self.image.height
                    abs_coords.extend([x, y])  # flat list of x, y

                annotation = PolygonAnnotation(abs_coords)

            else:
                continue  # Skip unrecognized or improperly formatted annotations

            annotation.label = label
            annotation.id = ann.get("id", "")
            annotation.iscrowd = ann.get("iscrowd", 0) 
            self.annotations.append(annotation)
    
    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Loaded", f"Annotations loaded from {annotations_file}")


def redraw_annotations(self):
    """Redraws all annotations on the canvas without deleting the image."""
    self.canvas.delete("annotation")

    if not self.image:
        return

    # ✅ Use zoomed image size
    current_width = int(self.image.width * self.zoom_factor)
    current_height = int(self.image.height * self.zoom_factor)

    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

    for annotation in self.annotations:
        self.redraw_annotation(annotation, current_width, current_height)

    self.update_annotation_listbox()
    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")
    self.canvas.tag_lower("image")  # 🧠 Always keep image in the background



def label_annotation(self, event):
    """Allows the user to label an annotation when they double-click on it in the Listbox."""
    selected_index = self.annotation_listbox.curselection()
    
    if not selected_index:
        return

    selected_index = selected_index[0]  
    annotation = self.annotations[selected_index]  

    label = tk.simpledialog.askstring("Label Annotation", "Enter a label for this annotation:")

    if label:  
        annotation.label = label  # Update label
        self.update_annotation_listbox()  # Refresh listbox


def download_annotations(self):
    if not self.annotation_folder:
        messagebox.showerror("Error", "No annotation folder loaded.")
        return

    export_format = simpledialog.askstring(
        "Export Format",
        "Enter format: COCO / YOLO / PascalVOC"
    )
    if not export_format:
        return

    format_lower = export_format.lower()
    data = load_all_annotations(self.annotation_folder)

    # Ask user to select a base folder
    base_folder = filedialog.askdirectory(title="Select Output Folder")
    if not base_folder:
        return

    if format_lower == "coco":
        export_folder = os.path.join(base_folder, "COCO")
        os.makedirs(export_folder, exist_ok=True)
        export_path = os.path.join(export_folder, "annotations_coco.json")
        export_to_coco(data, export_path)
        messagebox.showinfo("Exported", f"COCO annotations saved to:\n{export_path}")

    elif format_lower == "yolo":
        export_folder = os.path.join(base_folder, "YOLO")
        os.makedirs(export_folder, exist_ok=True)
        export_to_yolo(data, export_folder)
        messagebox.showinfo("Exported", f"YOLO labels saved in:\n{export_folder}")

    elif format_lower in ["pascal", "pascalvoc", "voc"]:
        export_folder = os.path.join(base_folder, "PascalVOC")
        os.makedirs(export_folder, exist_ok=True)
        export_to_pascal_voc(data, export_folder)
        messagebox.showinfo("Exported", f"Pascal VOC XMLs saved in:\n{export_folder}")

    else:
        messagebox.showerror("Unsupported Format", f"Format '{export_format}' is not supported.")

def toggle_lock_annotation(self):
    index = self.selected_annotation_index
    if index is not None and index < len(self.annotations):
        annotation = self.annotations[index]
        annotation.locked = not getattr(annotation, "locked", False)
        status = "🔒 Locked" if annotation.locked else "🔓 Unlocked"
        print(f"{status} annotation {index}")
        self.update_annotation_listbox()