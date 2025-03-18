import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import simpledialog
import json
import os

def load_folder(self):
    """Allows user to select an input folder and loads all image files."""
    self.input_folder = filedialog.askdirectory(title="Select Input Folder")
    if self.input_folder:
        self.output_folder = os.path.join(self.input_folder, "annotated_images")
        os.makedirs(self.output_folder, exist_ok=True)

        # Load image files from folder
        self.image_files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        if self.image_files:
            self.current_image_index = 0
            self.load_image()  # Ensure this function loads the selected image
        else:
            messagebox.showwarning("Warning", "No image files found in the selected folder.")

def save_annotations(self):
    """Saves all annotations for the current image as a JSON file."""
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.basename(current_image)  # Get full image name
    annotations_file = os.path.join(self.output_folder, f"{os.path.splitext(image_name)[0]}_annotations.json")

    if not self.image:
        messagebox.showerror("Error", "No image loaded.")
        return

    img_width, img_height = self.image.width, self.image.height  # Ensure this refers to the PIL image

    # Save annotations with image metadata
    annotations_data = {
        "image_name": image_name,  # ✅ Store the image name
        "image_width": img_width,
        "image_height": img_height,
        "annotations": []
    }

    for annotation in self.annotations:
        annotations_data["annotations"].append({
            "type": annotation["type"],
            "coordinates": annotation["coordinates"],
            "label": annotation.get("label", "No Label")  # Ensure label is stored
        })

    # Save to JSON file
    try:
        with open(annotations_file, "w") as f:
            json.dump(annotations_data, f, indent=4)
        messagebox.showinfo("Saved", f"Annotations saved to {annotations_file}")
    except IOError as e:
        messagebox.showerror("Error", f"Failed to save annotations: {e}")


def load_annotations(self):
    """Loads annotations for the currently displayed image."""
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.basename(current_image)  # Get image name
    annotations_file = os.path.join(self.output_folder, f"{os.path.splitext(image_name)[0]}_annotations.json")

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

    for ann in annotations_data["annotations"]:
        ann_type = ann.get("type")
        rel_coords = ann.get("coordinates", [])  # Ensure default empty list
        label = ann.get("label", "No Label")  # Ensure label is always present

        if ann_type and rel_coords:
            self.annotations.append({
                "type": ann_type,
                "coordinates": rel_coords,
                "label": label
            })

    # Redraw annotations & update UI
    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Loaded", f"Annotations loaded from {annotations_file}")

def redraw_annotations(self):
    """Redraws all annotations on the canvas without deleting the image."""
    self.canvas.delete("annotation")  # Clear only annotations, not the image

    if not self.image:
        return  # Prevent errors if no image is loaded

    current_width = self.image.width
    current_height = self.image.height

    # Ensure image is properly drawn with a tag
    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

    # Redraw each annotation
    for annotation in self.annotations:
        self.redraw_annotation(annotation, current_width, current_height)

    self.update_annotation_listbox()  # Update Listbox UI

def label_annotation(self, event):
    """Allows the user to label an annotation when they double-click on it in the Listbox."""
    # Get selected annotation index
    selected_index = self.annotation_listbox.curselection()
    
    if not selected_index:  # If nothing is selected, return
        return

    selected_index = selected_index[0]  # Get the first selected item index
    annotation = self.annotations[selected_index]  # Get the annotation dictionary

    # Ask the user for a label
    label = tk.simpledialog.askstring("Label Annotation", "Enter a label for this annotation:")

    if label:  
        annotation["label"] = label  # Update label
        self.update_annotation_listbox()  # Refresh listbox to reflect the label


def download_annotations(self):
    print("hello world")
