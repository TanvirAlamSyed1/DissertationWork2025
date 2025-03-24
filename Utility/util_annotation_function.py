import tkinter as tk
from tkinter import messagebox
from Utility.annotation_classes import *

def clamp_to_image_bounds(self, x, y):
    """Restrict x and y to be within the image bounds on canvas."""
    if not hasattr(self, "image") or self.image is None:
        return x, y  # Fallback in case image is not set

    left = self.image_x
    top = self.image_y
    right = left + self.image.width
    bottom = top + self.image.height

    x = max(left, min(x, right))
    y = max(top, min(y, bottom))
    return x, y

    return x, y

def is_within_image_bounds(self, annotation):
    """Check if an annotation is entirely within image bounds on canvas."""
    if not self.image:
        return False

    left = self.image_x
    top = self.image_y
    right = left + self.image.width
    bottom = top + self.image.height

    # Rectangle or Circle — use bounding box
    if isinstance(annotation, RectangleAnnotation):
        x1, y1, x2, y2 = annotation.get_absolute_bounds()
        return left <= x1 <= right and left <= x2 <= right and top <= y1 <= bottom and top <= y2 <= bottom

    elif isinstance(annotation, EllipseAnnotation):
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
    
    if self.current_annotation_type == KeypointAnnotation:
        print(f"Current annotation type: {self.current_annotation_type}")
        x, y = self.clamp_to_image_bounds(raw_x, raw_y)

        self.keypoints.append((x, y, 2))

        r = 3
        dot = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill="green", outline="", tags="temp_annotation"
        )
        self.keypoint_canvas_ids.append(dot)

        print(f"Placed keypoint at: ({x:.2f}, {y:.2f})")
    if self.current_annotation_type == PolygonAnnotation:
        x, y = self.clamp_to_image_bounds(raw_x, raw_y)
        self.polygon_points.extend([x, y])

        if len(self.polygon_points) >= 4:  # At least 2 points to draw a polygon
            if self.polygon_preview_id:
                self.canvas.delete(self.polygon_preview_id)
            self.polygon_preview_id = self.canvas.create_polygon(
                self.polygon_points, outline="blue", fill="", width=2, tags="temp_annotation"
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


def on_release(self, event):
    """Finalizes an annotation when the mouse is released."""
    raw_x = self.canvas.canvasx(event.x)
    raw_y = self.canvas.canvasy(event.y)
    end_x, end_y = self.clamp_to_image_bounds(raw_x, raw_y)
    if self.current_annotation_type == KeypointAnnotation or self.current_annotation_type == PolygonAnnotation:
        return
    
    self.canvas.delete("temp_annotation")

    img_width, img_height = self.image.width, self.image.height

    annotation = None
    canvas_id = None  # Store Canvas ID for selection feature

    if self.current_annotation_type == RectangleAnnotation:
        annotation = RectangleAnnotation(self.start_x, self.start_y, end_x, end_y)
        canvas_id = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red", tags="annotation")

    elif self.current_annotation_type == EllipseAnnotation:
        x1, y1 = self.start_x, self.start_y
        x2, y2 = end_x, end_y
        annotation = EllipseAnnotation(x1, y1, x2, y2)
        canvas_id = self.canvas.create_oval(
            x1, y1, x2, y2,
            outline="red", tags="annotation"
        )
    
    elif self.current_annotation_type == FreehandAnnotation:
        points = self.canvas.coords(self.current_annotation)
        if (len(points) <= 4):
            return
        annotation = FreehandAnnotation(points)
        canvas_id = self.current_annotation  # Freehand already exists on the canvas

    # ⛔️ Validate the annotation before keeping it
    if annotation and not self.is_within_image_bounds(annotation):
        self.canvas.delete(canvas_id)  # Remove from canvas
        return  # Skip saving and updating the listbox

    # ✅ Annotation is valid; keep it
    annotation.coordinates = annotation.normalize_coordinates(img_width, img_height)
    annotation.canvas_id = canvas_id
    self.annotations.append(annotation)
    self.update_annotation_listbox()

def finalise_keypoints(self, event=None):
    print("🔍 Finalizing keypoints...")
    print("Current annotation type:", self.current_annotation_type)
    print("Keypoints so far:", self.keypoints)

    if self.current_annotation_type != KeypointAnnotation:
        print("❌ Not in Keypoint mode.")
        return

    if not self.keypoints:
        print("⚠️ No keypoints to finalize.")
        return

    annotation = KeypointAnnotation(self.keypoints)

    if self.is_within_image_bounds(annotation):
        annotation.canvas_id = self.keypoint_canvas_ids.copy()  # 🔧 Save canvas IDs


        print("📦 Before appending, annotations:", [a.annotation_type for a in self.annotations])
        self.annotations.append(annotation)
        print("📦 Appended annotation:", annotation.annotation_type)
        print("📦 After append, annotations:", [a.annotation_type for a in self.annotations])

        self.update_annotation_listbox()
        print(f"✅ Keypoint group finalized with {len(self.keypoints)} points.")
    else:
        print("❌ Annotation not within bounds. Not added.")

    # Retag visual dots
    for dot_id in self.keypoint_canvas_ids:
        self.canvas.itemconfig(dot_id, tags="annotation")

    # Clear temporary buffers
    self.keypoints = []
    self.keypoint_canvas_ids = []

def finalise_polygon(self, event=None):
    if self.current_annotation_type != PolygonAnnotation:
        print("❌ Not in Polygon mode.")
        return

    if len(self.polygon_points) < 6:
        print("⚠️ Polygon needs at least 3 points.")
        return

    annotation = PolygonAnnotation(self.polygon_points)

    if self.is_within_image_bounds(annotation):
        canvas_id = self.canvas.create_polygon(
            self.polygon_points,
            outline="blue",             # You can choose outline color
            fill="",             # Light red (feels semi-transparent)
            width=2,
            tags="annotation"
        )
        annotation.canvas_id = canvas_id
        annotation.coordinates = annotation.normalize_coordinates(self.image.width, self.image.height)
        self.annotations.append(annotation)
        self.update_annotation_listbox()
        print("✅ Polygon finalized and added.")
    else:
        print("❌ Polygon out of bounds.")

    # Clear preview and buffers
    if self.polygon_preview_id:
        self.canvas.delete(self.polygon_preview_id)
        self.polygon_preview_id = None
    self.polygon_points = []


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
        print(f" - Annotation {index}: {annotation.annotation_type}")  # Debug

        if annotation.annotation_type == "Keypoint":
            label = f"{index + 1}. Keypoints ({len(annotation.coordinates)} points)"
        else:
            label = f"{index + 1}. {annotation.annotation_type}: {annotation.label}"

        print("Inserting into listbox:", label)  # Debug
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


