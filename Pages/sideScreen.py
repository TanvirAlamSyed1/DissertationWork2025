# Importing the tkinter module
import tkinter as tk

# Styling the GUI
from tkinter import ttk
#import the next page
import Pages.completionScreen

class SidePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the Side Page")
        label.pack(padx=10, pady=10)

        switch_window_button = tk.Button(
            self,
            text="Go to the Completion Screen",
            command=lambda: controller.show_frame(Pages.completionScreen.CompletionScreen),
        )
        switch_window_button.pack(side="bottom", fill=tk.X)