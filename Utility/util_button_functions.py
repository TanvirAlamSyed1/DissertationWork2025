import os
from tkinter import filedialog, messagebox

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

def save_annotation(self):  
    print("Saving annotation...")

def add_label():
    print("Adding label...")

def download_annotations():
    print("Downloading annotations...")
