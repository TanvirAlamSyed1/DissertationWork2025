# Importing the tkinter module
import tkinter as tk
# Styling the GUI
from tkinter import ttk
from Pages.WelcomeScreen import WelcomePage
from Pages.MainScreen import MainPage
from Pages.HelpScreen import HelpPage

# Allowing us to extend from the Tk class
class AnnotationApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Adding a title to the window
        self.wm_title("Annotation Tool")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # creating a frame and assigning it to container
        container = tk.Frame(self, height=1200, width=1000)
        # specifying the region where the frame is packed in root
        container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # We will now create a dictionary of frames
        self.frames = {}
        for F in (WelcomePage, MainPage,HelpPage):
            frame = F(container, self)
            # the windows class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Using a method to switch frames
        self.show_frame(WelcomePage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()
    
    def on_closing(self):
        # Check if any unsaved annotations
        current_frame = self.frames.get(MainPage)
        if current_frame and hasattr(current_frame, "annotations") and current_frame.annotations:
            if tk.messagebox.askyesno("Exit Confirmation", "You have unsaved annotations. Are you sure you want to exit?"):
                self.destroy()
            else:
                return
        else:
            self.destroy()


if __name__ == "__main__":
    testObj = AnnotationApp()
    testObj.mainloop()