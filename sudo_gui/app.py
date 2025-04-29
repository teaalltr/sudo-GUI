import sys
from PyQt6.QtWidgets import QApplication
from .main_window import SudoGUI

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("sudoers-safe-edit")
    app.setOrganizationName("ExampleOrg")
    win = SudoGUI()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":      # allows `python app.py`
    main()
