import tkinter as tk
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
        
        # Annotation type combobox
        annotation_type_label = tk.Label(left_toolbar, text="Annotation Type:")
        annotation_type_label.pack(pady=(10, 5))
        self.annotation_type = ttk.Combobox(left_toolbar, values=["Rectangle", "Circle", "Freehand"])
        self.annotation_type.set("Rectangle")
        self.annotation_type.pack(pady=(0, 10), padx=5, fill=tk.X)
        self.annotation_type.bind("<<ComboboxSelected>>", self.change_annotation_type)
        self.current_annotation_type = "Rectangle"
        
        # Annotation format combobox
        annotation_format_label = tk.Label(left_toolbar, text="Annotation Format:")
        annotation_format_label.pack(pady=(10, 5))
        self.annotation_format = ttk.Combobox(left_toolbar, values=["YOLO", "COCO", "PASCAL VOC"])
        self.annotation_format.set("YOLO")
        self.annotation_format.pack(pady=(0, 10), padx=5, fill=tk.X)
        self.annotation_format.bind("<<ComboboxSelected>>", self.change_annotation_format)
        self.current_annotation_format = "YOLO"
        
        #zoom in and out functionality
        zoom_in_button = tk.Button(left_toolbar, text="Zoom In", command=self.zoom_in)
        zoom_in_button.pack(pady=5, padx=5, fill=tk.X)

        zoom_out_button = tk.Button(left_toolbar, text="Zoom Out", command=self.zoom_out)
        zoom_out_button.pack(pady=5, padx=5, fill=tk.X)
        # Canvas for drawing
        self.canvas = tk.Canvas(main_content, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
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
        
        # Bind canvas events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        print("hello world")
        
    def on_drag(self, event):
       print("hello world")

    def on_release(self, event):
        print("hello world")

    def button_click(self, button_text):
        print("hello world")
        
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
            self.clear_annotations()
    
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
        
    def clear_annotation(self):
        print ("hello world")
        
    def undo_annotation(self):
        print ("hello world")
        
    def change_annotation_format(self,event):
        print("hello world")
    
    def change_annotation_type(self,event):
        print("hello world")
        
       
