import uuid

class Annotation:
    """Base class for all annotation types."""

    def __init__(self, annotation_type, coordinates):
        self.id = str(uuid.uuid4())  # Generates a unique ID
        self.annotation_type = annotation_type
        self.coordinates = coordinates
        self.label = "No Label"

    def normalize_coordinates(self, img_width, img_height):
        """Converts absolute coordinates to relative format."""
        return [
            coord / img_width if i % 2 == 0 else coord / img_height
            for i, coord in enumerate(self.coordinates)
        ]

    def __str__(self):
        return f"{self.annotation_type}: {self.label} (ID: {self.id})"

class RectangleAnnotation(Annotation):
    def __init__(self, start_x, start_y, end_x, end_y):
        super().__init__("Rectangle", (start_x, start_y, end_x, end_y))

class CircleAnnotation(Annotation):
    def __init__(self, center_x, center_y, radius):
        super().__init__("Circle", (center_x, center_y, radius))

class FreehandAnnotation(Annotation):
    def __init__(self, points):
        super().__init__("Freehand", points)
