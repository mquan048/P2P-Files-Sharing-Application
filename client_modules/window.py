import tkinter as tk
from socket import *

def loginDisplay():
    return

def initWindow(APP_NAME, WIDTH, HEIGHT):
    window = tk.Tk()
    # Init basic parameters
    window.title(APP_NAME)
    window.geometry(f"{WIDTH}x{HEIGHT}")

    # Run the window
    window.mainloop()