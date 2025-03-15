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
        radius = ((cur_x - self.start_x) ** 2 + (cur_y - self.start_y) ** 2) ** 0.5
        self.current_annotation = self.canvas.create_oval(
            self.start_x - radius, self.start_y - radius,
            self.start_x + radius, self.start_y + radius,
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

    elif self.current_annotation_type == "Circle":
        # Ensure correct center and radius
        x1, y1, x2, y2 = self.start_x, self.start_y, end_x, end_y
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2

        self.current_annotation = self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline="red", tags="annotation"
        )

        rel_coords = [
            center_x / img_width,  # Store center X relative to full width
            center_y / img_height,  # Store center Y relative to full height
            radius / img_width  # Store radius relative to width (avoiding min_dim issues)
        ]

    elif self.current_annotation_type == "Freehand":
        points = self.canvas.coords(self.current_annotation)
        rel_coords = [
            points[i] / img_width if i % 2 == 0 else points[i] / img_height
            for i in range(len(points))
        ]

    if rel_coords:
        self.annotations.append((self.current_annotation_type, rel_coords))

    self.update_annotation_listbox()



def clear_annotation(self):
    """Clears all annotations."""
    self.canvas.delete("annotation")
    self.annotations.clear()
    self.undone_annotations.clear()
    self.update_annotation_listbox()

def undo_annotation(self):
    """Undoes the last annotation."""
    if self.annotations:
        undone_annotation = self.annotations.pop()
        self.undone_annotations.append(undone_annotation)

        self.canvas.delete(self.canvas.find_withtag("annotation")[-1])
        self.update_annotation_listbox()

def redo_annotation(self):
    """Redoes the last undone annotation."""
    if self.undone_annotations:
        redone_annotation = self.undone_annotations.pop()
        self.annotations.append(redone_annotation)

        # Get the current image size to scale correctly
        img_width = self.image.width
        img_height = self.image.height

        # Redraw the annotation on the canvas
        ann_type, rel_coords = redone_annotation

        if ann_type == "Rectangle":
            abs_coords = [
                rel_coords[0] * img_width,
                rel_coords[1] * img_height,
                rel_coords[2] * img_width,
                rel_coords[3] * img_height
            ]
            self.canvas.create_rectangle(*abs_coords, outline="red", tags="annotation")

        elif ann_type == "Circle":
            center_x = rel_coords[0] * img_width
            center_y = rel_coords[1] * img_height
            radius = rel_coords[2] * img_width  # Use width scaling for radius

            self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline="red", tags="annotation"
            )

        elif ann_type == "Freehand":
            abs_points = [
                rel_coords[i] * img_width if i % 2 == 0 else rel_coords[i] * img_height
                for i in range(len(rel_coords))
            ]
            self.canvas.create_line(*abs_points, fill="red", width=2, tags="annotation")

        self.update_annotation_listbox()

def update_annotation_listbox(self):
    """Updates the listbox to display RELATIVE coordinates."""
    self.annotation_listbox.delete(0, tk.END)
    for i, (ann_type, rel_coords) in enumerate(self.annotations):
        self.annotation_listbox.insert(tk.END, f"{i+1}. {ann_type}: {rel_coords}")  # Shows RELATIVE coords

def change_annotation_type(self, event):
    """Changes the annotation type based on user selection."""
    self.current_annotation_type = self.annotation_type.get()
