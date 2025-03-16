from typing import List, Dict, Any
from uuid import uuid4
from PyQt6.QtCore import QRectF

class Shape:
    def __init__(self, position: List[float], color: List[int], id: str = None):
        self.position = position
        self.color = color
        self.id = id or str(uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "position": self.position,
            "color": self.color
        }
    
    def get_bounds(self) -> QRectF:
        raise NotImplementedError()

class Rectangle(Shape):
    def __init__(self, width: int, height: int, position: List[float],
                 color: List[int], id: str = None):
        super().__init__(position, color, id)
        self.width = width
        self.height = height
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "type": "rectangle",
            "width": self.width,
            "height": self.height
        })
        return data
    
    def get_bounds(self) -> QRectF:
        return QRectF(
            self.position[0] - self.width // 2,
            self.position[1] - self.height // 2,
            self.width,
            self.height
        )

class Circle(Shape):
    def __init__(self, radius: int, position: List[float],
                 color: List[int], id: str = None):
        super().__init__(position, color, id)
        self.radius = radius
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "type": "circle",
            "radius": self.radius
        })
        return data
    
    def get_bounds(self) -> QRectF:
        return QRectF(
            self.position[0] - self.radius,
            self.position[1] - self.radius,
            self.radius * 2,
            self.radius * 2
        )

class Polygon(Shape):
    def __init__(self, points: List[List[float]], position: List[float],
                 color: List[int], id: str = None):
        super().__init__(position, color, id)
        self.points = points
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "type": "polygon",
            "points": self.points
        })
        return data
    
    def get_bounds(self) -> QRectF:
        if not self.points:
            return QRectF()
        
        min_x = min(p[0] for p in self.points)
        max_x = max(p[0] for p in self.points)
        min_y = min(p[1] for p in self.points)
        max_y = max(p[1] for p in self.points)
        
        return QRectF(
            self.position[0] + min_x,
            self.position[1] + min_y,
            max_x - min_x,
            max_y - min_y
        ) 