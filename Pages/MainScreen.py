import tkinter as tk
from tkinter import ttk
from Utility import (
    util_image_functions,
    util_annotation_function,
    util_import_functions,
    util_zoom_functions,
    util_export_functions
)
from Utility.annotation_classes import *

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.setup_variables()
        self.setup_main_content()
        self.setup_left_toolbar()
        self.setup_right_sidebar()
        self.setup_bottom_toolbar()
        self.setup_canvas()
        self.bind_events()

    def setup_variables(self):
        self.image = None
        self.photo = None
        self.image_x = 0
        self.image_y = 0
        self.zoom_factor = 1.0
        
        self.edit_mode = False
        self.selected_annotation = None
        self.drag_start = None

        self.annotations = []
        self.undone_annotations = []
        self.keypoints = []
        self.keypoint_canvas_ids = []
        self.polygon_points = []
        self.polygon_preview_id = None

        self.image_files = []
        self.current_image_index = -1
        self.input_folder = ""
        self.output_folder = ""
        self.annotated_image_folder=""
        self.annotation_folder=""
        self.current_annotation = None

        self.annotation_classes = {
            "View": NoneType,
            "Rectangle": RectangleAnnotation,
            "Ellipse": EllipseAnnotation,
            "Circle": CircleAnnotation,
            "Polygon": PolygonAnnotation,
            "Freehand": FreehandAnnotation,
            "Keypoint": KeypointAnnotation,
        }

        self.current_annotation_type = NoneType
        self.notification_number = 0
        self.user_notification_preference = True

    def setup_main_content(self):
        self.main_content = tk.Frame(self)
        self.main_content.pack(fill=tk.BOTH, expand=True)

    def setup_left_toolbar(self):
        self.image_name_label = tk.Label(self.main_content, text="", font=("Arial", 12), anchor="w")
        self.image_name_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        left_toolbar = tk.Frame(self.main_content, bg='lightgray', width=200)
        left_toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        left_toolbar.pack_propagate(False)

        # Search bar
        tk.Label(left_toolbar, text="Search Image:").pack(pady=(10, 0), padx=5, anchor="w")
        search_frame = tk.Frame(left_toolbar)
        search_frame.pack(padx=5, fill=tk.X)
        
        self.edit_toggle = tk.BooleanVar(value=False)
        tk.Checkbutton(left_toolbar, text="Edit Mode", variable=self.edit_toggle, command=self.toggle_edit_mode).pack(pady=5, padx=5, anchor="w")
        
        # Annotation type
        tk.Label(left_toolbar, text="Annotation Type:").pack(pady=(10, 5))
        self.annotation_type = ttk.Combobox(left_toolbar, values=list(self.annotation_classes.keys()), state="readonly")
        self.annotation_type.set("View")
        self.annotation_type.pack(pady=(0, 10), padx=5, fill=tk.X)
        self.annotation_type.bind("<<ComboboxSelected>>", self.change_annotation_type)

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Go", width=4, command=self.go_to_image_by_name).pack(side=tk.RIGHT, padx=(5, 0))
        # Buttons
        buttons = [
            ("Load Folder", self.load_folder),
            ("Load Annotations Of Current Image", self.load_annotation),
            ("Save Annotations Of Current Image", self.save_annotation),
            ("Download All Annotations", self.download_annotations),
            ("Export Annotated Image",self.save_image)
        ]
        for text, cmd in buttons:
            tk.Button(left_toolbar, text=text, command=cmd).pack(pady=10, padx=5, fill=tk.X)

    def setup_right_sidebar(self):
        sidebar = tk.Frame(self.main_content, bg='lightgray', width=250)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Latest Annotations:", bg='lightgray').pack(pady=(10, 5))
        self.annotation_listbox = tk.Listbox(sidebar, width=30, height=20)
        self.annotation_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.listbox_menu = tk.Menu(self, tearoff=0)
        self.listbox_menu.add_command(label="Label Annotation", command=self.label_annotation)
        self.listbox_menu.add_command(label="Delete Annotation", command=self.delete_specific_annotation)
        self.listbox_menu.add_command(label="Toggle Crowd", command=self.toggle_crowd_label)
        self.listbox_menu.add_command(label="Lock/Unlock", command=self.toggle_lock_annotation)
        self.annotation_listbox.bind("<Button-3>", self.show_listbox_menu)

    def setup_bottom_toolbar(self):
        bottom_toolbar = tk.Frame(self)
        bottom_toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        button_frame = tk.Frame(bottom_toolbar)
        button_frame.pack(expand=True)

        for text, command in [
            ("Previous", self.prev_image),
            ("Next", self.next_image),
            ("Undo Annotation", self.undo_annotation),
            ("Redo Annotation", self.redo_annotation),
            ("Clear Annotations", self.clear_annotation)
        ]:
            tk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(bottom_toolbar, text="Go to the Main Screen", command=self.switch_to_welcome_page).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(bottom_toolbar, text="Help", command=self.switch_to_help_page).pack(side=tk.RIGHT, padx=5, pady=5)

    def setup_canvas(self):
        self.canvas = tk.Canvas(self.main_content, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", lambda e: self.on_edit_press(e) if self.edit_mode else self.on_press(e))
        self.canvas.bind("<B1-Motion>", lambda e: self.on_edit_drag(e) if self.edit_mode else self.on_drag(e))
        self.canvas.bind("<ButtonRelease-1>", lambda e: self.on_edit_release(e) if self.edit_mode else self.on_release(e))

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)

        self.bind_all("<KeyPress-d>", self.finalise_all)
        self.bind_all("<Control-z>", self.undo_annotation)
        self.bind_all("<Control-y>", self.redo_annotation)
        self.bind_all("<Control-s>", self.save_annotation)
        self.bind_all("<Control-l>", self.load_annotation)
        self.bind_all("<Control-n>", self.next_image)
        self.bind_all("<Control-p>", self.prev_image)
        self.bind_all("<Control-f>",self.load_folder)


    # ----- Delegated utility calls below -----

    def switch_to_welcome_page(self):
        try:
            from Pages.WelcomeScreen import WelcomePage
            self.controller.show_frame(WelcomePage)
        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")
    
    def switch_to_help_page(self):
        try:
            from Pages.HelpScreen import HelpPage
            self.controller.show_frame(HelpPage)
        except (ImportError, AttributeError) as e:
            print(f"Error: {e}")

    def on_press(self, event): util_annotation_function.on_press(self, event)
    def on_drag(self, event): util_annotation_function.on_drag(self, event)
    def on_release(self, event): util_annotation_function.on_release(self, event)
    def update_annotation_listbox(self): util_annotation_function.update_annotation_listbox(self)
    def clear_annotation(self): util_annotation_function.clear_annotation(self)
    def undo_annotation(self, event=None): util_annotation_function.undo_annotation(self, event)
    def redo_annotation(self, event=None): util_annotation_function.redo_annotation(self, event)
    def load_folder(self,event=None): util_import_functions.load_folder(self,event)
    def load_image(self): util_image_functions.load_image(self)
    def prev_image(self,event=None): util_image_functions.prev_image(self,event)
    def load_annotation(self,event=None): util_import_functions.load_annotations(self,event)
    def next_image(self,event=None): util_image_functions.next_image(self,event)
    def on_mouse_wheel(self, event): util_zoom_functions.on_mouse_wheel(self, event)
    def update_image_size(self, fx, fy, scale): util_zoom_functions.update_image_size(self, fx, fy, scale)
    def download_annotations(self): util_import_functions.download_annotations(self)
    def save_annotation(self,event=None): util_export_functions.save_annotations(self,event)
    def change_annotation_type(self, event): util_annotation_function.change_annotation_type(self, event)
    def redraw_annotations(self): util_import_functions.redraw_annotations(self)
    def redraw_annotation(self, ann, w, h): return util_zoom_functions.redraw_annotation(self, ann, w, h)
    def label_annotation(self, event=None): util_import_functions.label_annotation(self, event)
    def on_annotation_selected(self, event): util_annotation_function.on_annotation_selected(self, event)
    def clamp_to_image_bounds(self, x, y): return util_annotation_function.clamp_to_image_bounds(self, x, y)
    def is_within_image_bounds(self, ann): return util_annotation_function.is_within_image_bounds(self, ann)
    def finalise_all(self, event=None):
        util_annotation_function.finalise_keypoints(self, event)
        util_annotation_function.finalise_polygon(self, event)
    def delete_specific_annotation(self, event=None): util_annotation_function.delete_specific_annotation(self, event)
    def show_listbox_menu(self, event): util_import_functions.show_listbox_menu(self, event)
    def go_to_image_by_name(self): util_image_functions.go_to_image_by_name(self)
    def save_image(self):util_image_functions.save_image(self)
    def redraw_temp_annotations(self):util_zoom_functions.redraw_temp_annotations(self)
    def toggle_crowd_label(self):util_annotation_function.toggle_crowd_label(self)
    def toggle_edit_mode(self):self.edit_mode = self.edit_toggle.get()
    def on_edit_press(self,event=None):util_annotation_function.on_edit_press(self,event)
    def on_edit_drag(self,event=None):util_annotation_function.on_edit_drag(self,event)
    def on_edit_release(self,event=None):util_annotation_function.on_edit_release(self,event)
    def toggle_lock_annotation(self):util_import_functions.toggle_lock_annotation(self)
    def import_coco(self):util_import_functions.import_coco(self)
    def import_yolo(self):util_import_functions.import_yolo(self)
    def import_pascal_voc(self):util_import_functions.import_pascal_voc(self)

    
