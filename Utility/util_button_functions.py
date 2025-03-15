import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

def load_folder(self):
    self.input_folder = filedialog.askdirectory(title="Select Input Folder")
    if self.input_folder:
        self.output_folder = os.path.join(self.input_folder, "annotated_images")
        os.makedirs(self.output_folder, exist_ok=True)
        
        self.image_files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if self.image_files:
            self.current_image_index = 0
            self.load_image()
        else:
            messagebox.showwarning("Warning", "No image files found in the selected folder.")

def save_annotations(self):
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.splitext(os.path.basename(current_image))[0]
    annotations_file = os.path.join(self.output_folder, f"{image_name}_annotations.json")

    # Get image dimensions
    img_width, img_height = self.image.size  # Ensure this refers to the PIL image

    # Save image dimensions with annotations
    annotations_data = {
        "image_width": img_width,
        "image_height": img_height,
        "annotations": []
    }

    for ann_type, rel_coords in self.annotations:
        annotations_data["annotations"].append({
            "type": ann_type,
            "coords": rel_coords
        })

    with open(annotations_file, "w") as f:
        json.dump(annotations_data, f, indent=4)

    messagebox.showinfo("Saved", f"Annotations saved to {annotations_file}")


def load_annotations(self):
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.splitext(os.path.basename(current_image))[0]
    annotations_file = os.path.join(self.output_folder, f"{image_name}_annotations.json")

    if not os.path.exists(annotations_file):
        messagebox.showwarning("Not Found", f"No annotations found for {image_name}")
        return

    with open(annotations_file, "r") as f:
        annotations_data = json.load(f)

    # Get saved image dimensions
    saved_width = annotations_data.get("image_width", 1)  
    saved_height = annotations_data.get("image_height", 1)

    # Clear current annotations
    self.annotations.clear()

    # Load and store annotations in relative form
    for ann in annotations_data["annotations"]:
        rel_coords = ann["coords"]  # These are already relative

        self.annotations.append((ann["type"], rel_coords))  # Store as relative

    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Loaded", f"Annotations loaded from {annotations_file}")


def redraw_annotations(self):
    """Redraws annotations using the current image size."""
    self.canvas.delete("annotation")  # Clear old annotations

    current_width = self.image.width
    current_height = self.image.height

    for ann_type, rel_coords in self.annotations:
        if ann_type == "Rectangle":
            abs_coords = [
                rel_coords[0] * current_width,  
                rel_coords[1] * current_height,
                rel_coords[2] * current_width,
                rel_coords[3] * current_height
            ]
            self.canvas.create_rectangle(*abs_coords, outline="red", tags="annotation")

        elif ann_type == "Circle":
            center_x = rel_coords[0] * current_width
            center_y = rel_coords[1] * current_height
            radius = rel_coords[2] * current_width  # Using image width for uniform scaling

            self.canvas.create_oval(
                center_x - radius, center_y - radius,  
                center_x + radius, center_y + radius,
                outline="red", tags="annotation"
            )

        elif ann_type == "Freehand":
            # Scale each point correctly
            scaled_points = [p * current_width if i % 2 == 0 else p * current_height for i, p in enumerate(rel_coords)]
            self.canvas.create_line(*scaled_points, fill="red", width=2, tags="annotation")

    # Ensure listbox shows RELATIVE coordinates
    self.update_annotation_listbox()





def add_label():
    print("Adding label...")

def download_annotations():
    print("Downloading annotations...")
