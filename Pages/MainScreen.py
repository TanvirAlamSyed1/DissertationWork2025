import tkinter as tk
import json
from tkinter import ttk,filedialog
from PIL import Image, ImageTk, ImageDraw
import os
import Pages.WelcomeScreen

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        # Create a main content frame
        main_content = tk.Frame(self)
        main_content.pack(fill=tk.BOTH, expand=True)
        
        self.image = None
        self.photo = None
        self.annotations = []
        self.image_files = []
        self.current_image_index = -1
        self.input_folder = ""
        self.output_folder = ""
        self.current_annotation = None
        
        # Left toolbar for annotation comboboxes
        left_toolbar = tk.Frame(main_content, bg='lightgray', width=200)
        left_toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_toolbar.pack_propagate(False)  # Prevent shrinking
        #select the folder the user wants to annotate
        load_folder_button = tk.Button(left_toolbar, text="Load Folder", command=self.load_folder)
        load_folder_button.pack(pady=10, padx=5, fill=tk.X)
        #Allow the user to save their current image annotation
        save_annotation_button = tk.Button(left_toolbar, text="Save Annotation Of Current Image", command=self.save_annotation)
        save_annotation_button.pack(pady=10, padx=5, fill=tk.X)
        
        # Annotation type combobox
        annotation_type_label = tk.Label(left_toolbar, text="Annotation Type:")
        annotation_type_label.pack(pady=(10, 5))
        self.annotation_type = ttk.Combobox(left_toolbar, values=["Rectangle", "Circle", "Freehand"])
        self.annotation_type.set("Rectangle")
        self.annotation_type.pack(pady=(0, 10), padx=5, fill=tk.X)
        self.annotation_type.bind("<<ComboboxSelected>>", self.change_annotation_type)
        self.current_annotation_type = "Rectangle"
        
        download_annotation_button = tk.Button(left_toolbar, text="Download All Annotations", command=self.download_annotations)
        download_annotation_button.pack(pady=10, padx=5, fill=tk.X)
        
        #zoom in and out functionality
        zoom_in_button = tk.Button(left_toolbar, text="Zoom In", command=self.zoom_in)
        zoom_in_button.pack(pady=5, padx=5, fill=tk.X)

        zoom_out_button = tk.Button(left_toolbar, text="Zoom Out", command=self.zoom_out)
        zoom_out_button.pack(pady=5, padx=5, fill=tk.X)
        
        # Add label entry field
        label_frame = tk.Frame(left_toolbar)
        label_frame.pack(pady=10, padx=5, fill=tk.X)

        label_label = tk.Label(label_frame, text="Annotation Label:")
        label_label.pack(side=tk.TOP, anchor='w')  # This places the label on top

        self.label_entry = tk.Entry(label_frame)
        self.label_entry.pack(side=tk.TOP, fill=tk.X, expand=True)  # This places the entry below the label
        
        label_button = tk.Button(left_toolbar, text="add label to latest annotation", command=self.addlabel)
        label_button.pack(pady=5, padx=5, fill=tk.X)
        
        # Right sidebar for displaying annotations
        right_sidebar = tk.Frame(main_content, bg='lightgray', width=250)
        right_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        right_sidebar.pack_propagate(False)  # Prevent shrinking
        
        annotation_list_label = tk.Label(right_sidebar, text="Latest Annotations:", bg='lightgray')
        annotation_list_label.pack(pady=(10, 5))
        
        self.annotation_listbox = tk.Listbox(right_sidebar, width=30, height=20)
        self.annotation_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
       # Create the bottom toolbar
        bottom_toolbar = tk.Frame(self)
        bottom_toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a frame to hold the buttons
        button_frame = tk.Frame(bottom_toolbar)
        button_frame.pack(expand=True)

        # Buttons at the bottom
        buttons = [
            ("Previous", self.prev_image),
            ("Next", self.next_image),
            ("Save Annotations", self.save_annotation),
            ("Undo Annotation", self.undo_annotation),
            ("Clear Annotations", self.clear_annotation)
        ]

        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Switch window button
        switch_window_button = tk.Button(
            bottom_toolbar,
            text="Go to the Main Screen",
            command=lambda: controller.show_frame(Pages.WelcomeScreen.WelcomePage),
        )
        switch_window_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
         # Canvas for drawing
        self.canvas = tk.Canvas(main_content, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Bind canvas events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.current_annotation_type == "Freehand":
            self.current_annotation = self.canvas.create_line(
                self.start_x, self.start_y, self.start_x, self.start_y,
                fill="red", width=2, tags="annotation"
            )

    def on_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        if self.current_annotation_type == "Rectangle":
            self.canvas.delete("temp_annotation")
            self.current_annotation = self.canvas.create_rectangle(
                self.start_x, self.start_y, cur_x, cur_y,
                outline="red", tags="temp_annotation"
            )
        elif self.current_annotation_type == "Circle":
            self.canvas.delete("temp_annotation")
            radius = ((cur_x - self.start_x) ** 2 + (cur_y - self.start_y) ** 2) ** 0.5
            self.current_annotation = self.canvas.create_oval(
                self.start_x - radius, self.start_y - radius,
                self.start_x + radius, self.start_y + radius,
                outline="red", tags="temp_annotation"
            )
        elif self.current_annotation_type == "Freehand":
            self.canvas.coords(
                self.current_annotation,
                *self.canvas.coords(self.current_annotation),
                cur_x, cur_y
            )

    def on_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.canvas.delete("temp_annotation")
        
        if self.current_annotation_type == "Rectangle":
            self.current_annotation = self.canvas.create_rectangle(
                self.start_x, self.start_y, end_x, end_y,
                outline="red", tags="annotation"
            )
        elif self.current_annotation_type == "Circle":
            radius = ((end_x - self.start_x) ** 2 + (end_y - self.start_y) ** 2) ** 0.5
            self.current_annotation = self.canvas.create_oval(
                self.start_x - radius, self.start_y - radius,
                self.start_x + radius, self.start_y + radius,
                outline="red", tags="annotation"
            )
        
        annotation_coords = self.canvas.coords(self.current_annotation)
        self.annotations.append((self.current_annotation_type, annotation_coords))
        self.update_annotation_listbox()

    def update_annotation_listbox(self):
        self.annotation_listbox.delete(0, tk.END)
        for i, (ann_type, coords) in enumerate(self.annotations):
            self.annotation_listbox.insert(tk.END, f"{i+1}. {ann_type}: {coords}")

    def clear_annotation(self):
        self.canvas.delete("annotation")
        self.annotations.clear()
        self.update_annotation_listbox()

    def undo_annotation(self):
        if self.annotations:
            last_annotation = self.annotations.pop()
            self.canvas.delete(self.canvas.find_withtag("annotation")[-1])
            self.update_annotation_listbox()

    def change_annotation_format(self, event):
        self.current_annotation_format = self.annotation_format.get()

    def change_annotation_type(self, event):
        self.current_annotation_type = self.annotation_type.get()
            
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
        
    def update_image(self):
        print("hello world")
       
    def load_image(self):
         if 0 <= self.current_image_index < len(self.image_files):
            image_path = os.path.join(self.input_folder, self.image_files[self.current_image_index])
            self.image = Image.open(image_path)
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.config(width=self.image.width, height=self.image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
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
    
    def zoom_in(self):
        print("hello world")
        
    def zoom_out(self):
        print("hello world")
    
    def save_annotation(self):
        print ("hello world")
        
    def addlabel():
        print("hello world")
        
       
