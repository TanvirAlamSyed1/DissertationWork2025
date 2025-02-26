# Importing the tkinter module
import tkinter as tk

# Styling the GUI
from tkinter import ttk

import Pages.mainScreen
class CompletionScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Completion Screen, we did it!")
        label.pack(padx=10, pady=10)
        switch_window_button = ttk.Button(
            self, text="Return to menu", command=lambda: controller.show_frame(Pages.mainScreen.MainPage)
        )
        switch_window_button.pack(side="bottom", fill=tk.X)