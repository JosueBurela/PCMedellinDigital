import sys
import os

# Asegurar que el directorio raíz esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import MainApp

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
