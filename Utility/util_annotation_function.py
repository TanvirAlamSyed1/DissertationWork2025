import tkinter as tk
from Utility.annotation_classes import RectangleAnnotation, CircleAnnotation, FreehandAnnotation

def on_press(self, event):
    """Handles the start of an annotation."""
    self.start_x = self.canvas.canvasx(event.x)
    self.start_y = self.canvas.canvasy(event.y)

    if self.current_annotation_type == FreehandAnnotation:
        self.current_annotation = self.canvas.create_line(
            self.start_x, self.start_y, self.start_x, self.start_y,
            fill="red", width=2, tags="annotation"
        )

def on_drag(self, event):
    """Handles drawing while dragging."""
    cur_x = self.canvas.canvasx(event.x)
    cur_y = self.canvas.canvasy(event.y)

    if self.current_annotation_type == RectangleAnnotation:
        self.canvas.delete("temp_annotation")
        self.current_annotation = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline="red", tags="temp_annotation"
        )

    elif self.current_annotation_type == CircleAnnotation:
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


    elif self.current_annotation_type == FreehandAnnotation:
        self.canvas.coords(
            self.current_annotation,
            *self.canvas.coords(self.current_annotation),
            cur_x, cur_y
        )

def on_release(self, event):
    """Finalizes an annotation when the mouse is released."""
    end_x = self.canvas.canvasx(event.x)
    end_y = self.canvas.canvasy(event.y)

    self.canvas.delete("temp_annotation")
    img_width, img_height = self.image.width, self.image.height

    annotation = None
    canvas_id = None  # Store Canvas ID for selection feature

    if self.current_annotation_type == RectangleAnnotation:
        annotation = RectangleAnnotation(self.start_x, self.start_y, end_x, end_y)
        canvas_id = self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline="red", tags="annotation")

    elif self.current_annotation_type == CircleAnnotation:
        center_x, center_y = (self.start_x + end_x) / 2, (self.start_y + end_y) / 2
        radius = ((end_x - self.start_x) ** 2 + (end_y - self.start_y) ** 2) ** 0.5 / 2
        annotation = CircleAnnotation(center_x, center_y, radius)
        canvas_id = self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline="red", tags="annotation"
        )

    elif self.current_annotation_type == FreehandAnnotation:
        points = self.canvas.coords(self.current_annotation)
        annotation = FreehandAnnotation(points)
        canvas_id = self.current_annotation  # Freehand already exists on the canvas

    if annotation:
        annotation.coordinates = annotation.normalize_coordinates(img_width, img_height)
        annotation.canvas_id = canvas_id  # ✅ Store Canvas ID
        self.annotations.append(annotation)
        self.update_annotation_listbox()

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
    """Redoes the last undone annotation."""
    if self.undone_annotations:
        self.annotations.append(self.undone_annotations.pop())

    self.redraw_annotations()
    self.update_annotation_listbox()


def update_annotation_listbox(self):
    """Updates the Listbox with annotation types and labels."""
    self.annotation_listbox.delete(0, tk.END)

    for index, annotation in enumerate(self.annotations):
        self.annotation_listbox.insert(tk.END, f"{index + 1}. {annotation.annotation_type}: {annotation.label}")

    # Bind the selection event to highlight the selected annotation
    self.annotation_listbox.bind("<<ListboxSelect>>", self.on_annotation_selected)

def on_annotation_selected(self, event):
    """Highlights the selected annotation on the canvas."""
    selected_index = self.annotation_listbox.curselection()

    if not selected_index:
        return  # No selection made

    selected_index = selected_index[0]  # Get the first selected item index
    selected_annotation = self.annotations[selected_index]  # Get the annotation object

    # Reset all annotations to default color
    for annotation in self.annotations:
        if isinstance(annotation, FreehandAnnotation):
            self.canvas.itemconfig(annotation.canvas_id, fill="red")  # ✅ Freehand uses 'fill'
        else:
            self.canvas.itemconfig(annotation.canvas_id, outline="red")  # ✅ Other shapes use 'outline'

    # Highlight the selected annotation
    if isinstance(selected_annotation, FreehandAnnotation):
        self.canvas.itemconfig(selected_annotation.canvas_id, fill="blue")  # ✅ Highlight Freehand in blue
    else:
        self.canvas.itemconfig(selected_annotation.canvas_id, outline="blue")  # ✅ Highlight other shapes in blue



def change_annotation_type(self, event):
    """Changes the annotation type based on user selection."""
    selected_type = self.annotation_type.get()
    if selected_type in self.annotation_classes:
        self.current_annotation_type = self.annotation_classes[selected_type]  # ✅ Now stores class reference

