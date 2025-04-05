from PIL import Image, ImageDraw
import os

def generate_semantic_masks(annotation_data, save_dir):
    os.makedirs(save_dir, exist_ok=True)

    for image_entry in annotation_data["images"]:
        img_id = image_entry["id"]
        filename = image_entry["file_name"]
        width, height = image_entry["width"], image_entry["height"]

        # Create blank grayscale mask
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)

        # Draw each annotation for this image
        for ann in annotation_data["annotations"]:
            if ann["image_id"] != img_id:
                continue

            class_id = ann["category_id"]
            if "segmentation" not in ann:
                continue

            for seg in ann["segmentation"]:
                # Convert normalized coords to pixels (if necessary)
                if all(x < 1.0 for x in seg):  # normalized
                    seg = [seg[i] * width if i % 2 == 0 else seg[i] * height for i in range(len(seg))]

                polygon = [(seg[i], seg[i + 1]) for i in range(0, len(seg), 2)]
                draw.polygon(polygon, fill=class_id)

        # Save mask
        out_path = os.path.join(save_dir, f"{os.path.splitext(filename)[0]}_mask.png")
        mask.save(out_path)
