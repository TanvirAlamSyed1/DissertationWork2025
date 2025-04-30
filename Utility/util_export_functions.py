# Utility/util_export_functions.py
import json
import os
import datetime
from PIL import Image, ImageDraw
from Utility.annotation_classes import *
from tkinter import messagebox, simpledialog,filedialog
import xml.etree.ElementTree as ET
import tkinter.filedialog as fd
import math

def save_annotations(self, event=None):
    if not self.image_files or self.current_image_index == -1:
        messagebox.showwarning("No Image", "No image is currently loaded.")
        return

    format = simpledialog.askstring("Save Format", "Enter format (COCO / YOLO / VOC / Mask / JSON):")
    if not format:
        return

    format = format.strip().lower()
    image_file = self.image_files[self.current_image_index]
    image_name = os.path.basename(image_file)
    base_name = os.path.splitext(image_name)[0]

    annotation_subfolders = {
        "json": "JSON",
        "coco": "COCO",
        "yolo": "YOLO",
        "voc": "PascalVOC",
        "pascal": "PascalVOC",
        "pascalvoc": "PascalVOC",
        "mask": "Masks"
    }

    if format not in annotation_subfolders:
        messagebox.showerror("Invalid Format", f"Format '{format}' is not supported.")
        return

    target_folder = os.path.join(self.annotation_folder, annotation_subfolders[format])
    os.makedirs(target_folder, exist_ok=True)

    annotations_data = {
        "image_name": image_name,
        "image_width": self.image.width,
        "image_height": self.image.height,
        "annotations": [ann.to_dict(self.image.width, self.image.height) for ann in self.annotations],
    }

    try:
        if format == "json":
            path = os.path.join(target_folder, f"{base_name}_annotations.json")
            with open(path, "w") as f:
                json.dump(annotations_data, f, indent=4)
            messagebox.showinfo("Saved", f"Annotations saved as JSON:\n{path}")

        elif format == "coco":
            path = os.path.join(target_folder, f"{base_name}_coco.json")
            export_to_coco([annotations_data], path)
            messagebox.showinfo("Saved", f"Annotations saved in COCO format:\n{path}")

        elif format == "yolo":
            export_to_yolo([annotations_data], target_folder)
            messagebox.showinfo("Saved", f"Annotations saved in YOLO format:\n{target_folder}")

        elif format in ["voc", "pascal", "pascalvoc"]:
            export_to_pascal_voc([annotations_data], target_folder)
            messagebox.showinfo("Saved", f"Annotations saved in Pascal VOC format:\n{target_folder}")

        elif format == "mask":
            generate_semantic_masks(self, target_folder)
            messagebox.showinfo("Saved", f"Mask PNG saved to:\n{target_folder}")

    except Exception as e:
        messagebox.showerror("Save Error", f"Error saving annotations:\n{e}")


def load_all_annotations(annotation_folder):
    all_data = []
    for file in os.listdir(annotation_folder):
        if file.endswith('_annotations.json'):
            with open(os.path.join(annotation_folder, file), 'r') as f:
                data = json.load(f)
                all_data.append(data)
    return all_data

def export_to_yolo(data, export_folder):
    os.makedirs(export_folder, exist_ok=True)
    label_map = {}

    for entry in data:
        img_w = entry["image_width"]
        img_h = entry["image_height"]
        image_name = entry["image_name"]
        base_name = os.path.splitext(image_name)[0]

        yolo_file = os.path.join(export_folder, f"{base_name}.txt")
        lines = []

        for ann in entry["annotations"]:
            if ann["type"] not in ["Rectangle", "Circle", "Ellipse"]:
                continue  # Only rectangle-like annotations for YOLO

            label = ann["label"]
            class_id = label_map.setdefault(label, len(label_map))

            x1, y1, x2, y2 = ann["coordinates"]

            # 🔥 NEW: No scaling! Assume x1,y1,x2,y2 are normalized 0-1
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            width = abs(x2 - x1)
            height = abs(y2 - y1)
        
            lines.append(f"{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}")

        with open(yolo_file, 'w') as f:
            f.write("\n".join(lines))

    # Save label map
    label_path = os.path.join(export_folder, "classes.txt")
    with open(label_path, "w") as f:
        for label in sorted(label_map, key=lambda x: label_map[x]):
            f.write(f"{label}\n")
    
def export_to_pascal_voc(data, export_folder):
    os.makedirs(export_folder, exist_ok=True)
    skipped = 0
    converted = 0

    for entry in data:
        image_name = entry["image_name"]
        img_w = entry["image_width"]
        img_h = entry["image_height"]
        base_name = os.path.splitext(image_name)[0]
        xml_path = os.path.join(export_folder, f"{base_name}.xml")

        annotation = ET.Element("annotation")
        ET.SubElement(annotation, "filename").text = image_name

        size = ET.SubElement(annotation, "size")
        ET.SubElement(size, "width").text = str(img_w)
        ET.SubElement(size, "height").text = str(img_h)
        ET.SubElement(size, "depth").text = "3"

        for ann in entry["annotations"]:
            ann_type = ann["type"]

            if ann_type not in ["Rectangle", "Circle", "Ellipse"]:
                skipped += 1
                continue

            x1, y1, x2, y2 = ann["coordinates"]  # 🚨 Already normalized!

            if ann_type in ["Circle", "Ellipse"]:
                converted += 1

            # 🚨 Multiply normalized values back to pixel coordinates
            xmin = int(x1 * img_w)
            ymin = int(y1 * img_h)
            xmax = int(x2 * img_w)
            ymax = int(y2 * img_h)

            # Sort coordinates properly
            xmin, xmax = sorted([xmin, xmax])
            ymin, ymax = sorted([ymin, ymax])

            obj = ET.SubElement(annotation, "object")
            ET.SubElement(obj, "name").text = ann.get("label", "unlabeled")
            ET.SubElement(obj, "pose").text = "Unspecified"
            ET.SubElement(obj, "truncated").text = "0"
            ET.SubElement(obj, "difficult").text = str(ann.get("iscrowd", 0))

            bbox = ET.SubElement(obj, "bndbox")
            ET.SubElement(bbox, "xmin").text = str(xmin)
            ET.SubElement(bbox, "ymin").text = str(ymin)
            ET.SubElement(bbox, "xmax").text = str(xmax)
            ET.SubElement(bbox, "ymax").text = str(ymax)

        tree = ET.ElementTree(annotation)
        tree.write(xml_path, encoding="utf-8")

    # Final message
    message = "✅ Pascal VOC export completed.\n"
    if converted:
        message += f"- {converted} Circle/Ellipse annotations converted to rectangles.\n"
    if skipped:
        message += f"- {skipped} non-rectangle annotations skipped."
    messagebox.showinfo("Pascal VOC Export", message)

# 📤 Export COCO Annotations
def export_to_coco(data, export_folder):
    images = []
    annotations = []
    categories = {}
    annotation_id = 1
    category_id = 1

    label_to_category_id = {}

    for image_idx, entry in enumerate(data, start=1):
        img_w = entry["image_width"]
        img_h = entry["image_height"]
        image_name = entry["image_name"]

        images.append({
            "id": image_idx,
            "file_name": image_name,
            "width": img_w,
            "height": img_h
        })

        for ann in entry["annotations"]:
            ann_type = ann.get("type") if isinstance(ann, dict) else ann.__class__.__name__.replace("Annotation", "")
            
            label = ann.get("label", "No Label") if isinstance(ann, dict) else ann.label
            iscrowd = ann.get("iscrowd", 0) if isinstance(ann, dict) else getattr(ann, "iscrowd", 0)

            if label not in label_to_category_id:
                label_to_category_id[label] = category_id
                categories[label] = {
                    "id": category_id,
                    "name": label,
                    "supercategory": "none"
                }
                category_id += 1

            cat_id = label_to_category_id[label]

            coco_ann = {
                "id": annotation_id,
                "image_id": image_idx,
                "category_id": cat_id,
                "iscrowd": iscrowd,
            }

            coordinates = ann["coordinates"] if isinstance(ann, dict) else ann.coordinates

            if ann_type == "Rectangle":
                x1, y1, x2, y2 = coordinates
                x = x1 * img_w
                y = y1 * img_h
                w = (x2 - x1) * img_w
                h = (y2 - y1) * img_h
                coco_ann.update({
                    "bbox": [x, y, w, h],
                    "area": w * h,
                })

            elif ann_type in ["Polygon", "Freehand"]:
                seg = [
                    coord * img_w if i % 2 == 0 else coord * img_h
                    for i, coord in enumerate(coordinates)
                ]
                coco_ann.update({
                    "segmentation": [seg],
                    "bbox": get_bbox_from_polygon(seg),
                    "area": calculate_polygon_area(seg)
                })

            elif ann_type in ["Ellipse", "Circle"]:
                seg = approximate_ellipse_or_circle(coordinates, img_w, img_h)
                coco_ann.update({
                    "segmentation": [seg],
                    "bbox": get_bbox_from_polygon(seg),
                    "area": calculate_polygon_area(seg)
                })

            elif ann_type == "Keypoint":
                keypoints = []
                for x, y, v in coordinates:
                    keypoints.extend([x * img_w, y * img_h, v])
                coco_ann.update({
                    "keypoints": keypoints,
                    "num_keypoints": len(coordinates),
                    "bbox": get_bbox_from_keypoints(keypoints),
                    "area": 0
                })

            annotations.append(coco_ann)
            annotation_id += 1


    coco_output = {
        "images": images,
        "annotations": annotations,
        "categories": list(categories.values())
    }

    with open(export_folder, "w") as f:
        json.dump(coco_output, f, indent=4)

def generate_semantic_masks(self, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    if not hasattr(self, "annotations") or not self.annotations:
        messagebox.showerror("No Annotations", "No annotations found.")
        return

    width, height = self.image.width, self.image.height
    image_filename = self.image_files[self.current_image_index]
    base_name = os.path.splitext(image_filename)[0]

    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)

    drawn_anything = False

    for ann in self.annotations:
        if not getattr(ann, "ismask", False):
            continue  # Skip if not marked as mask

        if not isinstance(ann, (PolygonAnnotation, FreehandAnnotation)):
            continue  # Skip unsupported types

        coords = ann.coordinates

        # Check if normalised
        try:
            if all(0 <= x <= 1 for x in coords):
                points = [
                    (coords[i] * width if i % 2 == 0 else coords[i] * height)
                    for i in range(len(coords))
                ]
            else:
                points = coords
        except Exception as e:
            messagebox.showerror("Coordinate Error", f"Invalid coordinates in annotation {ann.id}: {e}")
            continue

        if len(points) >= 6:
            polygon = [(points[i], points[i + 1]) for i in range(0, len(points), 2)]
            draw.polygon(polygon, fill=1)
            drawn_anything = True
        else:
            messagebox.showerror("Invalid Polygon", f"Skipping annotation {ann.id}: not enough points.")

    if drawn_anything:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = os.path.join(save_dir, f"{base_name}_{timestamp}_mask.png")
        mask.save(out_path)
        messagebox.showinfo("Success", f"✅ Mask generated and saved to:\n{out_path}")
    else:
        messagebox.showerror("No Masks Created", "⚠️ No valid mask annotations found. No mask file created.")


# Helper functions

def get_bbox_from_polygon(points):
    xs = points[::2]
    ys = points[1::2]
    x_min = min(xs)
    y_min = min(ys)
    width = max(xs) - x_min
    height = max(ys) - y_min
    return [x_min, y_min, width, height]

def calculate_polygon_area(points):
    if len(points) < 6:
        return 0
    xs = points[::2]
    ys = points[1::2]
    area = 0.0
    n = len(xs)
    for i in range(n):
        j = (i + 1) % n
        area += xs[i] * ys[j]
        area -= xs[j] * ys[i]
    return abs(area) / 2.0

def get_bbox_from_keypoints(kps):
    xs = [kps[i] for i in range(0, len(kps), 3)]
    ys = [kps[i+1] for i in range(0, len(kps), 3)]
    x_min = min(xs)
    y_min = min(ys)
    width = max(xs) - x_min
    height = max(ys) - y_min
    return [x_min, y_min, width, height]

def approximate_ellipse_or_circle(coordinates, img_w, img_h, num_points=20):
    x1, y1, x2, y2 = coordinates
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    rx = abs(x2 - x1) / 2
    ry = abs(y2 - y1) / 2

    points = []
    for i in range(num_points):
        theta = (2 * math.pi * i) / num_points
        x = (cx + rx * math.cos(theta)) * img_w
        y = (cy + ry * math.sin(theta)) * img_h
        points.append(x)
        points.append(y)
    return points
