import os
from PIL import Image, ImageTk
import tkinter as tk

def load_image(self):
    """Loads the current image at its default size and resets scroll region."""
    if 0 <= self.current_image_index < len(self.image_files):
        image_path = os.path.join(self.input_folder, self.image_files[self.current_image_index])
        self.image = Image.open(image_path)
        new_width, new_height = self.image.width, self.image.height
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.delete("image")
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))
        self.annotations = []
        self.clear_annotation()


def next_image(self):
    """Loads the next image at its default size and resets zoom."""
    if self.current_image_index < len(self.image_files) - 1:
        self.current_image_index += 1
        self.zoom_factor = 1.0  
        self.load_image()

def prev_image(self):
    """Loads the previous image at its default size and resets zoom."""
    if self.current_image_index > 0:
        self.current_image_index -= 1
        self.zoom_factor = 1.0  
        self.load_image()
