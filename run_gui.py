import flet as ft
import sys
import os

# Add the project root to the Python path to allow imports from gui and other modules
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now that the path is set up, we can import from the gui module
from gui.app import main as gui_main

def main():
    ft.app(target=gui_main)

if __name__ == "__main__":
    main() 