import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from storage import load_tasks, save_tasks

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")

        # Data
        self.filename = "tasks.json"
        self.tasks = load_tasks(self.filename)

        # UI setup
        self.create_widgets()
        self.refresh_task_list()

    def create_widgets(self):
        title_label = tk.Label(
            self.root, text="📝 To-Do List Manager",
            font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#333"
        )
        title_label.pack(pady=15)

        # Input Frame
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(input_frame, text="Task:", font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.task_entry = tk.Entry(input_frame, width=40, font=("Arial", 11))
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)
        self.task_entry.bind('<Return>', lambda e: self.add_task())

        tk.Label(input_frame, text="Priority:", font=("Arial", 11), bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.priority_var = tk.StringVar(value="Medium")
        ttk.Combobox(input_frame, textvariable=self.priority_var,
                     values=["High", "Medium", "Low"], state="readonly",
                     width=10, font=("Arial", 10)).grid(row=0, column=3, padx=5)

        tk.Button(input_frame, text="➕ Add Task", command=self.add_task,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  padx=15, pady=5, cursor="hand2").grid(row=0, column=4, padx=10)

        # Filter Buttons
        filter_frame = tk.Frame(self.root, bg="#f0f0f0")
        filter_frame.pack(pady=5, padx=20, fill="x")

        tk.Label(filter_frame, text="Filter:", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.filter_var = tk.StringVar(value="All")
        for opt in ["All", "Active", "Completed"]:
            tk.Radiobutton(filter_frame, text=opt, variable=self.filter_var, value=opt,
                           command=self.refresh_task_list, bg="#f0f0f0",
                           font=("Arial", 10)).pack(side="left", padx=5)

        # Task List
        list_frame = tk.Frame(self.root, bg="white")
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.canvas = tk.Canvas(list_frame, bg="white", yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.canvas.yview)

        self.tasks_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.tasks_frame, anchor="nw")
        self.tasks_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="🗑️ Clear Completed", command=self.clear_completed,
                  bg="#f44336", fg="white", font=("Arial", 10),
                  padx=10, pady=5, cursor="hand2").pack(side="left", padx=5)

        self.stats_label = tk.Label(self.root, text="", font=("Arial", 9),
                                    bg="#f0f0f0", fg="#666")
        self.stats_label.pack(pady=5)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def add_task(self):
        text = self.task_entry.get().strip()
        if not text:
            messagebox.showwarning("Empty Task", "Please enter a task!")
            return

        task = {
            "id": len(self.tasks) + 1,
            "text": text,
            "priority": self.priority_var.get(),
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(task)
        self.task_entry.delete(0, tk.END)
        save_tasks(self.filename, self.tasks)
        self.refresh_task_list()

    def toggle_task(self, tid):
        for t in self.tasks:
            if t["id"] == tid:
                t["completed"] = not t["completed"]
        save_tasks(self.filename, self.tasks)
        self.refresh_task_list()

    def delete_task(self, tid):
        self.tasks = [t for t in self.tasks if t["id"] != tid]
        save_tasks(self.filename, self.tasks)
        self.refresh_task_list()

    def edit_task(self, tid):
        for t in self.tasks:
            if t["id"] == tid:
                win = tk.Toplevel(self.root)
                win.title("Edit Task")
                win.geometry("400x150")
                win.configure(bg="#f0f0f0")

                tk.Label(win, text="Edit Task:", font=("Arial", 11), bg="#f0f0f0").pack(pady=10)
                entry = tk.Entry(win, width=40, font=("Arial", 11))
                entry.insert(0, t["text"])
                entry.pack(pady=5)

                def save_edit():
                    new = entry.get().strip()
                    if new:
                        t["text"] = new
                        save_tasks(self.filename, self.tasks)
                        self.refresh_task_list()
                        win.destroy()
                    else:
                        messagebox.showwarning("Empty", "Task cannot be empty!")

                tk.Button(win, text="Save", command=save_edit,
                          bg="#4CAF50", fg="white", font=("Arial", 10),
                          padx=20, pady=5).pack(pady=10)
                entry.bind("<Return>", lambda e: save_edit())
                entry.focus()
                break

    def clear_completed(self):
        done = [t for t in self.tasks if t["completed"]]
        if not done:
            messagebox.showinfo("No Tasks", "No completed tasks to clear!")
            return
        if messagebox.askyesno("Confirm", f"Delete {len(done)} completed task(s)?"):
            self.tasks = [t for t in self.tasks if not t["completed"]]
            save_tasks(self.filename, self.tasks)
            self.refresh_task_list()

    def refresh_task_list(self):
        for w in self.tasks_frame.winfo_children():
            w.destroy()

        flt = self.filter_var.get()
        tasks = self.tasks
        if flt == "Active":
            tasks = [t for t in self.tasks if not t["completed"]]
        elif flt == "Completed":
            tasks = [t for t in self.tasks if t["completed"]]

        order = {"High": 0, "Medium": 1, "Low": 2}
        tasks.sort(key=lambda x: (x["completed"], order.get(x["priority"], 1)))

        for i, t in enumerate(tasks):
            self.create_task_widget(t, i)

        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t["completed"])
        active = total - done
        self.stats_label.config(text=f"Total: {total} | Active: {active} | Completed: {done}")

    def create_task_widget(self, t, idx):
        bg = "#f9f9f9" if idx % 2 == 0 else "white"
        frame = tk.Frame(self.tasks_frame, bg=bg, relief="solid", borderwidth=1)
        frame.pack(fill="x", padx=5, pady=2)

        var = tk.BooleanVar(value=t["completed"])
        tk.Checkbutton(frame, variable=var, command=lambda: self.toggle_task(t["id"]), bg=bg).pack(side="left", padx=5)

        colors = {"High": "#f44336", "Medium": "#ff9800", "Low": "#4CAF50"}
        tk.Label(frame, text="●", fg=colors.get(t["priority"], "#666"), bg=bg, font=("Arial", 16)).pack(side="left")

        style = ("Arial", 11, "overstrike" if t["completed"] else "normal")
        color = "#888" if t["completed"] else "#333"
        tk.Label(frame, text=t["text"], font=style, fg=color, bg=bg, anchor="w").pack(side="left", fill="x", expand=True, padx=10)

        btns = tk.Frame(frame, bg=bg)
        btns.pack(side="right", padx=5)

        tk.Button(btns, text="✏️", command=lambda: self.edit_task(t["id"]),
                  bg="#2196F3", fg="white", font=("Arial", 9),
                  padx=5, pady=2, cursor="hand2").pack(side="left", padx=2)
        tk.Button(btns, text="🗑️", command=lambda: self.delete_task(t["id"]),
                  bg="#f44336", fg="white", font=("Arial", 9),
                  padx=5, pady=2, cursor="hand2").pack(side="left", padx=2)
