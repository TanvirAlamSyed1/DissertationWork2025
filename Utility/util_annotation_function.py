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
        self.current_freehand_points = []  # Start collecting fresh points
        self.current_annotation = self.canvas.create_line(
            self.start_x, self.start_y, self.start_x, self.start_y,
            fill="red", width=2, tags="temp_annotation"
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
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        # Draw live on canvas
        self.canvas.coords(
            self.current_annotation,
            *self.canvas.coords(self.current_annotation),
            cur_x, cur_y
        )

        # 🔥 Record normalized coordinates immediately
        x_img = (cur_x - self.image_x) / self.zoom_factor
        y_img = (cur_y - self.image_y) / self.zoom_factor
        self.current_freehand_points.extend([x_img, y_img])

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

    # 🛠 Convert from canvas coords to raw image coords
    start_img_x = (self.start_x - self.image_x) / self.zoom_factor
    start_img_y = (self.start_y - self.image_y) / self.zoom_factor
    end_img_x = (end_x - self.image_x) / self.zoom_factor
    end_img_y = (end_y - self.image_y) / self.zoom_factor

    annotation = None
    canvas_id = None
    print(start_img_x, start_img_y, end_img_x, end_img_y)

    if self.current_annotation_type == RectangleAnnotation:
        annotation = RectangleAnnotation(start_img_x, start_img_y, end_img_x, end_img_y)
        canvas_id = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red", tags="annotation")

    elif self.current_annotation_type == EllipseAnnotation:
        annotation = EllipseAnnotation(start_img_x, start_img_y, end_img_x, end_img_y)
        canvas_id = self.canvas.create_oval(self.start_x, self.start_y, end_x, end_y, outline="red", tags="annotation")

    elif self.current_annotation_type == FreehandAnnotation:
        if len(self.current_freehand_points) <= 4:
            return

        annotation = FreehandAnnotation(self.current_freehand_points)
        canvas_id = self.current_annotation


    elif self.current_annotation_type == CircleAnnotation:
        cx = (self.start_x - self.image_x) / self.zoom_factor
        cy = (self.start_y - self.image_y) / self.zoom_factor
        radius = min(abs(end_img_x - cx), abs(end_img_y - cy))
        x1 = cx - radius
        y1 = cy - radius
        x2 = cx + radius
        y2 = cy + radius
        annotation = CircleAnnotation(x1, y1, x2, y2)
        canvas_id = self.canvas.create_oval(self.start_x, self.start_y, end_x, end_y, outline="red", tags="annotation")

    # ❗ Important: Do NOT normalize here
    if annotation and not self.is_within_image_bounds(annotation):
        self.canvas.delete(canvas_id)
        return

    # Save annotation with raw pixel coordinates
    annotation.coordinates = annotation.normalise_coordinates(self.image.width, self.image.height)
    annotation.canvas_id = canvas_id
    self.annotations.append(annotation)
    self.update_annotation_listbox()
    self.redraw_annotations()

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
        annotation.coordinates = annotation.normalise_coordinates(self.image.width, self.image.height)

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
    """Clears all annotations, with a user confirmation."""
    if not self.annotations:
        return  # Nothing to clear

    confirm = messagebox.askyesno(
        "Confirm Clear",
        "Are you sure you want to clear all annotations? This action cannot be undone.",
        parent=self.controller
    )
    if not confirm:
        return  # User cancelled

    # Proceed with clearing
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

        # 🔥 Properly delete from canvas
        if isinstance(deleted_annotation.canvas_id, list):
            for cid in deleted_annotation.canvas_id:
                try:
                    self.canvas.delete(cid)
                except Exception as e:
                    print(f"Failed to delete canvas ID {cid}: {e}")
        else:
            try:
                self.canvas.delete(deleted_annotation.canvas_id)
            except Exception as e:
                print(f"Failed to delete canvas ID {deleted_annotation.canvas_id}: {e}")

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
        
        if getattr(annotation,"ismask",False):
            label += "[MASK]"

        # Add locked flag if applicable
        if getattr(annotation, "islocked", False):
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

    # Step 1: Reset all annotations to their default colour
    for annotation in self.annotations:
        if isinstance(annotation, KeypointAnnotation):
            for dot_id in annotation.canvas_id or []:
                self.canvas.itemconfig(dot_id, fill="green")
        elif isinstance(annotation, FreehandAnnotation):
            color = "purple" if getattr(annotation, "ismask", False) else "red"
            self.canvas.itemconfig(annotation.canvas_id, fill=color)
        elif isinstance(annotation, PolygonAnnotation):
            color = "purple" if getattr(annotation, "ismask", False) else "red"
            self.canvas.itemconfig(annotation.canvas_id, outline=color)
        else:
            color = "grey" if getattr(annotation, "islocked", False) else "red"
            self.canvas.itemconfig(annotation.canvas_id, outline=color)

    # Step 2: Now highlight the selected annotation
    if isinstance(selected_annotation, KeypointAnnotation):
        for dot_id in selected_annotation.canvas_id or []:
            self.canvas.itemconfig(dot_id, fill="blue")
    elif isinstance(selected_annotation, FreehandAnnotation):
        self.canvas.itemconfig(selected_annotation.canvas_id, fill="blue")
    elif isinstance(selected_annotation, PolygonAnnotation):
        self.canvas.itemconfig(selected_annotation.canvas_id, outline="blue")
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

def toggle_mask_annotation(self):
    index = self.selected_annotation_index
    if index is None or index >= len(self.annotations):
        return

    annotation = self.annotations[index]

    # Only allow for Polygon or Freehand
    if isinstance(annotation, (PolygonAnnotation, FreehandAnnotation)):
        annotation.ismask = not getattr(annotation, "ismask", False)  # Toggle it
        status = "✅ Marked as Mask" if annotation.ismask else "❌ Unmarked as Mask"
        print(f"{status} for annotation {index}")

        self.update_annotation_listbox()
        self.redraw_annotations()
    else:
        tk.messagebox.showwarning("Invalid Type", "Only Polygon or Freehand annotations can be used as masks.")
