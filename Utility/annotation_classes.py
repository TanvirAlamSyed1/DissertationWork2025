import uuid

class Annotation:
    def __init__(self, annotation_type, coordinates):
        self.id = str(uuid.uuid4())
        self.annotation_type = annotation_type
        self.coordinates = coordinates
        self.label = "No Label"
        self.canvas_id = None
        self.iscrowd = 0  # 👈 NEW

    def to_dict(self, img_width=None, img_height=None):
        coords = self.coordinates
        if img_width and img_height:
            coords = self.normalize_coordinates(img_width, img_height)

        return {
            "id": self.id,
            "type": self.annotation_type,
            "coordinates": coords,
            "label": self.label,
            "iscrowd": self.iscrowd  # 👈 NEW
        }

    def normalize_coordinates(self, img_width, img_height):
        return [
            coord / img_width if i % 2 == 0 else coord / img_height
            for i, coord in enumerate(self.coordinates)
        ]

    def get_absolute_bounds(self):
        """Should be implemented by subclasses."""
        raise NotImplementedError


class RectangleAnnotation(Annotation):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__("Rectangle", [start_x, start_y, end_x, end_y])

    def get_absolute_bounds(self):
        x1, y1, x2, y2 = self.coordinates
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


class EllipseAnnotation(Annotation):
    def __init__(self, x1, y1, x2, y2):
        super().__init__("Ellipse", [x1, y1, x2, y2])

    def get_absolute_bounds(self):
        x1, y1, x2, y2 = self.coordinates
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

class CircleAnnotation(Annotation):
    def __init__(self, x1, y1, x2, y2):
        # Force the bounding box to be a square
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        size = min(width, height)

        # Preserve the direction of drawing (top-left to bottom-right, etc.)
        if x2 < x1:
            x2 = x1 - size
        else:
            x2 = x1 + size

        if y2 < y1:
            y2 = y1 - size
        else:
            y2 = y1 + size

        super().__init__("Circle", [x1, y1, x2, y2])

    def get_absolute_bounds(self):
        x1, y1, x2, y2 = self.coordinates
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)




class FreehandAnnotation(Annotation):
    def __init__(self, points):
        super().__init__("Freehand", points)

    def get_absolute_bounds(self):
        xs = self.coordinates[::2]
        ys = self.coordinates[1::2]
        return min(xs), min(ys), max(xs), max(ys)


class PolygonAnnotation(Annotation):
    def __init__(self, points):
        super().__init__("Polygon", points)

    def normalize_coordinates(self, img_width, img_height):
        return [
            x / img_width if i % 2 == 0 else x / img_height
            for i, x in enumerate(self.coordinates)
        ]

    def get_absolute_bounds(self):
        xs = self.coordinates[::2]
        ys = self.coordinates[1::2]
        return min(xs), min(ys), max(xs), max(ys)



class KeypointAnnotation(Annotation):
    def __init__(self, keypoints):  # list of (x, y, visibility)
        super().__init__("Keypoint", keypoints)

    def normalize_coordinates(self, img_width, img_height):
        return [
            (x / img_width, y / img_height, v)
            for x, y, v in self.coordinates
        ]
    
    def to_dict(self, img_width=None, img_height=None):
        return {
            "id": self.id,
            "type": self.annotation_type,
            "coordinates": self.coordinates,  # already normalized
            "label": self.label
        }

    def get_absolute_bounds(self):
        xs = [x for x, y, v in self.coordinates]
        ys = [y for x, y, v in self.coordinates]
        return min(xs), min(ys), max(xs), max(ys)


class SemanticSegmentationAnnotation(Annotation):
    def __init__(self, mask_filename):
        super().__init__("SemanticSegmentation", mask_filename)

    def normalize_coordinates(self, img_width, img_height):
        return self.coordinates  # Just return the filename

    def get_absolute_bounds(self):
        return (0, 0, 0, 0)
