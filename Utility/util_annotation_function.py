import tkinter as tk
from tkinter import messagebox
from Utility.annotation_classes import *

def clamp_to_image_bounds(self, x, y):
    """Restrict x and y to be within the zoomed image bounds on canvas."""
    if not hasattr(self, "image") or self.image is None:
        return x, y

    left = self.image_x
    top = self.image_y
    right = left + (self.image.width * self.zoom_factor)
    bottom = top + (self.image.height * self.zoom_factor)

    x = max(left, min(x, right))
    y = max(top, min(y, bottom))
    return x, y


def is_within_image_bounds(self, annotation):
    """Check if an annotation is entirely within zoomed image bounds on canvas."""
    if not self.image:
        return False

    zoomed_width = self.image.width * self.zoom_factor
    zoomed_height = self.image.height * self.zoom_factor

    left = self.image_x
    top = self.image_y
    right = left + zoomed_width
    bottom = top + zoomed_height

    # Rectangle or Circle — use bounding box
    if isinstance(annotation, RectangleAnnotation):
        x1, y1, x2, y2 = annotation.get_absolute_bounds()
        return left <= x1 <= right and left <= x2 <= right and top <= y1 <= bottom and top <= y2 <= bottom

    elif isinstance(annotation, EllipseAnnotation):
        x1, y1, x2, y2 = annotation.get_absolute_bounds()
        return left <= x1 <= right and left <= x2 <= right and top <= y1 <= bottom and top <= y2 <= bottom
    
    elif isinstance(annotation, CircleAnnotation):
        x1, y1, x2, y2 = annotation.get_absolute_bounds()
        return left <= x1 <= right and left <= x2 <= right and top <= y1 <= bottom and top <= y2 <= bottom

    elif isinstance(annotation, FreehandAnnotation):
        points = annotation.coordinates  # ← this is the fix!
        for i in range(0, len(points), 2):
            x, y = points[i], points[i+1]
            if not (left <= x <= right and top <= y <= bottom):
                return False
        return True
    elif isinstance(annotation, KeypointAnnotation):
        for x, y, v in annotation.coordinates:
            if not (left <= x <= right and top <= y <= bottom):
                return False
        return True
    elif isinstance(annotation, PolygonAnnotation):
        points = annotation.coordinates
        for i in range(0, len(points), 2):
            x, y = points[i], points[i+1]
            if not (left <= x <= right and top <= y <= bottom):
                return False
        return True

    return False  # fallback for unsupported types


def on_press(self, event):
    """Handles the start of an annotation."""
    
    raw_x = self.canvas.canvasx(event.x)
    raw_y = self.canvas.canvasy(event.y)
    self.start_x, self.start_y = self.clamp_to_image_bounds(raw_x, raw_y)

    if self.current_annotation_type == FreehandAnnotation:
        self.current_annotation = self.canvas.create_line(
            self.start_x, self.start_y, self.start_x, self.start_y,
            fill="red", width=2, tags="annotation"
        )

    elif self.current_annotation_type == KeypointAnnotation:
        # Clamp for drawing bounds
        x_clamped, y_clamped = self.clamp_to_image_bounds(raw_x, raw_y)

        # 🔥 Convert canvas position to raw image-space coordinates
        x_img = (x_clamped - self.image_x) / self.zoom_factor
        y_img = (y_clamped - self.image_y) / self.zoom_factor

        print(f"📌 Keypoint raw image coords: ({x_img:.2f}, {y_img:.2f})")

        self.keypoints.append((x_img, y_img, 2))

        # Draw on the canvas using zoomed position
        r = 3
        dot = self.canvas.create_oval(
            x_clamped - r, y_clamped - r, x_clamped + r, y_clamped + r,
            fill="green", outline="", tags="temp_annotation"
        )
        self.keypoint_canvas_ids.append(dot)


    elif self.current_annotation_type == PolygonAnnotation:
        x_clamped, y_clamped = self.clamp_to_image_bounds(raw_x, raw_y)

        # Convert to raw image coordinates (independent of zoom)
        x_img = (x_clamped - self.image_x) / self.zoom_factor
        y_img = (y_clamped - self.image_y) / self.zoom_factor

        self.polygon_points.extend([x_img, y_img])  # ✅ store image-space coords

        if len(self.polygon_points) >= 4:
            if self.polygon_preview_id:
                self.canvas.delete(self.polygon_preview_id)

            # Scale points to canvas coords for preview drawing
            scaled_points = [
                self.image_x + pt * self.zoom_factor if i % 2 == 0
                else self.image_y + pt * self.zoom_factor
                for i, pt in enumerate(self.polygon_points)
            ]

            self.polygon_preview_id = self.canvas.create_polygon(
                scaled_points,
                outline="blue",
                fill="",
                width=2,
                tags="temp_annotation"
            )

def on_drag(self, event):
    """Handles drawing while dragging."""
    raw_x = self.canvas.canvasx(event.x)
    raw_y = self.canvas.canvasy(event.y)
    cur_x, cur_y = self.clamp_to_image_bounds(raw_x, raw_y)


    if self.current_annotation_type == RectangleAnnotation:
        self.canvas.delete("temp_annotation")
        self.current_annotation = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline="red", tags="temp_annotation"
        )
    
    elif self.current_annotation_type == EllipseAnnotation:
        self.canvas.delete("temp_annotation")

        x1, y1 = self.start_x, self.start_y
        x2, y2 = cur_x, cur_y

        self.current_annotation = self.canvas.create_oval(
            x1, y1, x2, y2,
            outline="red", tags="temp_annotation"
        )

    
    elif self.current_annotation_type == FreehandAnnotation:
        cur_x, cur_y = self.clamp_to_image_bounds(cur_x, cur_y)
        self.canvas.coords(
            self.current_annotation,
            *self.canvas.coords(self.current_annotation),
            cur_x, cur_y
            )
    elif self.current_annotation_type == CircleAnnotation:
        self.canvas.delete("temp_annotation")

        cx, cy = self.start_x, self.start_y
        radius = min(abs(cur_x - cx), abs(cur_y - cy))

        x1 = cx - radius
        y1 = cy - radius
        x2 = cx + radius
        y2 = cy + radius

        self.current_annotation = self.canvas.create_oval(
            x1, y1, x2, y2,
            outline="red", tags="temp_annotation"
        )

def on_release(self, event):
    """Finalizes an annotation when the mouse is released."""
    raw_x = self.canvas.canvasx(event.x)
    raw_y = self.canvas.canvasy(event.y)
    end_x, end_y = self.clamp_to_image_bounds(raw_x, raw_y)
    if self.current_annotation_type == NoneType:
        return

    if self.current_annotation_type in [KeypointAnnotation, PolygonAnnotation]:
        return

    self.canvas.delete("temp_annotation")

    # ✅ Use zoomed dimensions for normalization
    zoomed_width = self.image.width * self.zoom_factor
    zoomed_height = self.image.height * self.zoom_factor

    annotation = None
    canvas_id = None

    if self.current_annotation_type == RectangleAnnotation:
        annotation = RectangleAnnotation(self.start_x, self.start_y, end_x, end_y)
        canvas_id = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red", tags="annotation")

    elif self.current_annotation_type == EllipseAnnotation:
        x1, y1 = self.start_x, self.start_y
        x2, y2 = end_x, end_y
        annotation = EllipseAnnotation(x1, y1, x2, y2)
        canvas_id = self.canvas.create_oval(x1, y1, x2, y2, outline="red", tags="annotation")

    elif self.current_annotation_type == FreehandAnnotation:
        points = self.canvas.coords(self.current_annotation)
        if len(points) <= 4:
            return
        annotation = FreehandAnnotation(points)
        canvas_id = self.current_annotation
    
    elif self.current_annotation_type == CircleAnnotation:
        cx, cy = self.start_x, self.start_y
        radius = min(abs(end_x - cx), abs(end_y - cy))

        x1 = cx - radius
        y1 = cy - radius
        x2 = cx + radius
        y2 = cy + radius

        annotation = CircleAnnotation(x1, y1, x2, y2)
        canvas_id = self.canvas.create_oval(x1, y1, x2, y2, outline="red", tags="annotation")


    # ❌ Skip invalid annotations
    if annotation and not self.is_within_image_bounds(annotation):
        self.canvas.delete(canvas_id)
        return

    # ✅ Normalize to zoomed image size
    annotation.coordinates = annotation.normalize_coordinates(zoomed_width, zoomed_height)
    annotation.canvas_id = canvas_id
    self.annotations.append(annotation)
    self.update_annotation_listbox()

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

    x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
    dx = (x - self.drag_start[0]) / self.image.width
    dy = (y - self.drag_start[1]) / self.image.height

    # Prepare updated coords
    ann = self.selected_annotation
    if isinstance(ann, KeypointAnnotation):
        preview_coords = [(x + dx, y + dy, v) for x, y, v in ann.coordinates]
        preview = KeypointAnnotation(preview_coords)
    else:
        preview_coords = [c + dx if i % 2 == 0 else c + dy for i, c in enumerate(ann.coordinates)]
        preview = type(ann)(*preview_coords)
        preview.coordinates = preview_coords

    if self.is_within_image_bounds(preview):
        # ✅ Move is valid → update
        ann.coordinates = preview_coords
        self.drag_start = (x, y)
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


def finalise_polygon(self, event=None):
    if self.current_annotation_type != PolygonAnnotation:
        print("❌ Not in Polygon mode.")
        return

    if len(self.polygon_points) < 6:
        print("⚠️ Polygon needs at least 3 points.")
        return

    annotation = PolygonAnnotation(self.polygon_points)
    if self.is_within_image_bounds(annotation):
        # ✅ Convert image-space polygon points to canvas coords
        scaled_points = [
            self.image_x + pt * self.zoom_factor if i % 2 == 0
            else self.image_y + pt * self.zoom_factor
            for i, pt in enumerate(self.polygon_points)
        ]

        canvas_id = self.canvas.create_polygon(
            scaled_points,
            outline="blue",
            fill="",
            width=2,
            tags="annotation"
        )
        annotation.canvas_id = canvas_id

        # ✅ Normalize using raw image dimensions (not zoomed!)
        annotation.coordinates = annotation.normalize_coordinates(self.image.width, self.image.height)

        self.annotations.append(annotation)
        self.update_annotation_listbox()
        print("✅ Polygon finalized and added.")

    else:
        print("❌ Polygon out of bounds.")

    if self.polygon_preview_id:
        self.canvas.delete(self.polygon_preview_id)
        self.polygon_preview_id = None
    self.polygon_points = []


def finalise_keypoints(self, event=None):
    if self.current_annotation_type != KeypointAnnotation:
        return

    if not self.keypoints:
        return

    normalized_keypoints = []

    for x, y, v in self.keypoints:
        x_norm = x / self.image.width
        y_norm = y / self.image.height
        normalized_keypoints.append((x_norm, y_norm, v))

    annotation = KeypointAnnotation(normalized_keypoints)
    print("✅ Saving normalized keypoints:", normalized_keypoints)

    if self.is_within_image_bounds(annotation):
        annotation.canvas_id = self.keypoint_canvas_ids.copy()
        self.annotations.append(annotation)
        self.redraw_annotations()
        self.update_annotation_listbox()
    else:
        print("❌ Keypoints out of bounds. Not added.")

    for dot_id in self.keypoint_canvas_ids:
        self.canvas.itemconfig(dot_id, tags="annotation")
    
    self.canvas.delete("temp_annotation")
    self.keypoints = []
    self.keypoint_canvas_ids = []

def clear_annotation(self):
    """Clears all annotations."""
    self.canvas.delete("annotation")
    self.annotations.clear()
    self.undone_annotations.clear()
    self.update_annotation_listbox()

def undo_annotation(self, event=None):
    """Undoes the last annotation action."""
    if self.annotations:
        self.undone_annotations.append(self.annotations.pop())

    self.redraw_annotations()
    self.update_annotation_listbox()

def delete_specific_annotation(self, event=None):
    def do_delete():
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this annotation?",
            parent=self.controller
        )
        if not confirm:
            return

        index = self.selected_annotation_index

        if index is None or index >= len(self.annotations):
            return

        deleted_annotation = self.annotations.pop(index)
        self.undone_annotations.append(deleted_annotation)

        if isinstance(deleted_annotation.canvas_id, list):
            for canvas_id in deleted_annotation.canvas_id:
                self.canvas.delete(canvas_id)
        else:
            self.canvas.delete(deleted_annotation.canvas_id)

        self.update_annotation_listbox()

    self.after(10, do_delete)

def redo_annotation(self, event=None):
    """Redoes the last undone annotation."""
    if self.undone_annotations:
        self.annotations.append(self.undone_annotations.pop())

    self.redraw_annotations()
    self.update_annotation_listbox()


def update_annotation_listbox(self):
    """Updates the Listbox with annotation types and labels."""
    self.annotation_listbox.delete(0, tk.END)

    print("📋 Updating listbox...")  # Debug

    for index, annotation in enumerate(self.annotations):
        if annotation.annotation_type == "Keypoint":
            label = f"{index + 1}. Keypoints ({len(annotation.coordinates)} points): {annotation.label}"
        else:
            label = f"{index + 1}. {annotation.annotation_type}: {annotation.label}"

        # Add crowd flag if applicable
        if getattr(annotation, "iscrowd", 0):
            label += " [CROWD]"

        # Add locked flag if applicable
        if getattr(annotation, "locked", False):
            label += " [LOCKED]"

        self.annotation_listbox.insert(tk.END, label)

    self.annotation_listbox.update_idletasks()  # Forces UI update
    self.annotation_listbox.bind("<<ListboxSelect>>", self.on_annotation_selected)

def on_annotation_selected(self, event):
    """Highlights the selected annotation on the canvas."""
    selected_index = self.annotation_listbox.curselection()
    if not selected_index:
        return

    selected_index = selected_index[0]
    selected_annotation = self.annotations[selected_index]

    # Reset all annotations to default color
    for annotation in self.annotations:
        if isinstance(annotation, FreehandAnnotation):
            self.canvas.itemconfig(annotation.canvas_id, fill="red")
        elif isinstance(annotation, KeypointAnnotation):
            for dot_id in annotation.canvas_id or []:
                self.canvas.itemconfig(dot_id, fill="green")  # Reset to default green
        elif isinstance(annotation, PolygonAnnotation):
            self.canvas.itemconfig(annotation.canvas_id, outline="red")
        else:
            self.canvas.itemconfig(annotation.canvas_id, outline="red")

    # Highlight the selected annotation
    if isinstance(selected_annotation, FreehandAnnotation):
        self.canvas.itemconfig(selected_annotation.canvas_id, fill="blue")
    elif isinstance(selected_annotation, KeypointAnnotation):
        for dot_id in selected_annotation.canvas_id or []:
            self.canvas.itemconfig(dot_id, fill="blue")  # Highlight all keypoints in blue
    elif isinstance(selected_annotation, PolygonAnnotation):
        self.canvas.itemconfig(selected_annotation.canvas_id,fill="",outline="blue")
    else:
        self.canvas.itemconfig(selected_annotation.canvas_id, outline="blue")


def change_annotation_type(self, event):
    """Changes the annotation type based on user selection."""
    selected = self.annotation_type.get()  # ✅ Always returns a string
    if selected in self.annotation_classes:
        self.current_annotation_type = self.annotation_classes[selected]

def toggle_crowd_label(self):
    index = self.selected_annotation_index
    if index is None or index >= len(self.annotations):
        return

    annotation = self.annotations[index]
    annotation.iscrowd = 1 if getattr(annotation, "iscrowd", 0) == 0 else 0  # toggle it
    print(f"🔁 Toggled iscrowd for annotation {index} → {annotation.iscrowd}")

    self.update_annotation_listbox()
