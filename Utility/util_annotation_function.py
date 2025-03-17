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
    """Undoes the last annotation by removing it from the canvas and storing it in the redo stack."""
    if not self.annotations:
        return  # No annotations to undo

    # Remove the last annotation and store it in the redo stack
    undone_annotation = self.annotations.pop()
    self.undone_annotations.append(undone_annotation)

    # Delete the last drawn annotation from the canvas
    annotation_ids = self.canvas.find_withtag("annotation")
    if annotation_ids:
        self.canvas.delete(annotation_ids[-1])  # Remove only the last annotation

    self.update_annotation_listbox()  # Update the UI


def redo_annotation(self, event=None):
    """Redoes the last undone annotation."""
    if self.undone_annotations:
        redone_annotation = self.undone_annotations.pop()
        self.annotations.append(redone_annotation)

        # Get the current image size
        if self.image:
            img_width = self.image.width
            img_height = self.image.height
        else:
            return  # Prevent crash if image is not loaded

        # Extract annotation data
        ann_type = redone_annotation["type"]
        rel_coords = redone_annotation["coordinates"]

        if ann_type == "Rectangle":
            abs_coords = [rel_coords[i] * (img_width if i % 2 == 0 else img_height) for i in range(4)]
            self.canvas.create_rectangle(*abs_coords, outline="red", tags="annotation")

        elif ann_type == "Circle":
            cx, cy, r = rel_coords
            cx *= img_width
            cy *= img_height
            r *= img_width  # Scale radius based on width

            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="red", tags="annotation")

        elif ann_type == "Freehand":
            abs_points = [rel_coords[i] * (img_width if i % 2 == 0 else img_height) for i in range(len(rel_coords))]
            self.canvas.create_line(*abs_points, fill="red", width=2, tags="annotation")

        self.update_annotation_listbox()


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
