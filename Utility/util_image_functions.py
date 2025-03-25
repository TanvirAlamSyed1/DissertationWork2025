import os
from Utility import *
from Utility.annotation_classes import *
from tkinter import messagebox
from PIL import Image, ImageTk,ImageDraw
import tkinter as tk

def load_image(self):
    if self.user_notification_preference:
        self.notification_number += 1

        confirm = messagebox.askyesno(
            "Have you saved annotations?",
            "If you haven't saved your annotations and move on, they won't be saved. Are you sure you want to continue?",
            parent=self.controller
        )

        if not confirm:
            self.notification_number -= 1  # Roll back count if cancelled
            return

        if self.notification_number >= 3:
            disable_prompt = messagebox.askyesno(
                "Annoyed at Notifications?",
                "Would you like to stop seeing this warning in the future?",
                parent=self.controller
            )
            if disable_prompt:
                self.user_notification_preference = False
            self.notification_number = 0  # Reset either way

    if 0 <= self.current_image_index < len(self.image_files):
        image_path = os.path.join(self.input_folder, self.image_files[self.current_image_index])
        self.image = Image.open(image_path)
        new_width, new_height = self.image.width, self.image.height
        self.photo = ImageTk.PhotoImage(self.image)

        self.canvas.delete("image")
        self.canvas.config(width=new_width, height=new_height)

        self.image_x = 0
        self.image_y = 0
        self.canvas.create_image(self.image_x, self.image_y, anchor=tk.NW, image=self.photo, tags="image")
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))

        self.annotations = []
        self.clear_annotation()




def next_image(self):
    """Loads the next image at its default size and resets zoom."""
    if self.current_image_index < len(self.image_files) - 1:
        self.current_image_index += 1
        self.zoom_factor = 1.0  
        self.keypoints = []
        self.keypoint_canvas_ids = []
        self.load_image()

def prev_image(self):
    """Loads the previous image at its default size and resets zoom."""
    if self.current_image_index > 0:
        self.current_image_index -= 1
        self.zoom_factor = 1.0  
        self.keypoints = []
        self.keypoint_canvas_ids = []
        self.load_image()

def go_to_image_by_name(self):
    image_name = self.search_entry.get().strip()
    if not image_name:
        messagebox.showwarning("Input Required", "Please enter an image name.", parent=self.controller)
        return

    # Normalize name for search
    image_name = image_name.lower()
    
    # Try exact match
    for i, filename in enumerate(self.image_files):
        if filename.lower() == image_name or filename.lower().startswith(image_name):
            self.current_image_index = i
            self.load_image()
            return

    messagebox.showwarning("Not Found", f"No image found matching: {image_name}", parent=self.controller)

def save_image(self):
    if not self.image or self.current_image_index == -1:
        messagebox.showwarning("No Image", "Please load an image first.", parent=self.controller)
        return

    annotated_folder = os.path.join(self.input_folder, "annotated_images")
    os.makedirs(annotated_folder, exist_ok=True)

    image_filename = self.image_files[self.current_image_index]
    base_name = os.path.splitext(image_filename)[0]
    save_path = os.path.join(annotated_folder, f"{base_name}_annotated.png")

    # Copy the image and get draw context
    image_copy = self.image.copy()
    draw = ImageDraw.Draw(image_copy)
    img_w, img_h = self.image.width, self.image.height

    for annotation in self.annotations:
        coords = annotation.coordinates

        # Handle normal coordinate scaling
        if isinstance(annotation, KeypointAnnotation):
            # Already a list of (x, y, v) tuples — normalized
            points = [(x * img_w, y * img_h) for x, y, _ in coords]
            for x, y in points:
                r = 4
                draw.ellipse((x - r, y - r, x + r, y + r), fill="green")

        else:
            # Normalize flat list
            abs_coords = [
                coord * img_w if i % 2 == 0 else coord * img_h
                for i, coord in enumerate(coords)
            ]

            if isinstance(annotation, RectangleAnnotation) and len(abs_coords) == 4:
                draw.rectangle(abs_coords, outline="red", width=3)

            elif isinstance(annotation, EllipseAnnotation) and len(abs_coords) == 4:
                draw.ellipse(abs_coords, outline="red", width=3)

            elif isinstance(annotation, FreehandAnnotation) and len(abs_coords) >= 4:
                points = list(zip(abs_coords[::2], abs_coords[1::2]))
                draw.line(points, fill="red", width=2)

            elif isinstance(annotation, PolygonAnnotation) and len(abs_coords) >= 6:
                points = list(zip(abs_coords[::2], abs_coords[1::2]))
                draw.polygon(points, outline="red")

    # Save result
    try:
        image_copy.save(save_path)
        messagebox.showinfo("Saved", f"Annotated image saved to:\n{save_path}", parent=self.controller)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save image:\n{e}", parent=self.controller)

