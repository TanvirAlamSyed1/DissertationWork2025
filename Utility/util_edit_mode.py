import tkinter as tk
from tkinter import messagebox
from Utility.annotation_classes import *

def toggle_edit_mode(self):
    self.edit_mode = self.edit_toggle.get()

def on_edit_press(self, event):
    if not self.edit_mode or not self.image:
        return

    x = self.canvas.canvasx(event.x)
    y = self.canvas.canvasy(event.y)
    clicked_items = self.canvas.find_overlapping(x, y, x, y)

    if not clicked_items:
        print("❌ No canvas items under cursor.")
        return

    # Reverse order = topmost item first
    for item in reversed(clicked_items):
        # Only check items tagged as "annotation"
        tags = self.canvas.gettags(item)
        if "annotation" not in tags:
            continue

        for annotation in self.annotations:
            ids = annotation.canvas_id if isinstance(annotation.canvas_id, list) else [annotation.canvas_id]
            if item in ids:
                if getattr(annotation, "locked", False):
                    print("🔒 Locked annotation selected but not editable.")
                    return
                self.selected_annotation = annotation
                self.drag_start = (x, y)
                print(f"✅ Selected annotation: {annotation.annotation_type}")
                return

    print("⚠️ No matching annotation found under cursor.")

def on_edit_drag(self, event):
    if not self.selected_annotation or not self.image:
        return

    x_canvas, y_canvas = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
    dx = x_canvas - self.drag_start[0]
    dy = y_canvas - self.drag_start[1]

    ann = self.selected_annotation

    if isinstance(ann, KeypointAnnotation):
        # Work in absolute (canvas) coords
        preview_coords = [(x * self.image.width * self.zoom_factor + dx,
                           y * self.image.height * self.zoom_factor + dy,
                           v) for x, y, v in ann.coordinates]

        # After move, re-normalize
        new_coords = [( (x - self.image_x) / (self.image.width * self.zoom_factor),
                        (y - self.image_y) / (self.image.height * self.zoom_factor),
                        v) for x, y, v in preview_coords]

        preview = KeypointAnnotation(new_coords)

    elif isinstance(ann, (RectangleAnnotation, EllipseAnnotation, CircleAnnotation)):
        coords = ann.coordinates
        # convert normalized coords → absolute
        abs_coords = [coords[i] * (self.image.width if i % 2 == 0 else self.image.height) * self.zoom_factor for i in range(len(coords))]
        # shift by mouse
        moved_coords = [abs_coords[i] + (dx if i % 2 == 0 else dy) for i in range(len(abs_coords))]
        # re-normalize
        new_coords = [(moved_coords[i] - (self.image_x if i % 2 == 0 else self.image_y)) / (self.image.width * self.zoom_factor) for i in range(len(moved_coords))]

        if isinstance(ann, RectangleAnnotation):
            preview = RectangleAnnotation(*new_coords)
        elif isinstance(ann, EllipseAnnotation):
            preview = EllipseAnnotation(*new_coords)
        elif isinstance(ann, CircleAnnotation):
            preview = CircleAnnotation(*new_coords)

        preview.coordinates = new_coords

    elif isinstance(ann, (PolygonAnnotation, FreehandAnnotation)):
        coords = ann.coordinates
        abs_coords = [coords[i] * (self.image.width if i % 2 == 0 else self.image.height) * self.zoom_factor for i in range(len(coords))]
        moved_coords = [abs_coords[i] + (dx if i % 2 == 0 else dy) for i in range(len(abs_coords))]
        new_coords = [(moved_coords[i] - (self.image_x if i % 2 == 0 else self.image_y)) / (self.image.width * self.zoom_factor) for i in range(len(moved_coords))]

        if isinstance(ann, PolygonAnnotation):
            preview = PolygonAnnotation(new_coords)
        else:
            preview = FreehandAnnotation(new_coords)
        preview.coordinates = new_coords

    else:
        return

    if self.is_within_image_bounds(preview):
        ann.coordinates = new_coords
        self.drag_start = (x_canvas, y_canvas)
        self.redraw_annotations()
    else:
        print("🚫 Move rejected: annotation would go out of bounds.")

def on_edit_release(self, event):
    if self.selected_annotation:
        # Restore default outline color
        if isinstance(self.selected_annotation.canvas_id, list):
            for cid in self.selected_annotation.canvas_id:
                self.canvas.itemconfig(cid, outline="blue" if isinstance(self.selected_annotation, KeypointAnnotation) else "red")
        else:
            self.canvas.itemconfig(self.selected_annotation.canvas_id, outline="red")
        
    self.selected_annotation = None
    self.drag_start = None