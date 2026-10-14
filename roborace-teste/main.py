"""Ponto de entrada do RoboRace. Execute:  python main.py"""
import sys

try:
    import tkinter as tk
except ImportError:
    sys.exit("Tkinter não encontrado. No Linux, instale com: sudo apt install python3-tk")

from interface import App


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
