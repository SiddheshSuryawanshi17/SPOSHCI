import tkinter as tk
from tkinter import messagebox

def on_button_click():
    """Function to be called when the button is clicked."""
    user_input = entry.get().strip()  # Get and trim text from the entry widget
    if user_input:
        messagebox.showinfo("Greeting", f"Hello, {user_input}!")
    else:
        messagebox.showwarning("Warning", "Please enter your name.")

# 1. Create the main window
root = tk.Tk()
root.title("Simple UI Example")
root.geometry("400x200")  # Set initial window size

# 2. Add widgets to the window

# Label
label = tk.Label(root, text="Enter your name:", font=("Arial", 12))
label.pack(pady=10)  # Add padding for better spacing

# Entry (text input field)
entry = tk.Entry(root, width=30, font=("Arial", 11))
entry.pack(pady=5)

# Button
button = tk.Button(root, text="Greet Me", command=on_button_click, font=("Arial", 11))
button.pack(pady=10)

# 3. Start the Tkinter event loop
root.mainloop()

"""
Tkinter setup for Python (installed via apt on Ubuntu)
------------------------------------------------------

Step 1 — Check if Tkinter is already installed:
    python3 -m tkinter

    - If a small blank window titled "Tk" appears, Tkinter is working.
    - If you get the error:
        ModuleNotFoundError: No module named '_tkinter'
      then continue to Step 2.

Step 2 — Install Tkinter package:
    sudo apt update
    sudo apt install python3-tk

    This installs both '_tkinter' and the underlying Tcl/Tk libraries.

Step 3 — Verify installation:
    python3 -m tkinter

    You should now see a small GUI window titled "Tk", confirming Tkinter is working.

Step 4 — Run your Python GUI program:
    python3 simple_ui.py

    or any other Tkinter-based Python script.

Summary Table
--------------
| Step | Command                       | Purpose                    |
|------|--------------------------------|-----------------------------|
| 1    | python3 -m tkinter             | Check if Tkinter works     |
| 2    | sudo apt install python3-tk    | Install Tkinter support    |
| 3    | python3 -m tkinter             | Verify by opening a window |
| 4    | python3 your_script.py         | Run your GUI program       |

Note:
Tkinter will work with any Python version installed via apt on Ubuntu
once the 'python3-tk' package is installed.
"""
