import tkinter as tk

def on_press(self, event):
    """Handles the start of an annotation."""
    self.start_x = self.canvas.canvasx(event.x)
    self.start_y = self.canvas.canvasy(event.y)

    if self.current_annotation_type == "Freehand":
        self.current_annotation = self.canvas.create_line(
            self.start_x, self.start_y, self.start_x, self.start_y,
            fill="red", width=2, tags="annotation"
        )

def on_drag(self, event):
    """Handles drawing while dragging."""
    cur_x = self.canvas.canvasx(event.x)
    cur_y = self.canvas.canvasy(event.y)

    if self.current_annotation_type == "Rectangle":
        self.canvas.delete("temp_annotation")
        self.current_annotation = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline="red", tags="temp_annotation"
        )

    elif self.current_annotation_type == "Circle":
        self.canvas.delete("temp_annotation")

        # Ensure the circle grows from start to end position
        x1, y1 = self.start_x, self.start_y
        x2, y2 = cur_x, cur_y

        # Calculate center and radius
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2  # Euclidean distance / 2

        self.current_annotation = self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline="red", tags="temp_annotation"
        )


    elif self.current_annotation_type == "Freehand":
        self.canvas.coords(
            self.current_annotation,
            *self.canvas.coords(self.current_annotation),
            cur_x, cur_y
        )


def on_release(self, event):
    """Finalizes an annotation when the mouse is released."""
    end_x = self.canvas.canvasx(event.x)
    end_y = self.canvas.canvasy(event.y)

    self.canvas.delete("temp_annotation")  # Remove temporary drawings

    img_width = self.image.width
    img_height = self.image.height

    rel_coords = []

    if self.current_annotation_type == "Rectangle":
        self.current_annotation = self.canvas.create_rectangle(
            self.start_x, self.start_y, end_x, end_y,
            outline="red", tags="annotation"
        )
        ann_coords = self.canvas.coords(self.current_annotation)
        rel_coords = [
            ann_coords[0] / img_width,
            ann_coords[1] / img_height,
            ann_coords[2] / img_width,
            ann_coords[3] / img_height
        ]
        self.annotations.append({"type": "Rectangle", "coordinates": rel_coords, "label": "No Label"})

    elif self.current_annotation_type == "Circle":
        x1, y1 = self.start_x, self.start_y
        x2, y2 = end_x, end_y

        # Calculate center and radius
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2  # Euclidean distance

        self.current_annotation = self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline="red", tags="annotation"
        )
        rel_coords = [
            center_x / img_width,
            center_y / img_height,
            radius / img_width
        ]
        self.annotations.append({"type": "Circle", "coordinates": rel_coords, "label": "No Label"})

    elif self.current_annotation_type == "Freehand":
        points = self.canvas.coords(self.current_annotation)
        rel_coords = [
            points[i] / img_width if i % 2 == 0 else points[i] / img_height
            for i in range(len(points))
        ]
        self.annotations.append({"type": "Freehand", "coordinates": rel_coords, "label": "No Label"})

    self.update_annotation_listbox()


def clear_annotation(self):
    """Clears all annotations."""
    self.canvas.delete("annotation")
    self.annotations.clear()
    self.undone_annotations.clear()
    self.update_annotation_listbox()

def undo_annotation(self, event=None):
    """Undoes the last annotation action (either deleting or drawing)."""

    if not self.annotations and not self.undone_annotations:
        return  # Nothing to undo

    if self.annotations:
        # ✅ Remove the last drawn annotation and store it for redo
        undone_annotation = self.annotations.pop()
        self.undone_annotations.append(undone_annotation)
    else:
        # ✅ If no new annotations, restore last deleted one
        if self.undone_annotations:
            restored_annotation = self.undone_annotations.pop()
            self.annotations.append(restored_annotation)

    self.redraw_annotations()  # ✅ Update canvas
    self.update_annotation_listbox()  # ✅ Update Listbox

def delete_specific_annotation(self):
    """Deletes the selected annotation and stores it in the undo stack."""
    
    if self.selected_annotation_index is None or self.selected_annotation_index >= len(self.annotations):
        return  # No valid selection

    # Remove the annotation from the list and store it in the undo stack
    deleted_annotation = self.annotations.pop(self.selected_annotation_index)
    self.undone_annotations.append(deleted_annotation)  # ✅ Store in undo stack

    # Remove the annotation from the canvas
    self.redraw_annotations()  # ✅ Redraw the canvas without the deleted annotation

    # Refresh UI
    self.update_annotation_listbox()


def redo_annotation(self, event=None):
    """Redoes the last undone annotation, restoring it properly."""
    
    if not self.undone_annotations:
        return  # No annotations to redo

    # ✅ Restore the last undone annotation
    redone_annotation = self.undone_annotations.pop()
    self.annotations.append(redone_annotation)

    self.redraw_annotations()  # ✅ Update canvas properly
    self.update_annotation_listbox()  # ✅ Sync with Listbox



def update_annotation_listbox(self):
    """Updates the Listbox with the latest annotations, including labels."""
    self.annotation_listbox.delete(0, tk.END)  # Clear existing items

    for i, annotation in enumerate(self.annotations):
        label = annotation.get("label", "No Label")  # Get label or default to "No Label"
        ann_type = annotation["type"]
        self.annotation_listbox.insert(tk.END, f"{ann_type}: {label}")  # Display type and label


def change_annotation_type(self, event):
    """Changes the annotation type based on user selection."""
    self.current_annotation_type = self.annotation_type.get()
