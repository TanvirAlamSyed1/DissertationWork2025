# Importing the tkinter module
import tkinter as tk
# Styling the GUI
from tkinter import ttk
#Importing the next page
from Pages.MainScreen import MainPage
class HelpPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #Welcome label
        help_label = tk.Label(self, text="Help & User Guide", font=("Arial", 24))
        help_label.pack(pady=50)
        #Description
        text_widget = tk.Text(self, wrap="word", padx=10, pady=10)
        text_widget.pack(expand=True, fill="both")

        help_content = """
            ✨ Welcome to the Image Annotation Tool!

            ----------------------------

            🔹 GETTING STARTED
            1. Click 'Load Folder' to select a folder containing your images.
            2. Images will display one at a time for you to annotate.

            ----------------------------

            🖊️ ANNOTATION TOOLS (Left Toolbar)
            - Rectangle: Draw boxes around objects.
            - Ellipse: Draw elliptical shapes.
            - Circle: Draw perfect circles.
            - Polygon: Click points around a shape, press Ctrl+D when done.
            - Freehand: Draw freely with the mouse.
            - Keypoints: Mark important points, press Ctrl+D when done.

            **Tip:** Switch tools anytime from the 'Annotation Type' dropdown.

            ----------------------------

            📂 SAVING & LOADING
            - Save current annotations: Click 'Save Annotations'.
            - Load previous annotations: Click 'Load Annotations'.
            - When loading annotations, this application always priorities JSON. If you have an alternate format (COCO, YOLO ect), The application will give you the option to load it in.
            - Export all annotations: Use 'Download All Annotations' and select the format you need.
            - To save the annotated image as an image, use 'Export Annotated Image'

            ----------------------------

            📤 EXPORT FORMATS
            - **COCO**: Object detection & segmentation
            - **YOLO**: Object detection (bounding boxes)
            - **Pascal VOC**: XML format for object detection
            - **Masks**: Create semantic segmentation PNG masks
            - **JSON**: Full annotation backup

            ----------------------------

            📈 KEYBOARD SHORTCUTS
            - Ctrl+F : Load image folder
            - Ctrl+L : Load annotations
            - Ctrl+S : Save/export annotations
            - Ctrl+Z : Undo last action
            - Ctrl+Y : Redo last undone action
            - Ctrl+D : Finalize polygon or keypoints
            - Ctrl+N : Next image
            - Ctrl+P : Previous image

            ----------------------------

            🧐 USEFUL TIPS
            - Right-click an annotation in the sidebar to rename, lock, or delete it.
            - To turn your polygon or freehand drawing into a mask, right-click on the annotation in the listbox, and the option will appear. 
            - Zoom in/out with mouse scroll.
            - Undo/redo mistakes anytime.
            - Use 'Edit Mode' to move annotations after creating them.

            ----------------------------

            Enjoy using the tool!
            """

        
        text_widget.insert("1.0", help_content)
        text_widget.config(state="disabled")
        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = tk.Button(
            self,
            text="Go to the Main Page",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.pack(side="bottom")
        