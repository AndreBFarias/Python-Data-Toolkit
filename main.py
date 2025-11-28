import os
import sys

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import DataToolkitApp

if __name__ == "__main__":
    # Ensure working directory is correct
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    app = DataToolkitApp()
    app.mainloop()
