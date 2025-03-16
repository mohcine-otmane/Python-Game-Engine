from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QSplitter, QMessageBox
from PyQt6.QtCore import Qt, QSize, QDir
import os
import json
import shutil
from pathlib import Path

from src.gui.scene_view import SceneView
from src.core.scene import Scene
from src.core.shapes import Rectangle, Circle, Polygon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Engine")
        self.setMinimumSize(QSize(800, 600))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create splitter for project explorer and scene view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Create project explorer
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("Project Explorer")
        splitter.addWidget(self.project_tree)
        
        # Create scene view
        self.scene_view = SceneView()
        splitter.addWidget(self.scene_view)
        
        # Set splitter sizes
        splitter.setSizes([200, 600])
        
        # Load default project
        self.load_default_project()
    
    def load_default_project(self):
        try:
            # Get the path to the default project
            default_project_path = Path("src/core/default_project")
            
            # Create directories if they don't exist
            for dir_name in ["scenes", "assets", "scripts"]:
                (default_project_path / dir_name).mkdir(parents=True, exist_ok=True)
            
            # Load project configuration
            project_config_path = default_project_path / "project.json"
            if project_config_path.exists():
                with open(project_config_path) as f:
                    project_config = json.load(f)
                    
                # Load main scene
                if project_config.get("scenes"):
                    main_scene_path = default_project_path / "scenes" / project_config["scenes"][0]
                    if main_scene_path.exists():
                        with open(main_scene_path) as f:
                            scene_data = json.load(f)
                            scene = Scene.from_dict(scene_data)
                            self.scene_view.set_scene(scene)
            
            # Update project explorer
            self.update_project_tree(default_project_path)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load default project: {str(e)}")
    
    def update_project_tree(self, project_path):
        self.project_tree.clear()
        root = QTreeWidgetItem(self.project_tree, ["Project"])
        
        # Add scenes folder
        scenes_item = QTreeWidgetItem(root, ["Scenes"])
        scenes_path = project_path / "scenes"
        if scenes_path.exists():
            for scene_file in scenes_path.glob("*.sc"):
                QTreeWidgetItem(scenes_item, [scene_file.name])
        
        # Add assets folder
        assets_item = QTreeWidgetItem(root, ["Assets"])
        assets_path = project_path / "assets"
        if assets_path.exists():
            for asset_file in assets_path.iterdir():
                QTreeWidgetItem(assets_item, [asset_file.name])
        
        # Add scripts folder
        scripts_item = QTreeWidgetItem(root, ["Scripts"])
        scripts_path = project_path / "scripts"
        if scripts_path.exists():
            for script_file in scripts_path.glob("*.py"):
                QTreeWidgetItem(scripts_item, [script_file.name])
        
        root.setExpanded(True)
        scenes_item.setExpanded(True) 