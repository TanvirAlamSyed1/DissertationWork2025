import tkinter as tk

def on_press(self, event):
    self.start_x = self.canvas.canvasx(event.x)
    self.start_y = self.canvas.canvasy(event.y)
    if self.current_annotation_type == "Freehand":
        self.current_annotation = self.canvas.create_line(
            self.start_x, self.start_y, self.start_x, self.start_y,
            fill="red", width=2, tags="annotation"
        )

def on_drag(self, event):
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
    end_x = self.canvas.canvasx(event.x)
    end_y = self.canvas.canvasy(event.y)
    
    self.canvas.delete("temp_annotation")
    
    # Store annotations relative to the original image size
    if self.current_annotation_type == "Rectangle":
        self.current_annotation = self.canvas.create_rectangle(
            self.start_x, self.start_y, end_x, end_y,
            outline="red", tags="annotation"
        )
    elif self.current_annotation_type == "Circle":
        radius = ((end_x - self.start_x) ** 2 + (end_y - self.start_y) ** 2) ** 0.5
        self.current_annotation = self.canvas.create_oval(
            self.start_x - radius, self.start_y - radius,
            self.start_x + radius, self.start_y + radius,
            outline="red", tags="annotation"
        )

    # Convert absolute pixel positions to relative (0-1 range)
    ann_coords = self.canvas.coords(self.current_annotation)
    rel_coords = [
        ann_coords[0] / self.image.width,
        ann_coords[1] / self.image.height,
        ann_coords[2] / self.image.width,
        ann_coords[3] / self.image.height
    ]

    self.annotations.append((self.current_annotation_type, rel_coords))
    self.update_annotation_listbox()


def clear_annotation(self):
    self.canvas.delete("annotation")
    self.annotations.clear()
    self.update_annotation_listbox()

def undo_annotation(self):
    if self.annotations:
        self.annotations.pop()
        self.canvas.delete(self.canvas.find_withtag("annotation")[-1])
        self.update_annotation_listbox()

def update_annotation_listbox(self):
    self.annotation_listbox.delete(0, tk.END)
    for i, (ann_type, coords) in enumerate(self.annotations):
        self.annotation_listbox.insert(tk.END, f"{i+1}. {ann_type}: {coords}")


def change_annotation_type(self, event):
    self.current_annotation_type = self.annotation_type.get()
