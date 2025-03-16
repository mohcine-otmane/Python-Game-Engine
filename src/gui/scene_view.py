from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPainter, QImage, QColor, QPen
import pygame
import numpy as np

from src.core.shapes import Rectangle, Circle, Polygon

class SceneView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Enable keyboard focus
        
        # Initialize Pygame surface
        pygame.init()
        self._update_pygame_surface()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(16)  # ~60 FPS
        
        # Mouse state
        self.last_mouse_pos = None
        self.is_panning = False
        
        # Initialize scene manager reference
        self.scene_manager = parent.scene_manager if parent else None
        
        self.scene = None
        self.dragged_entity = None
        self.drag_offset = QPoint()
        self.setMouseTracking(True)
        
    def _update_pygame_surface(self):
        """Update Pygame surface to match widget size"""
        self.pygame_surface = pygame.Surface(
            (self.width(), self.height())
        )
        
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self._update_pygame_surface()
        
    def paintEvent(self, event):
        """Paint the scene"""
        if not self.scene:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw grid if enabled
        if self.scene.show_grid:
            self.draw_grid(painter)
        
        # Draw entities
        for entity in self.scene.entities:
            self.draw_entity(painter, entity)
        
        # Get current scene
        scene = self.scene_manager.current_scene if self.scene_manager else None
        
        if scene:
            # Draw scene to Pygame surface
            scene.draw(self.pygame_surface)
            
            # Convert Pygame surface to QImage
            image = self._pygame_surface_to_qimage(self.pygame_surface)
            
            # Draw QImage to widget
            painter.drawImage(0, 0, image)
            
    def _pygame_surface_to_qimage(self, surface):
        """Convert Pygame surface to QImage"""
        size = surface.get_size()
        
        # Get raw buffer
        buffer = pygame.image.tostring(surface, "RGB")
        
        # Create QImage from buffer
        image = QImage(buffer, size[0], size[1], QImage.Format.Format_RGB888)
        return image
        
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = True
        elif event.button() == Qt.MouseButton.LeftButton and self.scene:
            entity = self.find_entity_at_position(event.pos())
            if entity:
                self.dragged_entity = entity
                scene_pos = self.view_to_scene_pos(event.pos())
                self.drag_offset = QPoint(
                    scene_pos.x() - entity.position[0],
                    scene_pos.y() - entity.position[1]
                )
        self.last_mouse_pos = event.pos()
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.is_panning = False
        elif event.button() == Qt.MouseButton.LeftButton:
            self.dragged_entity = None
        self.last_mouse_pos = None
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.is_panning and self.last_mouse_pos and self.scene_manager and self.scene_manager.current_scene:
            # Calculate delta movement
            delta = event.pos() - self.last_mouse_pos
            
            # Update camera offset
            self.scene_manager.current_scene.camera_offset[0] += delta.x()
            self.scene_manager.current_scene.camera_offset[1] += delta.y()
            
            self.last_mouse_pos = event.pos()
            self.update()
        elif self.dragged_entity:
            scene_pos = self.view_to_scene_pos(event.pos())
            self.dragged_entity.position = [
                scene_pos.x() - self.drag_offset.x(),
                scene_pos.y() - self.drag_offset.y()
            ]
            self.update()
            
    def wheelEvent(self, event):
        """Handle mouse wheel events"""
        if self.scene_manager and self.scene_manager.current_scene:
            # Adjust grid size with Ctrl + wheel
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                delta = 1 if event.angleDelta().y() > 0 else -1
                self.scene_manager.current_scene.grid_size = max(8, self.scene_manager.current_scene.grid_size + delta * 4)
                self.update()
                
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if self.scene_manager and self.scene_manager.current_scene:
            # Reset view with Home key
            if event.key() == Qt.Key.Key_Home:
                self.scene_manager.current_scene.camera_offset = [0, 0]
                self.scene_manager.current_scene.grid_size = 32
                self.update()
            # Toggle grid with G key
            elif event.key() == Qt.Key.Key_G:
                self.scene_manager.current_scene.show_grid = not self.scene_manager.current_scene.show_grid
                self.update()
    
    def set_scene(self, scene):
        self.scene = scene
        self.update()
    
    def draw_grid(self, painter):
        grid_size = self.scene.grid_size
        width = self.width()
        height = self.height()
        
        # Set up grid pen
        grid_pen = QPen(QColor(100, 100, 100))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        
        # Draw vertical lines
        for x in range(0, width, grid_size):
            painter.drawLine(x, 0, x, height)
        
        # Draw horizontal lines
        for y in range(0, height, grid_size):
            painter.drawLine(0, y, width, y)
    
    def draw_entity(self, painter, entity):
        # Set entity color
        color = QColor(*entity.color)
        painter.setPen(QPen(color, 2))
        painter.setBrush(color)
        
        # Apply camera offset
        offset_x, offset_y = self.scene.camera_offset
        x = entity.position[0] + offset_x + self.width() // 2
        y = entity.position[1] + offset_y + self.height() // 2
        
        if isinstance(entity, Rectangle):
            painter.drawRect(x - entity.width // 2, y - entity.height // 2,
                           entity.width, entity.height)
        elif isinstance(entity, Circle):
            painter.drawEllipse(x - entity.radius, y - entity.radius,
                              entity.radius * 2, entity.radius * 2)
        elif isinstance(entity, Polygon):
            points = []
            for point in entity.points:
                points.append(QPoint(x + point[0], y + point[1]))
            painter.drawPolygon(points)
    
    def find_entity_at_position(self, pos):
        if not self.scene:
            return None
            
        scene_pos = self.view_to_scene_pos(pos)
        for entity in reversed(self.scene.entities):
            bounds = entity.get_bounds()
            if bounds.contains(scene_pos.x(), scene_pos.y()):
                return entity
        return None
    
    def view_to_scene_pos(self, pos):
        """Convert view coordinates to scene coordinates"""
        return QPoint(
            pos.x() - self.width() // 2 - self.scene.camera_offset[0],
            pos.y() - self.height() // 2 - self.scene.camera_offset[1]
        ) 