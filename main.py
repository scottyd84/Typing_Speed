import sys

from PyQt6.QtWidgets import QApplication

from app import TypingApp


def main():
    app = QApplication(sys.argv)
    window = TypingApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
