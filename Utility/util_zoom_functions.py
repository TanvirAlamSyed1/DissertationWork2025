from PIL import ImageTk
import tkinter as tk
from Utility.annotation_classes import *

def on_mouse_wheel(self, event):
    """Handles zooming in and out while keeping the cursor at the same position."""
    mouse_x = self.canvas.canvasx(event.x)
    mouse_y = self.canvas.canvasy(event.y)

    bbox = self.canvas.bbox("image")
    if not bbox:
        return

    focus_x = (mouse_x - bbox[0]) / (bbox[2] - bbox[0])
    focus_y = (mouse_y - bbox[1]) / (bbox[3] - bbox[1])

    zoom_in = event.delta > 0
    scale_factor = 1.1 if zoom_in else (1 / 1.1)

    if not zoom_in and self.zoom_factor <= 1.0:
        return

    self.zoom_factor = max(self.zoom_factor * scale_factor, 1.0)
    self.update_image_size(focus_x, focus_y, scale_factor)

    # ✅ Re-draw live keypoints AFTER zoom, don't finalize them
    if (self.current_annotation_type in [KeypointAnnotation, PolygonAnnotation] and (self.keypoints or self.polygon_points)):
        self.redraw_temp_annotations()

        

    
def redraw_temp_annotations(self):
    """Redraws in-progress keypoints and polygon using zoomed coords."""
    self.canvas.delete("temp_annotation")

    # 🟢 Keypoints
    for x_img, y_img, v in self.keypoints:
        x_canvas = self.image_x + (x_img * self.zoom_factor)
        y_canvas = self.image_y + (y_img * self.zoom_factor)
        r = 3
        self.canvas.create_oval(
            x_canvas - r, y_canvas - r, x_canvas + r, y_canvas + r,
            fill="green", outline="", tags="temp_annotation"
        )

    # 🔵 Polygon
    if len(self.polygon_points) >= 4:
        scaled_points = [
            self.image_x + pt * self.zoom_factor if i % 2 == 0
            else self.image_y + pt * self.zoom_factor
            for i, pt in enumerate(self.polygon_points)
        ]
        self.polygon_preview_id = self.canvas.create_polygon(
            scaled_points,
            outline="blue", fill="", width=2, tags="temp_annotation"
        )




def update_image_size(self, focus_x=None, focus_y=None, scale_factor=1.0):
    """Resizes the image and adjusts annotations accordingly while maintaining zoom focus."""

    if not self.image:
        return

    # Calculate new image dimensions
    new_width = int(self.image.width * self.zoom_factor)
    new_height = int(self.image.height * self.zoom_factor)
    resized_image = self.image.resize((new_width, new_height))
    self.photo = ImageTk.PhotoImage(resized_image)

    # Update canvas scroll region
    self.canvas.config(scrollregion=(0, 0, new_width, new_height))

    # Redraw image
    self.canvas.delete("image")
    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

    # Maintain cursor-centered zoom focus
    if focus_x is not None and focus_y is not None:
        bbox = self.canvas.bbox("image")
        if bbox:
            new_x_scroll = focus_x * (bbox[2] - bbox[0]) - (self.canvas.winfo_width() / 2)
            new_y_scroll = focus_y * (bbox[3] - bbox[1]) - (self.canvas.winfo_height() / 2)

            x_scroll = max(0, min(new_x_scroll / (bbox[2] - bbox[0]), 1.0))
            y_scroll = max(0, min(new_y_scroll / (bbox[3] - bbox[1]), 1.0))

            self.canvas.xview_moveto(x_scroll)
            self.canvas.yview_moveto(y_scroll)

    # Redraw finalized annotations
    self.canvas.delete("annotation")
    for annotation in self.annotations:
        self.redraw_annotation(annotation, new_width, new_height)
    # Redraw temp annotations (e.g., in-progress polygon)
    if hasattr(self, "current_annotation_type"):
        if self.current_annotation_type in [KeypointAnnotation, PolygonAnnotation]:
            self.redraw_temp_annotations()



def redraw_annotation(self, annotation, new_width, new_height):
    annotation.draw_annotation(self.canvas, new_width, new_height)
    return annotation








