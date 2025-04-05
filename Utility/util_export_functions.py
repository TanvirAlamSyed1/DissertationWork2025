# Utility/util_export_functions.py
import json
import os
import xml.etree.ElementTree as ET
import tkinter.filedialog as fd
from Utility.util_mask_generator import generate_semantic_masks
import json

def load_all_annotations(annotation_folder):
    all_data = []
    for file in os.listdir(annotation_folder):
        if file.endswith('_annotations.json'):
            with open(os.path.join(annotation_folder, file), 'r') as f:
                data = json.load(f)
                all_data.append(data)
    return all_data


def export_to_coco(data, export_path):
    images = []
    annotations = []
    categories = {}
    category_id = 1
    annotation_id = 1

    for image_id, entry in enumerate(data, 1):
        img_w = entry["image_width"]
        img_h = entry["image_height"]
        image_name = entry["image_name"]

        images.append({
            "id": image_id,
            "file_name": image_name,
            "width": img_w,
            "height": img_h
        })

        for ann in entry["annotations"]:
            label = ann.get("label", "unlabeled")
            if label not in categories:
                categories[label] = category_id
                category_id += 1

            ann_type = ann["type"]

            if ann_type == "Rectangle":
                x1, y1, x2, y2 = ann["coordinates"]
                x = x1 * img_w
                y = y1 * img_h
                width = abs(x2 - x1) * img_w
                height = abs(y2 - y1) * img_h
                coco_ann = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": categories[label],
                    "bbox": [x, y, width, height],
                    "area": width * height,
                    "iscrowd": ann.get("iscrowd", 0)
                }
                annotations.append(coco_ann)
                annotation_id += 1

            elif ann_type == "Polygon":
                seg = [
                    coord * img_w if i % 2 == 0 else coord * img_h
                    for i, coord in enumerate(ann["coordinates"])
                ]
                coco_ann = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": categories[label],
                    "segmentation": [seg],
                    "bbox": get_bbox_from_polygon(seg),
                    "area": calculate_polygon_area(seg),
                    "iscrowd": ann.get("iscrowd", 0)
                }
                annotations.append(coco_ann)
                annotation_id += 1

            elif ann_type == "Keypoint":
                keypoints = []
                for x, y, v in ann["coordinates"]:
                    keypoints.extend([x * img_w, y * img_h, v])
                coco_ann = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": categories[label],
                    "keypoints": keypoints,
                    "num_keypoints": len(ann["coordinates"]),
                    "bbox": get_bbox_from_keypoints(keypoints),
                    "area": 0,
                    "iscrowd": 0
                }
                annotations.append(coco_ann)
                annotation_id += 1
            
            elif ann_type == "Freehand":
                seg = [
                    coord * img_w if i % 2 == 0 else coord * img_h
                    for i, coord in enumerate(ann["coordinates"])
                ]
                coco_ann = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": categories[label],
                    "segmentation": [seg],
                    "bbox": get_bbox_from_polygon(seg),
                    "area": calculate_polygon_area(seg),
                    "iscrowd": ann.get("iscrowd", 0)
                }
                annotations.append(coco_ann)
                annotation_id += 1

            
            elif ann_type in ["Circle", "Ellipse"]:
                x1, y1, x2, y2 = ann["coordinates"]
                x = x1 * img_w
                y = y1 * img_h
                width = abs(x2 - x1) * img_w
                height = abs(y2 - y1) * img_h
                coco_ann = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": categories[label],
                    "bbox": [x, y, width, height],
                    "area": width * height,
                    "iscrowd": ann.get("iscrowd", 0)
                }
                annotations.append(coco_ann)
                annotation_id += 1


    coco_data = {
        "images": images,
        "annotations": annotations,
        "categories": [{"id": cid, "name": name} for name, cid in categories.items()]
    }

    with open(export_path, 'w') as f:
        json.dump(coco_data, f, indent=4)


def export_to_yolo(data, export_folder):
    os.makedirs(export_folder, exist_ok=True)
    label_map = {}

    for entry in data:
        image_name = entry["image_name"]
        base_name = os.path.splitext(image_name)[0]
        img_w = entry["image_width"]
        img_h = entry["image_height"]

        yolo_file = os.path.join(export_folder, f"{base_name}.txt")
        lines = []

        for ann in entry["annotations"]:
            if ann["type"] not in ["Rectangle", "Circle", "Ellipse"]:
                continue

            label = ann["label"]
            class_id = label_map.setdefault(label, len(label_map))

            x1, y1, x2, y2 = ann["coordinates"]
            x_center = ((x1 + x2) / 2)
            y_center = ((y1 + y2) / 2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)

            lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

        with open(yolo_file, 'w') as f:
            f.write("\n".join(lines))

    # Save label map
    label_path = os.path.join(export_folder, "classes.txt")
    with open(label_path, "w") as f:
        for label in sorted(label_map, key=lambda x: label_map[x]):
            f.write(f"{label}\n")


def export_to_pascal_voc(data, export_folder):
    os.makedirs(export_folder, exist_ok=True)

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
            if ann["type"] not in ["Rectangle", "Circle", "Ellipse"]:
                continue

            x1 = int(ann["coordinates"][0] * img_w)
            y1 = int(ann["coordinates"][1] * img_h)
            x2 = int(ann["coordinates"][2] * img_w)
            y2 = int(ann["coordinates"][3] * img_h)

            obj = ET.SubElement(annotation, "object")
            ET.SubElement(obj, "name").text = ann["label"]
            ET.SubElement(obj, "pose").text = "Unspecified"
            ET.SubElement(obj, "truncated").text = "0"
            ET.SubElement(obj, "difficult").text = str(ann.get("iscrowd", 0))

            bbox = ET.SubElement(obj, "bndbox")
            ET.SubElement(bbox, "xmin").text = str(min(x1, x2))
            ET.SubElement(bbox, "ymin").text = str(min(y1, y2))
            ET.SubElement(bbox, "xmax").text = str(max(x1, x2))
            ET.SubElement(bbox, "ymax").text = str(max(y1, y2))

        tree = ET.ElementTree(annotation)
        tree.write(xml_path)

def get_bbox_from_polygon(points):
    """
    Returns [x, y, width, height] from a flat list of polygon points.
    Assumes: points = [x1, y1, x2, y2, ..., xn, yn]
    """
    xs = points[::2]
    ys = points[1::2]
    x_min = min(xs)
    y_min = min(ys)
    width = max(xs) - x_min
    height = max(ys) - y_min
    return [x_min, y_min, width, height]

def get_bbox_from_keypoints(keypoints):
    """
    Returns [x, y, width, height] from a flat keypoints list:
    keypoints = [x1, y1, v1, x2, y2, v2, ...]
    """
    xs = [keypoints[i] for i in range(0, len(keypoints), 3)]
    ys = [keypoints[i + 1] for i in range(0, len(keypoints), 3)]
    x_min = min(xs)
    y_min = min(ys)
    width = max(xs) - x_min
    height = max(ys) - y_min
    return [x_min, y_min, width, height]

def calculate_polygon_area(points):
    """
    Uses the Shoelace formula to calculate area of a polygon.
    Assumes: points = [x1, y1, x2, y2, ..., xn, yn]
    """
    if len(points) < 6:
        return 0  # not a valid polygon

    xs = points[::2]
    ys = points[1::2]

    area = 0.0
    n = len(xs)
    for i in range(n):
        j = (i + 1) % n
        area += xs[i] * ys[j]
        area -= xs[j] * ys[i]
    return abs(area) / 2.0
