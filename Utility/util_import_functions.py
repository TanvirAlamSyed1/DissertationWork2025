import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox,simpledialog
import json
import os
from Utility.annotation_classes import *


def show_listbox_menu(self, event):
    widget = event.widget
    index = widget.nearest(event.y)
    if index < len(self.annotations):
        self.selected_annotation_index = index  # ✅ Store index for delete
        self.annotation_listbox.selection_clear(0, tk.END)
        self.annotation_listbox.selection_set(index)
        self.listbox_menu.post(event.x_root, event.y_root)

def load_folder(self, event=None):
    """Allows user to select an input folder and loads all image files."""
    selected_folder = filedialog.askdirectory(title="Select Input Folder")

    if not selected_folder:
        messagebox.showinfo("Cancelled", "No folder selected. Keeping the current image set.")
        return

    self.input_folder = selected_folder

    # Check for image files
    self.image_files = [
        f for f in os.listdir(self.input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
    ]

    if not self.image_files:
        messagebox.showwarning("Warning", "No image files found in the selected folder.")
        return

    # Create required folder structure
    self.annotation_folder = os.path.join(self.input_folder, "annotations")
    self.annotated_image_folder = os.path.join(self.input_folder, "annotations", "Annotated_Images")

    # Folders for each annotation format
    formats = ["COCO", "YOLO", "PascalVOC", "Masks", "JSON"]
    for fmt in formats:
        os.makedirs(os.path.join(self.annotation_folder, fmt), exist_ok=True)

    # Annotated Images folder
    os.makedirs(self.annotated_image_folder, exist_ok=True)

    self.current_image_index = 0
    self.load_image()

    messagebox.showinfo("Folder Structure Created", 
                        f"Created annotation folders at:\n{self.annotation_folder}")

def load_annotations(self, event=None):
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.basename(current_image)
    base_name = os.path.splitext(image_name)[0]
    annotations_file = os.path.join(
        self.annotation_folder, "JSON", f"{base_name}_annotations.json"
    )

    print(f"[DEBUG] Loading annotations from: {annotations_file}")

    if not os.path.exists(annotations_file):
        if messagebox.askquestion("Annotations Not Found",
                                  f"No local annotations found for '{image_name}'.\nWould you like to import from another format?",
                                  icon='question') != "yes":
            return

        format_choice = simpledialog.askstring("Import Format", "Enter format: COCO / YOLO / Pascal VOC")
        if not format_choice:
            return

        format_map = {
            "coco": self.import_coco,
            "yolo": self.import_yolo,
            "pascal voc": self.import_pascal_voc,
            "voc": self.import_pascal_voc
        }

        handler = format_map.get(format_choice.strip().lower())
        if handler:
            handler()
        else:
            messagebox.showerror("Invalid Format", "Only 'COCO', 'YOLO', or 'Pascal VOC' supported for import.")
        return

    try:
        with open(annotations_file, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        messagebox.showerror("Error", "Failed to load JSON. The file might be corrupted.")
        return

    if data.get("image_name") != image_name or "annotations" not in data:
        messagebox.showwarning("Error", "Mismatch or missing annotation data.")
        return

    self.annotations.clear()
    img_w, img_h = self.image.width, self.image.height

    type_handlers = {
        "Rectangle": RectangleAnnotation,
        "Ellipse": EllipseAnnotation,
        "Circle": CircleAnnotation,
        "Freehand": FreehandAnnotation,
        "Polygon": PolygonAnnotation,
        "Keypoint": lambda coords: KeypointAnnotation([(x, y, v) for x, y, v in coords])
    }

    for ann in data["annotations"]:
        ann_type = ann.get("type")
        coords = ann.get("coordinates", [])
        label = ann.get("label", "No Label")

        if ann_type in type_handlers and coords:
            try:
                if ann_type == "Keypoint":
                    annotation = type_handlers[ann_type](coords)
                elif ann_type in ["Polygon", "Freehand"]:
                    annotation = type_handlers[ann_type](coords)  # Pass coords as a single list
                else:
                    annotation = type_handlers[ann_type](*coords)

                annotation.label = label
                annotation.id = ann.get("id", str(uuid.uuid4()))
                annotation.iscrowd = ann.get("iscrowd", 0)
                annotation.islocked = ann.get("islocked", False)
                annotation.ismask = ann.get("ismask", False)

                current_width = int(self.image.width * self.zoom_factor)
                current_height = int(self.image.height * self.zoom_factor)

                annotation.canvas_id = annotation.draw_annotation(self.canvas, current_width, current_height, "red")
                self.annotations.append(annotation)
                print(f"[DEBUG] Annotation imported: {annotation.annotation_type}, Label: {label}")
            except Exception as e:
                print(f"[ERROR] Skipping annotation due to error: {e}")

    print(f"[INFO] Total annotations loaded: {len(self.annotations)}")
    self.update_annotation_listbox()
    messagebox.showinfo("Loaded", f"Annotations loaded from {annotations_file}")

def redraw_annotations(self):
    """Redraws all annotations on the canvas without deleting the image."""
    self.canvas.delete("annotation")  # Only delete previous annotations, not the image!

    if not self.image:
        return

    # ✅ Use zoomed image size
    current_width = int(self.image.width * self.zoom_factor)
    current_height = int(self.image.height * self.zoom_factor)

    # DO NOT re-draw the image here again!
    # self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

    for annotation in self.annotations:
        self.redraw_annotation(annotation, current_width, current_height)

    self.update_annotation_listbox()

def label_annotation(self, event):
    """Allows the user to label an annotation when they double-click on it in the Listbox."""
    selected_index = self.annotation_listbox.curselection()
    
    if not selected_index:
        return

    selected_index = selected_index[0]  
    annotation = self.annotations[selected_index]  

    label = tk.simpledialog.askstring("Label Annotation", "Enter a label for this annotation:")

    if label:  
        annotation.label = label  # Update label
        self.update_annotation_listbox()  # Refresh listbox

def download_annotations(self):
    if not self.annotation_folder:
        messagebox.showerror("Error", "No annotation folder loaded.")
        return

    export_format = simpledialog.askstring(
        "Export Format",
        "Enter format: COCO / YOLO / PascalVOC / Mask / JSON"
    )
    if not export_format:
        return

    format_lower = export_format.lower()
    data = load_all_annotations(self.annotation_folder)

    # Ask user to select a base folder
    base_folder = filedialog.askdirectory(title="Select Output Folder")
    if not base_folder:
        return
    if format_lower == "json":
        export_folder = os.path.join(base_folder, "AllAnnotations")
        os.makedirs(export_folder, exist_ok=True)

        export_path = os.path.join(export_folder, "annotations_all.json")
        with open(export_path, "w") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Exported", f"All annotations saved to:\n{export_path}")

    elif format_lower == "coco":
        export_folder = os.path.join(base_folder, "COCO")
        os.makedirs(export_folder, exist_ok=True)
        export_path = os.path.join(export_folder, "annotations_coco.json")
        export_to_coco(data, export_path)
        messagebox.showinfo("Exported", f"COCO annotations saved to:\n{export_path}")

    elif format_lower == "yolo":
        export_folder = os.path.join(base_folder, "YOLO")
        os.makedirs(export_folder, exist_ok=True)
        export_to_yolo(data, export_folder)
        messagebox.showinfo("Exported", f"YOLO labels saved in:\n{export_folder}")

    elif format_lower in ["pascal", "pascalvoc", "voc"]:
        export_folder = os.path.join(base_folder, "PascalVOC")
        os.makedirs(export_folder, exist_ok=True)
        export_to_pascal_voc(data, export_folder)
        messagebox.showinfo("Exported", f"Pascal VOC XMLs saved in:\n{export_folder}")

    elif format_lower == "mask":
        export_folder = os.path.join(base_folder, "Masks")
        os.makedirs(export_folder, exist_ok=True)
        
        # ✅ COCO conversion needed before mask export
        temp_coco_path = os.path.join(export_folder, "temp_annotations_coco.json")
        export_to_coco(data, temp_coco_path)
        with open(temp_coco_path, "r") as f:
            coco_data = json.load(f)

        generate_semantic_masks(coco_data, export_folder)

        os.remove(temp_coco_path)  # clean up
        messagebox.showinfo("Exported", f"Semantic masks saved in:\n{export_folder}")

    else:
        messagebox.showerror("Unsupported Format", f"Format '{export_format}' is not supported.")

def toggle_lock_annotation(self):
    index = self.selected_annotation_index
    if index is not None and index < len(self.annotations):
        annotation = self.annotations[index]
        annotation.islocked = not getattr(annotation, "islocked", False)
        status = "🔒 Locked" if annotation.islocked else "🔓 Unlocked"
        print(f"{status} annotation {index}")
        self.update_annotation_listbox()
        self.redraw_annotations()

def import_yolo(self):
    folder = filedialog.askdirectory(title="Select YOLO Folder")
    if not folder:
        return

    img_w, img_h = self.image.width, self.image.height
    base_name = os.path.splitext(self.image_files[self.current_image_index])[0]
    txt_path = os.path.join(folder, f"{base_name}.txt")
    classes_path = os.path.join(folder, "classes.txt")

    if not os.path.exists(txt_path) or not os.path.exists(classes_path):
        messagebox.showerror("Error", "Missing YOLO .txt or classes.txt file.")
        return

    with open(classes_path, "r") as f:
        class_list = [line.strip() for line in f.readlines()]

    new_annotations = []

    with open(txt_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            class_id, center_x, center_y, width, height = map(float, parts)
            label = class_list[int(class_id)]

            x1 = center_x - width / 2
            y1 = center_y - height / 2
            x2 = center_x + width / 2
            y2 = center_y + height / 2

            ann = RectangleAnnotation(x1, y1, x2, y2)
            ann.label = label
            new_annotations.append(ann)

    self.annotations = new_annotations
    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Import", f"YOLO import successful: {len(new_annotations)} annotations.")

def import_pascal_voc(self):
    folder = filedialog.askdirectory(title="Select Pascal VOC Folder")
    if not folder:
        return

    img_w, img_h = self.image.width, self.image.height
    base_name = os.path.splitext(self.image_files[self.current_image_index])[0]
    xml_path = os.path.join(folder, f"{base_name}.xml")

    if not os.path.exists(xml_path):
        messagebox.showerror("Error", "Missing Pascal VOC XML file.")
        return

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse XML: {e}")
        return

    new_annotations = []

    for obj in root.findall("object"):
        label = obj.findtext("name", default="No Label")
        bbox = obj.find("bndbox")
        if bbox is None:
            continue

        try:
            xmin = int(bbox.findtext("xmin")) / img_w
            ymin = int(bbox.findtext("ymin")) / img_h
            xmax = int(bbox.findtext("xmax")) / img_w
            ymax = int(bbox.findtext("ymax")) / img_h

            ann = RectangleAnnotation(xmin, ymin, xmax, ymax)
            ann.label = label
            new_annotations.append(ann)
        except Exception as e:
            print(f"Skipping bad annotation: {e}")

    self.annotations = new_annotations
    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Import", f"Pascal VOC import successful: {len(new_annotations)} annotations.")

def import_coco(self):
    from tkinter import filedialog, messagebox
    import json
    import os

    import_path = filedialog.askopenfilename(title="Select COCO JSON", filetypes=[("JSON files", "*.json")])
    if not import_path:
        return

    try:
        with open(import_path, "r") as f:
            coco_data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON: {e}")
        return

    current_image = self.image_files[self.current_image_index]
    base_image_name = os.path.splitext(os.path.basename(current_image))[0].lower()

    img_entry = None
    for img in coco_data.get("images", []):
        if base_image_name in os.path.splitext(img["file_name"])[0].lower():
            img_entry = img
            break

    if not img_entry:
        messagebox.showwarning("Not Found", "Image not found in COCO JSON.")
        return

    img_w, img_h = img_entry["width"], img_entry["height"]
    image_id = img_entry["id"]

    self.annotations.clear()
    cat_id_to_label = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}

    for ann in coco_data.get("annotations", []):
        if ann.get("image_id") != image_id:
            continue

        label = cat_id_to_label.get(ann.get("category_id"), "No Label")
        iscrowd = ann.get("iscrowd", 0)

        annotation = None

        # --- Rectangle ---
        if "bbox" in ann and not ann.get("segmentation") and not ann.get("keypoints"):
            x, y, w, h = ann["bbox"]
            if x > 1.0 or y > 1.0 or w > 1.0 or h > 1.0:
                x /= img_w
                y /= img_h
                w /= img_w
                h /= img_h
            annotation = RectangleAnnotation(x, y, x + w, y + h)

        # --- Polygon / Freehand / Circle / Ellipse ---
        elif "segmentation" in ann and ann["segmentation"]:
            points = ann["segmentation"][0]

            if any(pt > 1.0 for pt in points):
                norm_points = [
                    (pt / img_w) if i % 2 == 0 else (pt / img_h)
                    for i, pt in enumerate(points)
                ]
            else:
                norm_points = points

            if looks_like_circle_or_ellipse(norm_points):
                x_coords = norm_points[::2]
                y_coords = norm_points[1::2]
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)

                if abs((x_max - x_min) - (y_max - y_min)) < 0.05:  # nearly circular
                    annotation = CircleAnnotation(x_min, y_min, x_max, y_max)
                else:
                    annotation = EllipseAnnotation(x_min, y_min, x_max, y_max)
            else:
                if len(norm_points) <= 75:
                    annotation = PolygonAnnotation(norm_points)
                else:
                    annotation = FreehandAnnotation(norm_points)

        # --- Keypoints ---
        elif "keypoints" in ann and ann["keypoints"]:
            kps = ann["keypoints"]
            keypoints = []
            for i in range(0, len(kps), 3):
                x = kps[i]
                y = kps[i+1]
                v = kps[i+2]
                if x > 1.0 or y > 1.0:
                    x /= img_w
                    y /= img_h
                keypoints.append((x, y, v))
            annotation = KeypointAnnotation(keypoints)

        if annotation:
            annotation.label = label
            annotation.iscrowd = iscrowd
            self.annotations.append(annotation)

    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Imported", "COCO annotations loaded successfully!")

def looks_like_circle_or_ellipse(points):
    if len(points) < 20:
        return False

    xs = points[::2]
    ys = points[1::2]
    cx = (max(xs) + min(xs)) / 2
    cy = (max(ys) + min(ys)) / 2
    rx = (max(xs) - min(xs)) / 2
    ry = (max(ys) - min(ys)) / 2

    radius_errors = []
    for x, y in zip(xs, ys):
        dx = x - cx
        dy = y - cy
        if rx > 0 and ry > 0:
            error = abs((dx / rx) ** 2 + (dy / ry) ** 2 - 1)
            radius_errors.append(error)

    average_error = sum(radius_errors) / len(radius_errors)
    return average_error < 0.1
