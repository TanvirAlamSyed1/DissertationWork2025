import tkinter as tk
from tkinter import ttk
from Utility import util_image_functions
from Utility import util_annotation_function
from Utility import util_button_functions
from Utility import util_zoom_functions
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller  # Assign the controller to self.controller
        # Create a main content frame
        main_content = tk.Frame(self)
        main_content.pack(fill=tk.BOTH, expand=True)
        
        self.image = None #this stores the file path
        self.photo = None #this uploads the picture to the screen
        self.annotations = [] #stores annotations
        self.undone_annotations = []  # Stores undone annotations for redo
        self.image_files = [] #loads all files within the folder
        self.current_image_index = -1
        self.input_folder = "" #serves as a storage location for the path to the directory selected by the user.
        self.output_folder = "" #used to create a folder that all annotations can be saved into
        self.current_annotation = None
        self.zoom_factor = 1.0 #zoom in and out
        
        # Left toolbar for annotation comboboxes
        left_toolbar = tk.Frame(main_content, bg='lightgray', width=200)
        left_toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_toolbar.pack_propagate(False)  # Prevent shrinking
        #select the folder the user wants to annotate
        load_folder_button = tk.Button(left_toolbar, text="Load Folder", command=self.load_folder)
        load_folder_button.pack(pady=10, padx=5, fill=tk.X)
        #Allow the user to save their current image annotation
        save_annotation_button = tk.Button(left_toolbar, text="Save Annotations Of Current Image", command=self.save_annotation)
        save_annotation_button.pack(pady=10, padx=5, fill=tk.X)
        
        load_annotation_button = tk.Button(left_toolbar, text="Load Annotations Of Current Image", command=self.load_annotation)
        load_annotation_button.pack(pady=10, padx=5, fill=tk.X)
    
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
        
        # Add label entry field
        label_frame = tk.Frame(left_toolbar)
        label_frame.pack(pady=10, padx=5, fill=tk.X)
        
        # Right sidebar for displaying annotations
        right_sidebar = tk.Frame(main_content, bg='lightgray', width=250)
        right_sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        right_sidebar.pack_propagate(False)  # Prevent shrinking
        
        annotation_list_label = tk.Label(right_sidebar, text="Latest Annotations:", bg='lightgray')
        annotation_list_label.pack(pady=(10, 5))
        
        self.annotation_listbox = tk.Listbox(right_sidebar, width=30, height=20)
        self.annotation_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        # Bind double-click event to trigger label function
        self.annotation_listbox.bind("<Double-Button-1>", self.label_annotation)


        
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
            ("Undo Annotation", self.undo_annotation),
            ("Redo Annotation", self.redo_annotation),
            ("Clear Annotations", self.clear_annotation)
        ]

        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Switch window button
        switch_window_button = tk.Button(
            bottom_toolbar,
            text="Go to the Main Screen",
            command=self.switch_to_welcome_page,  # Ensure this is correct
        )
        switch_window_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
         # Canvas for drawing
        self.canvas = tk.Canvas(main_content, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Bind canvas events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        # Add mouse wheel event binding for zooming
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        # Bind keys to the entire application frame instead of the canvas
        self.bind_all("<Control-z>", self.undo_annotation)
        self.bind_all("<Control-y>", self.redo_annotation)
        

    
    def switch_to_welcome_page(self):
        print("Switch to Welcome Page button clicked")  # Debug print
        try:
            from Pages.WelcomeScreen import WelcomePage  # Lazy import
            print("WelcomePage imported successfully")  # Debug print
            self.controller.show_frame(WelcomePage)
        except ImportError as e:
            print(f"Error importing WelcomePage: {e}")  # Debug print
        except AttributeError as e:
            print(f"Error with controller or show_frame: {e}")  # Debug print
            
    #Here is where I've started splitting functions into seperate files in the utility folder, to keep code more clean
            
    def on_press(self, event): #this controlls what happens when you start annotating
        util_annotation_function.on_press(self, event)

    def on_drag(self, event):
        util_annotation_function.on_drag(self,event)

    def on_release(self, event):
        util_annotation_function.on_release(self,event)

    def update_annotation_listbox(self):
        util_annotation_function.update_annotation_listbox(self)

    def clear_annotation(self):
        util_annotation_function.clear_annotation(self)

    def undo_annotation(self,event):
        util_annotation_function.undo_annotation(self,event)
    
    def redo_annotation(self,event):
        util_annotation_function.redo_annotation(self, event)

    def change_annotation_type(self,event):
        util_annotation_function.change_annotation_type(self,event)

    def load_folder(self):
        util_button_functions.load_folder(self)
       
    def load_image(self):
        util_image_functions.load_image(self)

    def prev_image(self):
        util_image_functions.prev_image(self)
    
    def load_annotation(self):
        util_button_functions.load_annotations(self)

    def next_image(self):
        util_image_functions.next_image(self)
    
    def on_mouse_wheel(self,event):
        util_zoom_functions.on_mouse_wheel(self,event)
    
    def update_image_size(self,focus_x, focus_y, scale_factor):
        util_zoom_functions.update_image_size(self,focus_x, focus_y, scale_factor)
        
    def download_annotations(self):
        util_button_functions.download_annotations(self)
    
    def save_annotation(self):
        util_button_functions.save_annotations(self)
    
    def redraw_annotations(self):
        util_button_functions.redraw_annotations(self)
    
    def redraw_annotation(self, annotation, new_width, new_height):
        util_zoom_functions.redraw_annotation(self, annotation, new_width, new_height)
    
    def label_annotation (self,event):
        util_button_functions.label_annotation(self, event)
        
    def addlabel(self):
        print("hello world")
        
       