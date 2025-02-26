# Importing the tkinter module
import tkinter as tk

# Styling the GUI
from tkinter import ttk
#import the next page
import Pages.welcomeScreen

class SidePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the Side Page")
        label.pack(padx=10, pady=10)
        canvas = tk.Canvas(self, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(self)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        button_frame = tk.Frame(toolbar)
        button_frame.pack(expand=True)

        buttons = [
            ("Load Folder"),
            ("Previous"),
            ("Next"),
            ("Save Annotations"),
            ("Clear Annotations")
        ]

        for text in buttons:
            tk.Button(button_frame, text=text).pack(side=tk.LEFT, padx=5, pady=5)

        annotation_type = ttk.Combobox(button_frame, values=["Rectangle", "Circle", "Freehand"])
        annotation_type.set("Rectangle")
        annotation_type.pack(side=tk.LEFT, padx=5, pady=5)
        annotation_type.bind("<<ComboboxSelected>>")

        canvas.bind("<ButtonPress-1>")
        canvas.bind("<B1-Motion>")
        canvas.bind("<ButtonRelease-1>")
        
        switch_window_button = tk.Button(
            self,
            text="Go to the Completion Screen",
            command=lambda: controller.show_frame(Pages.welcomeScreen.MainPage),
        )
        switch_window_button.pack(side="top", fill=tk.X)
        
        
        