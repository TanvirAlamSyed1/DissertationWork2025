# Importing the tkinter module
import tkinter as tk
# Styling the GUI
from tkinter import ttk
#Importing the next page
import Pages.sideScreen


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #Welcome label
        welcome_label = tk.Label(self, text="Welcome to the Melanoma Annotation Tool", font=("Arial", 24))
        welcome_label.pack(pady=50)
        #Description
        description = "This tool allows you to annotate skin lesion images.\nYou can load a folder of images and use various annotation types."
        desc_label = tk.Label(self, text=description, font=("Arial", 14))
        desc_label.pack(pady=20)
        # We use the switch_window_button in order to call the show_frame() method as a lambda function
        switch_window_button = tk.Button(
            self,
            text="Go to the Side Page",
            command=lambda: controller.show_frame(Pages.sideScreen.SidePage),
        )
        switch_window_button.pack(side="bottom")