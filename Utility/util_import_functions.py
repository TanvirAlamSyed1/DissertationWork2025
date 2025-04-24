import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox,simpledialog
from Utility.annotation_classes import *
import json
import os
from Utility.util_mask_generator import generate_semantic_masks
from Utility.util_export_functions import (
    load_all_annotations,
    export_to_coco,
    export_to_yolo,
    export_to_pascal_voc
)

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
        return  # ❌ User cancelled, exit safely without wiping state

    self.input_folder = selected_folder

    # Check for image files
    self.image_files = [
        f for f in os.listdir(self.input_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
    ]

    if not self.image_files:
        messagebox.showwarning("Warning", "No image files found in the selected folder.")
        return

    # ✅ Only create folders if images are found
    self.annotation_folder = os.path.join(self.input_folder, "annotations")
    self.annotated_image_folder = os.path.join(self.input_folder, "annotated_images")
    os.makedirs(self.annotation_folder, exist_ok=True)
    os.makedirs(self.annotated_image_folder, exist_ok=True)

    self.current_image_index = 0
    self.load_image()

    
def load_annotations(self, event=None):
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    current_image = self.image_files[self.current_image_index]
    image_name = os.path.basename(current_image)
    annotations_file = os.path.normpath((os.path.join(self.annotation_folder, f"{os.path.splitext(image_name)[0]}_annotations.json")))
    print(f"[DEBUG] Looking for annotations at: {annotations_file}")

    if not os.path.exists(annotations_file):
        if messagebox.askquestion("Annotations Not Found",
                                  f"No local annotations found for '{image_name}'.\nWould you like to import from COCO or YOLO?",
                                  icon='question') != "yes":
            return

        format_choice = simpledialog.askstring("Import Format", "Enter format: COCO / YOLO / Pascal VOC")
        if not format_choice:
            return

        format_map = {
            "coco": import_coco,
            "yolo": import_yolo,
            "pascal voc": import_pascal_voc,
            "voc": import_pascal_voc
        }

        handler = format_map.get(format_choice.strip().lower())
        if handler:
            handler(self)
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

    def scale_coords(coords):
        return [coords[i] * img_w if i % 2 == 0 else coords[i] * img_h for i in range(len(coords))]

    type_handlers = {
        "Rectangle": lambda c: RectangleAnnotation(*scale_coords(c)),
        "Ellipse": lambda c: EllipseAnnotation(*scale_coords(c)),
        "Circle": lambda c: CircleAnnotation(*scale_coords(c)),
        "Freehand": lambda c: FreehandAnnotation(scale_coords(c)),
        "Polygon": lambda c: PolygonAnnotation(scale_coords(c)),
        "Keypoint": lambda c: KeypointAnnotation([(x, y, v if len(k) > 2 else 2)
                                                  for k in c if isinstance(k, (list, tuple)) and len(k) >= 2
                                                  for x, y, *v in [k]])
    }

    for ann in data["annotations"]:
        ann_type = ann.get("type")
        coords = ann.get("coordinates", [])
        label = ann.get("label", "No Label")

        if ann_type in type_handlers and coords:
            try:
                annotation = type_handlers[ann_type](coords)
                annotation.label = label
                annotation.id = ann.get("id", "")
                annotation.iscrowd = ann.get("iscrowd", 0)
                self.annotations.append(annotation)
            except Exception as e:
                print(f"Skipping annotation due to error: {e}")

    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Loaded", f"Annotations loaded from {annotations_file}")




def redraw_annotations(self):
    """Redraws all annotations on the canvas without deleting the image."""
    self.canvas.delete("annotation")

    if not self.image:
        return

    # ✅ Use zoomed image size
    current_width = int(self.image.width * self.zoom_factor)
    current_height = int(self.image.height * self.zoom_factor)

    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

    for annotation in self.annotations:
        self.redraw_annotation(annotation, current_width, current_height)

    self.update_annotation_listbox()
    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")
    self.canvas.tag_lower("image")  # 🧠 Always keep image in the background



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
        annotation.locked = not getattr(annotation, "locked", False)
        status = "🔒 Locked" if annotation.locked else "🔓 Unlocked"
        print(f"{status} annotation {index}")
        self.update_annotation_listbox()
        
def import_yolo(self):
    yolo_folder = filedialog.askdirectory(title="Select YOLO Annotation Folder")
    if not yolo_folder:
        return

    image_name = os.path.splitext(self.image_files[self.current_image_index])[0]
    txt_file = os.path.join(yolo_folder, f"{image_name}.txt")
    classes_file = os.path.join(yolo_folder, "classes.txt")

    if not os.path.exists(txt_file) or not os.path.exists(classes_file):
        messagebox.showerror("Missing Files", "YOLO .txt or classes.txt file is missing.")
        return

    with open(classes_file, "r") as f:
        class_list = [line.strip() for line in f.readlines()]

    self.annotations.clear()
    img_w, img_h = self.image.width, self.image.height

    with open(txt_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            class_id, x_center, y_center, width, height = map(float, parts)
            label = class_list[int(class_id)]

            x1 = (x_center - width / 2)
            y1 = (y_center - height / 2)
            x2 = (x_center + width / 2)
            y2 = (y_center + height / 2)

            annotation = RectangleAnnotation(x1, y1, x2, y2)
            annotation.label = label
            self.annotations.append(annotation)

    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Import Successful", "YOLO annotations imported.")
import xml.etree.ElementTree as ET

def import_pascal_voc(self):
    voc_folder = filedialog.askdirectory(title="Select Pascal VOC Folder")
    if not voc_folder:
        return

    image_name = os.path.splitext(self.image_files[self.current_image_index])[0]
    xml_path = os.path.join(voc_folder, f"{image_name}.xml")

    if not os.path.exists(xml_path):
        messagebox.showwarning("Not Found", f"No XML file found for {image_name}.")
        return

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to parse XML: {e}")
        return

    self.annotations.clear()
    img_w, img_h = self.image.width, self.image.height

    for obj in root.findall("object"):
        label = obj.findtext("name", default="unlabeled")
        bbox = obj.find("bndbox")
        if bbox is None:
            continue

        try:
            xmin = int(bbox.findtext("xmin"))
            ymin = int(bbox.findtext("ymin"))
            xmax = int(bbox.findtext("xmax"))
            ymax = int(bbox.findtext("ymax"))

            # Normalize coordinates
            x1 = xmin / img_w
            y1 = ymin / img_h
            x2 = xmax / img_w
            y2 = ymax / img_h

            ann = RectangleAnnotation(x1, y1, x2, y2)
            ann.label = label
            ann.iscrowd = int(obj.findtext("difficult", default="0"))
            self.annotations.append(ann)

        except (ValueError, TypeError):
            continue

    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Import Successful", f"Pascal VOC annotations loaded for {image_name}.")

def import_coco(self):
    import_file = filedialog.askopenfilename(title="Select COCO JSON", filetypes=[("JSON Files", "*.json")])
    if not import_file:
        return

    try:
        with open(import_file, "r") as f:
            coco_data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load JSON: {e}")
        return

    image_name = os.path.basename(self.image_files[self.current_image_index])
    current_image_id = None

    # Find matching image entry
    for img in coco_data.get("images", []):
        if img["file_name"] == image_name:
            current_image_id = img["id"]
            break

    if current_image_id is None:
        messagebox.showwarning("Image Not Found", "Current image not found in COCO JSON.")
        return

    self.annotations.clear()
    img_w, img_h = self.image.width, self.image.height
    cat_id_to_label = {cat["id"]: cat["name"] for cat in coco_data.get("categories", [])}

    for ann in coco_data.get("annotations", []):
        if ann["image_id"] != current_image_id:
            continue

        label = cat_id_to_label.get(ann["category_id"], "Unknown")
        iscrowd = ann.get("iscrowd", 0)

        if "bbox" in ann:
            x, y, w, h = ann["bbox"]
            annotation = RectangleAnnotation(
                x / img_w, y / img_h, (x + w) / img_w, (y + h) / img_h
            )
        elif "segmentation" in ann and ann["segmentation"]:
            points = ann["segmentation"][0]  # assume 1 polygon
            norm_coords = [
                pt / img_w if i % 2 == 0 else pt / img_h for i, pt in enumerate(points)
            ]
            annotation = PolygonAnnotation(norm_coords)
        elif "keypoints" in ann:
            keypoints = ann["keypoints"]
            kp_list = []
            for i in range(0, len(keypoints), 3):
                kp_list.append((
                    keypoints[i] / img_w,
                    keypoints[i + 1] / img_h,
                    keypoints[i + 2]
                ))
            annotation = KeypointAnnotation(kp_list)
        else:
            continue

        annotation.label = label
        annotation.iscrowd = iscrowd
        self.annotations.append(annotation)

    self.redraw_annotations()
    self.update_annotation_listbox()
    messagebox.showinfo("Import Successful", "COCO annotations imported.")
