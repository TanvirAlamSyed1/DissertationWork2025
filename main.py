# Importing the tkinter module
import tkinter as tk
# Styling the GUI
from tkinter import ttk
from Pages.WelcomeScreen import WelcomePage
from Pages.MainScreen import  MainPage
# Allowing us to extend from the Tk class
class testClass(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Adding a title to the window
        self.wm_title("Annotation Tool")

        # creating a frame and assigning it to container
        container = tk.Frame(self, height=1200, width=1000)
        # specifying the region where the frame is packed in root
        container.pack(side="top", fill="both", expand=True)

        # configuring the location of the container using grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # We will now create a dictionary of frames
        self.frames = {}
        # we'll create the frames themselves later but let's add the components to the dictionary.
        for F in (WelcomePage, MainPage):
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
        

if __name__ == "__main__":
    testObj = testClass()
    testObj.mainloop()