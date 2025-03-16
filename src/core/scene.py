from datetime import datetime
from typing import List, Dict, Any
from src.core.shapes import Rectangle, Circle, Polygon

class Scene:
    def __init__(self, name: str = "Untitled", camera_offset: List[float] = None,
                 grid_size: int = 32, show_grid: bool = True):
        self.name = name
        self.camera_offset = camera_offset or [0, 0]
        self.grid_size = grid_size
        self.show_grid = show_grid
        self.entities = []
        self.created_at = datetime.now().isoformat()
        self.modified_at = self.created_at
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scene':
        scene = cls(
            name=data.get("name", "Untitled"),
            camera_offset=data.get("camera_offset", [0, 0]),
            grid_size=data.get("grid_size", 32),
            show_grid=data.get("show_grid", True)
        )
        
        # Load entities
        for entity_data in data.get("entities", []):
            entity_type = entity_data.get("type")
            if entity_type == "rectangle":
                entity = Rectangle(
                    width=entity_data.get("width", 100),
                    height=entity_data.get("height", 100),
                    position=entity_data.get("position", [0, 0]),
                    color=entity_data.get("color", [255, 255, 255]),
                    id=entity_data.get("id")
                )
            elif entity_type == "circle":
                entity = Circle(
                    radius=entity_data.get("radius", 50),
                    position=entity_data.get("position", [0, 0]),
                    color=entity_data.get("color", [255, 255, 255]),
                    id=entity_data.get("id")
                )
            elif entity_type == "polygon":
                entity = Polygon(
                    points=entity_data.get("points", [[0, 0], [50, 0], [25, 50]]),
                    position=entity_data.get("position", [0, 0]),
                    color=entity_data.get("color", [255, 255, 255]),
                    id=entity_data.get("id")
                )
            else:
                continue
            
            scene.entities.append(entity)
        
        # Set timestamps
        scene.created_at = data.get("created_at", scene.created_at)
        scene.modified_at = data.get("modified_at", scene.modified_at)
        
        return scene
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "camera_offset": self.camera_offset,
            "grid_size": self.grid_size,
            "show_grid": self.show_grid,
            "entities": [entity.to_dict() for entity in self.entities],
            "created_at": self.created_at,
            "modified_at": self.modified_at
        } 