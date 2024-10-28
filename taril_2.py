import tkinter as tk
from tkinter import filedialog
import subprocess
from PIL import Image, ImageTk


def run_script():
    script_path = script_entry.get()
    if script_path:
        result = subprocess.run(['python', script_path],
                                capture_output=True, text=True)
        output_text.config(state='normal')
        output_text.delete('1.0', tk.END)
        output_text.insert(tk.END, result.stdout)
        output_text.config(state='disabled')

        # Check if result images exist
        try:
            image_path1 = "result_image.jpg"
            image1 = Image.open(image_path1)
            image1.thumbnail((300, 300))  # Resize image if necessary
            photo1 = ImageTk.PhotoImage(image1)
            image_label1.config(image=photo1)
            image_label1.image = photo1  # Keep reference to prevent garbage collection
            canvas1.create_text(20, 20, anchor="nw",
                                text="Image 1", fill="white")

            image_path2 = "Original_Image.jpg"
            image2 = Image.open(image_path2)
            image2.thumbnail((300, 300))  # Resize image if necessary
            photo2 = ImageTk.PhotoImage(image2)
            image_label2.config(image=photo2)
            image_label2.image = photo2  # Keep reference to prevent garbage collection
            canvas2.create_text(20, 20, anchor="nw",
                                text="Image 2", fill="white")
        except FileNotFoundError:
            image_label1.config(image=None)
            image_label2.config(image=None)


def browse_script():
    file_path = filedialog.askopenfilename(
        filetypes=[("Python files", "*.py")])
    if file_path:
        script_entry.delete(0, tk.END)
        script_entry.insert(tk.END, file_path)


# Create the main window
window = tk.Tk()
window.title("Python Script Runner")

# Script path entry
script_label = tk.Label(window, text="Script Path:")
script_label.grid(row=0, column=0, padx=10, pady=5)
script_entry = tk.Entry(window, width=50)
script_entry.grid(row=0, column=1, padx=10, pady=5)
browse_button = tk.Button(window, text="Browse", command=browse_script)
browse_button.grid(row=0, column=2, padx=5, pady=5)

# Run button
run_button = tk.Button(window, text="Run Script", command=run_script)
run_button.grid(row=1, column=2, pady=10)

# Output text area
output_label = tk.Label(window, text="Output:")
output_label.grid(row=2, column=0, padx=10, pady=5)
output_text = tk.Text(window, width=60, height=20, state='disabled')
output_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# Image labels and their corresponding labels
image_frame1 = tk.Frame(window, bd=2, relief="groove")
image_frame1.grid(row=4, column=1, padx=10, pady=5)
canvas1 = tk.Canvas(image_frame1, width=300, height=300, bg="black")
canvas1.pack()
image_label1 = canvas1.create_image(0, 0, anchor="nw")

image_frame2 = tk.Frame(window, bd=2, relief="groove")
image_frame2.grid(row=4, column=2, padx=10, pady=5)
canvas2 = tk.Canvas(image_frame2, width=300, height=300, bg="black")
canvas2.pack()
image_label2 = canvas2.create_image(0, 0, anchor="nw")

window.mainloop()
