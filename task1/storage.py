import json
import os
from tkinter import messagebox

def save_tasks(filename, tasks):
    try:
        with open(filename, 'w') as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save tasks: {e}")

def load_tasks(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")
    return []
