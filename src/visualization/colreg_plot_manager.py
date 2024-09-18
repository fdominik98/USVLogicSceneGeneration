import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ColregPlotManager():
    def __init__(self) -> None:
        root = tk.Tk()
        root.title("Matplotlib Plot with Tkinter Radio Buttons")

        # Create a frame for the plot
        plot_frame = ttk.Frame(root)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a Matplotlib figure and axes
        self.fig, self.ax = plt.subplots()

        # Embed the plot in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create a frame for the radio buttons
        control_frame = ttk.Frame(root)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a variable to store the selected function
        self.selected_function = tk.StringVar(value="Sine")

        # Create radio buttons
        ttk.Radiobutton(control_frame, text="Sine", variable=self.selected_function, value="Sine", command=self.update_plot).pack(anchor=tk.W)
        ttk.Radiobutton(control_frame, text="Cosine", variable=self.selected_function, value="Cosine", command=self.update_plot).pack(anchor=tk.W)
        ttk.Radiobutton(control_frame, text="Tangent", variable=self.selected_function, value="Tangent", command=self.update_plot).pack(anchor=tk.W)

        # Initialize the plot with the default function
        self.update_plot()

        # Start the Tkinter main loop
        root.mainloop()
        
        
    # Function to update the plot based on the radio button selection
    def update_plot(self):
        function = self.selected_function.get()
        self.ax.clear()
        
        x = np.linspace(0, 10, 100)
        if function == "Sine":
            y = np.sin(x)
        elif function == "Cosine":
            y = np.cos(x)
        elif function == "Tangent":
            y = np.tan(x)
        
        self.ax.plot(x, y)
        self.ax.set_title(f"Plot of {function}")
        self.ax.grid(True)
        
        # Refresh canvas to show updated plot
        self.canvas.draw()

