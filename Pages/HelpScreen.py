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

        help_text = """
        📘 Welcome to the Image Annotation Tool!

        ---

        🔹 GETTING STARTED
        - Use 'File > Load Images' to select a folder of images.
        - Images will appear one by one for annotation.

        ---

        ✏️ ANNOTATION TOOLS
        - Rectangle: Draw bounding boxes.
        - Ellipse: Draw elliptical annotations.
        - Polygon: Click to create points, double-click to close.
        - Freehand: Hold and draw like a pen (used for masks).
        - Keypoints: Place landmarks on the image.

        Use the left toolbar to switch tools.

        ---

        💾 SAVING & LOADING
        - Annotations are saved automatically in a JSON format.
        - You can reload them when reopening the image.

        ---

        📤 EXPORT OPTIONS
        - COCO: Object detection + segmentation (polygon)
        - YOLO: Object detection (bounding boxes)
        - Pascal VOC: XML-based format
        - Mask: PNG mask images for segmentation
        - JSON: Raw full annotation backup

        Use 'Download All Annotations' to export.

        ---

        ⌨️ KEYBOARD SHORTCUTS
        - Ctrl + Z: Undo last annotation
        - Ctrl + Y: Redo
        - Delete / Backspace: Delete selected annotation
        - Ctrl + S: Save current annotations
        - Ctrl + O: Open an image
        - Ctrl + E: Export annotations
        - Ctrl + M: Export masks
        - Ctrl + H: Show help
        - Ctrl + D: Finalise Polygon Annotation / Keypoints
        - ← → : Navigate between images
        - Esc: Cancel current annotation or exit tool

        ---

        🧠 TIPS
        - Right-click on canvas to delete the selected annotation.
        - Use zoom controls at bottom to zoom in/out.
        - Use undo/redo to correct mistakes.
        - Use the annotation list (right sidebar) to navigate/edit annotations.

        Enjoy annotating!
        """

        
        text_widget.insert("1.0", help_text)
        text_widget.config(state="disabled")
        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = tk.Button(
            self,
            text="Go to the Main Page",
            command=lambda: controller.show_frame(MainPage),
        )
        switch_window_button.pack(side="bottom")
        