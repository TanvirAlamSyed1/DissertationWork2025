from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import ttk

def zoom_in(self):
    self.zoom_factor *= 1.1
    self.update_image_size()

def zoom_out(self):
    self.zoom_factor = max(1.0, self.zoom_factor / 1.1)  # Prevent zooming out too much
    self.update_image_size()

def on_mouse_wheel(self, event):
    # Get the mouse position relative to the canvas
    mouse_x = self.canvas.canvasx(event.x)
    mouse_y = self.canvas.canvasy(event.y)

    # Get current scroll position as a fraction
    x_fraction = self.canvas.xview()[0]
    y_fraction = self.canvas.yview()[0]

    # Determine zoom direction
    if event.delta > 0:  # Zoom in
        scale_factor = 1.1
    else:  # Zoom out
        if self.zoom_factor <= 1.0:  # Prevent zooming out beyond original size
            return
        scale_factor = 1 / 1.1

    # Apply zoom
    self.zoom_factor *= scale_factor
    if self.zoom_factor < 1.0:  # Prevent zooming out too much
        self.zoom_factor = 1.0

    self.update_image_size(mouse_x, mouse_y, x_fraction, y_fraction)

def update_image_size(self, mouse_x, mouse_y, x_fraction, y_fraction):
    if self.image:
        # Resize the image while ensuring it doesn’t shrink beyond original size
        new_width = int(self.image.width * self.zoom_factor)
        new_height = int(self.image.height * self.zoom_factor)

        resized_image = self.image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(resized_image)

        # Set new scroll region
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))

        # Adjust scroll position to keep the cursor in place
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        new_x_fraction = (mouse_x / new_width) - (canvas_width / (2 * new_width))
        new_y_fraction = (mouse_y / new_height) - (canvas_height / (2 * new_height))

        self.canvas.xview_moveto(new_x_fraction)
        self.canvas.yview_moveto(new_y_fraction)

        # Update canvas image
        self.canvas.delete("image")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

def update_image_size(self, mouse_x=None, mouse_y=None, x_fraction=None, y_fraction=None):
    if self.image:
        # Resize the image while ensuring it doesn’t shrink beyond original size
        new_width = int(self.image.width * self.zoom_factor)
        new_height = int(self.image.height * self.zoom_factor)

        resized_image = self.image.resize((new_width, new_height))
        self.photo = ImageTk.PhotoImage(resized_image)

        # Set new scroll region
        self.canvas.config(scrollregion=(0, 0, new_width, new_height))

        # Adjust scroll position to keep the cursor in place if mouse_x and mouse_y are provided
        if mouse_x is not None and mouse_y is not None:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            new_x_fraction = (mouse_x / new_width) - (canvas_width / (2 * new_width))
            new_y_fraction = (mouse_y / new_height) - (canvas_height / (2 * new_height))

            self.canvas.xview_moveto(new_x_fraction)
            self.canvas.yview_moveto(new_y_fraction)
        elif x_fraction is not None and y_fraction is not None:
            # Adjust scroll position based on provided fractions
            self.canvas.xview_moveto(x_fraction)
            self.canvas.yview_moveto(y_fraction)

        # Update canvas image
        self.canvas.delete("image")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

        # Clear old annotations and redraw them at new scaled positions
        self.canvas.delete("annotation")
        for ann_type, ann_data in self.annotations:
            if ann_type == "Rectangle":
                rel_coords = ann_data
                scaled_coords = [
                    rel_coords[0] * new_width,
                    rel_coords[1] * new_height,
                    rel_coords[2] * new_width,
                    rel_coords[3] * new_height
                ]
                self.canvas.create_rectangle(*scaled_coords, outline="red", tags="annotation")
            elif ann_type == "Circle":
                rel_coords = ann_data
                scaled_coords = [
                    rel_coords[0] * new_width,
                    rel_coords[1] * new_height,
                    rel_coords[2] * new_width,
                    rel_coords[3] * new_height
                ]
                radius = ((scaled_coords[2] - scaled_coords[0]) ** 2 +
                          (scaled_coords[3] - scaled_coords[1]) ** 2) ** 0.5
                self.canvas.create_oval(
                    scaled_coords[0] - radius, scaled_coords[1] - radius,
                    scaled_coords[0] + radius, scaled_coords[1] + radius,
                    outline="red", tags="annotation"
                )
            elif ann_type == "Freehand":
                # Scale each point in the freehand drawing
                points = ann_data
                scaled_points = []
                for i in range(0, len(points), 2):
                    scaled_points.append(points[i] * new_width)
                    scaled_points.append(points[i + 1] * new_height)
                self.canvas.create_line(*scaled_points, fill="red", width=2, tags="annotation")