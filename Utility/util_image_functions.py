import os
from PIL import Image, ImageTk
import tkinter as tk

def load_image(self):
    if 0 <= self.current_image_index < len(self.image_files):
        image_path = os.path.join(self.input_folder, self.image_files[self.current_image_index])
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.config(width=self.image.width, height=self.image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")
        self.annotations = []
        self.clear_annotation()

def prev_image(self):
    if self.current_image_index > 0:
        self.current_image_index -= 1
        self.load_image()

def next_image(self):
    if self.current_image_index < len(self.image_files) - 1:
        self.current_image_index += 1
        self.load_image()
