from PIL import Image, ImageTk
import tkinter as tk
from Utility.annotation_classes import RectangleAnnotation, CircleAnnotation, FreehandAnnotation

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
    self.zoom_factor *= scale_factor
    self.zoom_factor = max(self.zoom_factor, 1.0)  # Ensure it doesn't go below 1.0

    # Apply updated zoom
    self.update_image_size(focus_x, focus_y, scale_factor)

def update_image_size(self, focus_x=None, focus_y=None, scale_factor=1.0):
    """Resizes the image and adjusts annotations accordingly while maintaining zoom focus."""

    if not self.image:
        return

    # Get the current scroll position BEFORE zooming
    x_scroll, y_scroll = self.canvas.xview(), self.canvas.yview()

    # Calculate new dimensions while preserving aspect ratio
    new_width = int(self.image.width * self.zoom_factor)
    new_height = int(self.image.height * self.zoom_factor)
    resized_image = self.image.resize((new_width, new_height))

    self.photo = ImageTk.PhotoImage(resized_image)

    # Update canvas scroll region
    self.canvas.config(scrollregion=(0, 0, new_width, new_height))

    # Update canvas image
    self.canvas.delete("image")
    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

    # Adjust scrollbars to maintain focus on the cursor position
    if focus_x is not None and focus_y is not None:
        bbox = self.canvas.bbox("image")
        if bbox:
            # Compute new scroll position to keep the cursor focus
            new_x_scroll = focus_x * (bbox[2] - bbox[0]) - (self.canvas.winfo_width() / 2)
            new_y_scroll = focus_y * (bbox[3] - bbox[1]) - (self.canvas.winfo_height() / 2)

            # Convert to valid scroll fraction (0-1 range) with clamping
            x_scroll = max(0, min(new_x_scroll / (bbox[2] - bbox[0]), 1.0))
            y_scroll = max(0, min(new_y_scroll / (bbox[3] - bbox[1]), 1.0))

            self.canvas.xview_moveto(x_scroll)
            self.canvas.yview_moveto(y_scroll)

    # Clear old annotations and redraw them at new scaled positions
    self.canvas.delete("annotation")
    for annotation in self.annotations:
        self.redraw_annotation(annotation, new_width, new_height)


def redraw_annotation(self, annotation, new_width, new_height):
    """Redraws a single annotation at the correct scaled position."""

    ann_type = annotation.annotation_type  # ✅ Use object attributes
    rel_coords = annotation.coordinates  # ✅ Use object attributes

    if isinstance(annotation, RectangleAnnotation):
        x1, y1, x2, y2 = [rel_coords[i] * new_width if i % 2 == 0 else rel_coords[i] * new_height for i in range(4)]
        canvas_id = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="annotation")

    elif isinstance(annotation, CircleAnnotation):
        cx, cy, r = rel_coords
        cx *= new_width
        cy *= new_height
        r *= new_width  # Scale radius based on width

        canvas_id = self.canvas.create_oval(
            cx - r, cy - r,
            cx + r, cy + r,
            outline="red", tags="annotation"
        )

    elif isinstance(annotation, FreehandAnnotation):
        if len(rel_coords) < 4:
            return  # Not enough points for a freehand stroke

        scaled_points = [
            rel_coords[i] * new_width if i % 2 == 0 else rel_coords[i] * new_height
            for i in range(len(rel_coords))
        ]
        canvas_id = self.canvas.create_line(*scaled_points, fill="red", width=2, tags="annotation")
    
    annotation.canvas_id = canvas_id
    return annotation






