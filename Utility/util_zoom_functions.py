from PIL import ImageTk
import tkinter as tk
from Utility.annotation_classes import *

def on_mouse_wheel(self, event):
    """Handles zooming in and out while keeping the cursor at the same position."""

    # Get mouse position relative to the canvas
    mouse_x = self.canvas.canvasx(event.x)
    mouse_y = self.canvas.canvasy(event.y)

    # Get the bounding box of the image
    bbox = self.canvas.bbox("image")
    if not bbox:
        return  # Prevents crashes if no image is loaded

    # Calculate the focus point relative to the image size
    focus_x = (mouse_x - bbox[0]) / (bbox[2] - bbox[0])
    focus_y = (mouse_y - bbox[1]) / (bbox[3] - bbox[1])

    # Determine zoom direction
    zoom_in = event.delta > 0
    scale_factor = 1.1 if zoom_in else (1 / 1.1)

    # Prevent excessive zooming out
    if not zoom_in and self.zoom_factor <= 1.0:
        return
    # Update zoom factor
    self.zoom_factor = max(self.zoom_factor * scale_factor, 1.0)
    # Apply updated zoom
    self.update_image_size(focus_x, focus_y, scale_factor)

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

    # ✅ Redraw temporary annotations (in-progress keypoints, polygons, etc.)
    self.redraw_temp_annotations()

        
def redraw_temp_annotations(self):
    """Redraw in-progress keypoints or polygons during zoom."""
    self.canvas.delete("temp_annotation")

    zoomed_width = self.image.width * self.zoom_factor
    zoomed_height = self.image.height * self.zoom_factor

    if self.current_annotation_type == KeypointAnnotation:
        for x_norm, y_norm, _ in self.keypoints:
            x = x_norm * zoomed_width
            y = y_norm * zoomed_height
            r = 3
            self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="green", outline="", tags="temp_annotation"
            )

    elif self.current_annotation_type == PolygonAnnotation and len(self.polygon_points) >= 4:
        scaled_points = []
        for i in range(0, len(self.polygon_points), 2):
            x = self.polygon_points[i] * zoomed_width
            y = self.polygon_points[i+1] * zoomed_height
            scaled_points.extend([x, y])

        self.polygon_preview_id = self.canvas.create_polygon(
            scaled_points, outline="blue", fill="", width=2, tags="temp_annotation"
        )



def redraw_annotation(self, annotation, new_width, new_height):
    """Redraws a single annotation at the correct scaled position."""

    ann_type = annotation.annotation_type
    rel_coords = annotation.coordinates
    new_width = int(self.image.width * self.zoom_factor)
    new_height = int(self.image.height * self.zoom_factor)


    if isinstance(annotation, RectangleAnnotation):
        x1, y1, x2, y2 = [rel_coords[i] * new_width if i % 2 == 0 else rel_coords[i] * new_height for i in range(4)]
        canvas_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="annotation")
        annotation.canvas_id = canvas_id

    elif isinstance(annotation, EllipseAnnotation):
        x1 = rel_coords[0] * new_width
        y1 = rel_coords[1] * new_height
        x2 = rel_coords[2] * new_width
        y2 = rel_coords[3] * new_height
        canvas_id = self.canvas.create_oval(x1, y1, x2, y2, outline="red", tags="annotation")
        annotation.canvas_id = canvas_id

    elif isinstance(annotation, FreehandAnnotation):
        if len(rel_coords) < 4:
            return

        scaled_points = [
            rel_coords[i] * new_width if i % 2 == 0 else rel_coords[i] * new_height
            for i in range(len(rel_coords))
        ]
        canvas_id = self.canvas.create_line(*scaled_points, fill="red", width=2, tags="annotation")
        annotation.canvas_id = canvas_id
    
    elif isinstance(annotation, KeypointAnnotation):
        dot_ids = []
        for x_norm, y_norm, v in annotation.coordinates:
            x = x_norm * new_width  # ✅ correct — new_width is zoomed width
            y = y_norm * new_height
            r = 1
            dot = self.canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill="green", outline="", tags="annotation"
            )
            dot_ids.append(dot)
        annotation.canvas_id = dot_ids

    elif isinstance(annotation, PolygonAnnotation):
        if len(rel_coords) >= 6:
            scaled_points = [
                rel_coords[i] * new_width if i % 2 == 0 else rel_coords[i] * new_height
                for i in range(len(rel_coords))
            ]
            canvas_id = self.canvas.create_polygon(
                scaled_points,
                outline="red",
                fill="",
                width=2,
                tags="annotation"
            )
            annotation.canvas_id = canvas_id


    return annotation







