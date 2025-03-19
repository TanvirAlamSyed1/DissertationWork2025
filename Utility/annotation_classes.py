import uuid

class Annotation:
    """Base class for annotations"""
    def __init__(self, annotation_type, coordinates):
        self.id = str(uuid.uuid4())
        self.annotation_type = annotation_type
        self.coordinates = coordinates
        self.label = "No Label"
        self.canvas_id = None

    # Example normalization in Annotation subclass
    def normalize_coordinates(self, img_width, img_height):
        return [
            coord / img_width if i % 2 == 0 else coord / img_height
            for i, coord in enumerate(self.coordinates)
    ]

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.annotation_type,
            "coordinates": self.coordinates,
            "label": self.label
        }

class RectangleAnnotation(Annotation):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__("Rectangle", [start_x, start_y, end_x, end_y])

class CircleAnnotation(Annotation):
    def __init__(self, center_x, center_y, radius):
        super().__init__("Circle", [center_x, center_y, radius])

class FreehandAnnotation(Annotation):  # Freehand as polygon (COCO-style)
    def __init__(self, points):
        super().__init__("Freehand", points)

class PolygonAnnotation(Annotation):
    def __init__(self, points):
        super().__init__("Polygon", points)

class KeypointAnnotation(Annotation):
    def __init__(self, keypoints):  # keypoints: list of tuples (x,y,visibility)
        super().__init__("Keypoint", keypoints)

    def normalize_coordinates(self, img_width, img_height):
        return [
            (x/img_width, y/img_height, v) for x, y, v in self.coordinates
        ]
class SemanticSegmentationAnnotation(Annotation):
    def __init__(self, mask_filename):
        super().__init__("SemanticSegmentation", mask_file_path)

