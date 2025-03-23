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

        # Clear existing canvas content
        self.canvas.delete("image")
        self.canvas.config(width=new_width, height=new_height)

        # Draw image at top-left and store position
        self.image_x = 0
        self.image_y = 0
        self.canvas.create_image(self.image_x, self.image_y, anchor=tk.NW, image=self.photo, tags="image")

        # Set canvas scroll region
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))

        # Reset annotations
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
