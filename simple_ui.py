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
