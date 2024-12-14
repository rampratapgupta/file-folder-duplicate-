import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import pandas as pd
import os
import time
from datetime import datetime
import multiprocessing  # Import multiprocessing

# Global Variables
mode = "file"  # Default mode
selected_file_or_folder = None
folder_mode_columns_to_disable = []
has_duplicates = False  # Track if duplicates are found
columns_to_check = []  # Columns selected for duplicate check
duplicate_count = 0  # Count of duplicates

# Splash screen function
def splash_screen():
    splash = tk.Tk()
    splash.title("Splash Screen")
    splash.geometry("480x330+480+280")
    splash.resizable(False, False)

    bg_color = 'lightblue'
    splash.config(bg=bg_color)

    splash_label = tk.Label(splash, text="Rampratap Gupta Application ", font=("Arial", 22, "bold"), fg="Red", bg=bg_color)
    splash_label.pack(pady=20)

    loading_label = tk.Label(splash, text="Loading... 0%", font=("Arial", 14), fg="green", bg=bg_color)
    loading_label.pack(pady=10)

    progressbar = ttk.Progressbar(splash, orient=tk.HORIZONTAL, length=300, mode="determinate")
    progressbar.pack(pady=10)

    def update_progress(progress):
        progressbar['value'] = progress
        loading_label.config(text=f"Loading... {progress}%")
        splash.update_idletasks()

    # Simulate loading process
    for i in range(101):
        update_progress(i)
        splash.after(20)  # Simulate a delay

    splash.destroy()

def hover_effect(widget, enter_bg, leave_bg):
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_bg))

def login():
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == "Rampratap" and password == "Ram@2001!!":
            login_window.destroy()
            main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("350x250")
    login_window.configure(bg="#E8F0F2")

    tk.Label(login_window, text="Username:", bg="#E8F0F2", font=("Arial", 12, "bold")).pack(pady=5)
    username_entry = tk.Entry(login_window, font=("Arial", 12))
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:", bg="#E8F0F2", font=("Arial", 12, "bold")).pack(pady=5)
    password_entry = tk.Entry(login_window, show="*", font=("Arial", 12))
    password_entry.pack(pady=5)

    login_button = tk.Button(
        login_window, text="Login", command=validate_login, bg="#0078D7", fg="white", font=("Arial", 12, "bold"), width=15
    )
    login_button.pack(pady=20)
    hover_effect(login_button, "#0053A5", "#0078D7")

    login_window.mainloop()

def main_app():
    global mode, selected_file_or_folder, has_duplicates, columns_to_check, duplicate_count

    def set_mode(selected_mode):
        global mode
        mode = selected_mode
        clear_data()

    def browse():
        global selected_file_or_folder
        if mode == "file":
            selected_file_or_folder = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")])
        else:
            selected_file_or_folder = filedialog.askdirectory()
        if selected_file_or_folder:
            find_button.config(state=tk.NORMAL)
            load_columns()

    def clear_data():
        global has_duplicates, columns_to_check, duplicate_count
        table.delete(*table.get_children())
        has_duplicates = False
        export_button.config(state=tk.DISABLED)
        find_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.DISABLED)
        columns_to_check.clear()
        duplicate_count = 0
        for widget in columns_frame.winfo_children():
            widget.destroy()

    def load_columns():
        if mode == "file":
            if selected_file_or_folder.endswith((".xlsx", ".csv")):
                df = pd.read_excel(selected_file_or_folder) if selected_file_or_folder.endswith(".xlsx") else pd.read_csv(selected_file_or_folder)
                for col in df.columns:
                    var = tk.BooleanVar(value=False)
                    checkbox = tk.Checkbutton(columns_frame, text=col, variable=var, bg="#F0F0F0", font=("Arial", 10))
                    checkbox.var = var
                    checkbox.pack(anchor="w")
                    columns_to_check.append((col, var))
                enable_column_checkboxes(True)  # Enable checkboxes for file mode
        else:
            enable_column_checkboxes(False)  # Disable checkboxes for folder mode

    def enable_column_checkboxes(enable):
        for widget in columns_frame.winfo_children():
            if isinstance(widget, tk.Checkbutton):
                widget.config(state=tk.NORMAL if enable else tk.DISABLED)

    def show_processing_message():
        processing_label = tk.Label(root, text="Please wait, processing...", bg="#F0F0F0", font=("Arial", 12, "italic"), fg="red")
        processing_label.pack(pady=5)
        root.update_idletasks()
        return processing_label

    def find_duplicates():
        global has_duplicates, duplicate_count
        if not selected_file_or_folder:
            messagebox.showwarning("No File/Folder Selected", "Please select a file or folder first!")
            return

        selected_columns = [col for col, var in columns_to_check if var.get()]
        if not selected_columns:
            messagebox.showwarning("No Columns Selected", "Please select at least one column to check for duplicates!")
            return

        progress_bar["value"] = 0
        progress_label.config(text="Processing: 0%")
        processing_label = show_processing_message()

        for i in range(1, 101):
            time.sleep(0.02)
            progress_bar["value"] = i
            progress_label.config(text=f"Processing: {i}%")
            root.update_idletasks()

        processing_label.destroy()

        if mode == "file":
            process_file(selected_file_or_folder, selected_columns)
        else:
            process_folder(selected_file_or_folder, selected_columns)

        if has_duplicates:
            export_button.config(state=tk.NORMAL)
            clear_button.config(state=tk.NORMAL)
            show_qty()  # Show duplicate count after processing
        else:
            messagebox.showinfo("No Duplicates", "No duplicate data found.")

    def process_file(file_path, selected_columns):
        global has_duplicates, duplicate_count
        if file_path.endswith(".xlsx") or file_path.endswith(".csv"):
            df = pd.read_excel(file_path) if file_path.endswith(".xlsx") else pd.read_csv(file_path)
            duplicates = df[df.duplicated(subset=selected_columns, keep=False)]
            if not duplicates.empty:
                has_duplicates = True
                duplicate_count += len(duplicates)
                show_duplicates_window(duplicates, file_path)
                populate_table(duplicates, file_path)
            else:
                messagebox.showinfo("No Duplicates", f"No duplicates found in {file_path}")
        else:
            messagebox.showerror("Invalid File", "Please select a valid Excel or CSV file.")

    def process_folder(folder_path, selected_columns):
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith((".xlsx", ".csv"))]
        
        # Using multiprocessing to process files in parallel
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        pool.starmap(process_file, [(file, selected_columns) for file in files])
        pool.close()
        pool.join()

    def show_duplicates_window(duplicates, file_name):
        duplicate_window = Toplevel(root)
        duplicate_window.title("Duplicate Data")
        duplicate_window.geometry("700x400")
        duplicate_window.configure(bg="#F0F0F0")

        tk.Label(duplicate_window, text=f"Duplicates from {os.path.basename(file_name)}", font=("Arial", 14, "bold"), bg="#F0F0F0").pack(pady=10)

        duplicates_table = ttk.Treeview(duplicate_window, columns=list(duplicates.columns), show="headings", height=15)
        duplicates_table.pack(pady=5, padx=10, fill="both", expand=True)

        for col in duplicates.columns:
            duplicates_table.heading(col, text=col)
            duplicates_table.column(col, anchor="center")

        for _, row in duplicates.iterrows():
            duplicates_table.insert("", "end", values=list(row))

    def show_qty():
        """Show total duplicate count in a new window."""
        qty_window = Toplevel(root)
        qty_window.title("Duplicate Count")
        qty_window.geometry("300x150")
        qty_window.configure(bg="#F0F0F0")

        tk.Label(qty_window, text=f"Total Duplicates Found: {duplicate_count}", font=("Arial", 14, "bold"), bg="#F0F0F0").pack(pady=30)

    def populate_table(duplicates, file_name):
        for idx, row in duplicates.iterrows():
            data = str(row.to_dict())
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            table.insert("", "end", values=(idx, data, file_name, current_time))

    def export_data():
        export_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if export_file:
            all_data = [table.item(item)["values"] for item in table.get_children()]
            df = pd.DataFrame(all_data, columns=["Index", "Data", "File Name", "Timestamp"])
            df.to_csv(export_file, index=False)
            messagebox.showinfo("Export Successful", "Duplicate data exported successfully.")

    def update_time():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label.config(text=f"Current Time: {current_time}")
        root.after(1000, update_time)

    def logout():
        root.destroy()
        login()

    def copy_data(event):
        selected_item = table.selection()
        if selected_item:
            data = table.item(selected_item)['values']
            copied_text = "\n".join([str(value) for value in data])
            root.clipboard_clear()
            root.clipboard_append(copied_text)
            messagebox.showinfo("Copied", "Data copied to clipboard")

    root = tk.Tk()
    root.title("Duplicate Finder")
    root.geometry("1000x700")
    root.config(bg="#F0F0F0")

    BUTTON_STYLE = {"padx": 10, "pady": 5, "bg": "#0078D7", "fg": "white", "font": ("Arial", 12, "bold")}
    LOGOUT_BUTTON_STYLE = {"padx": 10, "pady": 5, "bg": "red", "fg": "white", "font": ("Arial", 12, "bold")}

    top_frame = tk.Frame(root, bg="#F0F0F0")
    top_frame.pack(side=tk.TOP, pady=10)

    file_button = tk.Button(top_frame, text="File Mode", command=lambda: set_mode("file"), **BUTTON_STYLE)
    file_button.pack(side=tk.LEFT, padx=5)
    hover_effect(file_button, "#0053A5", "#0078D7")

    folder_button = tk.Button(top_frame, text="Folder Mode", command=lambda: set_mode("folder"), **BUTTON_STYLE)
    folder_button.pack(side=tk.LEFT, padx=5)
    hover_effect(folder_button, "#0053A5", "#0078D7")

    browse_button = tk.Button(top_frame, text="Browse", command=browse, **BUTTON_STYLE)
    browse_button.pack(side=tk.LEFT, padx=5)
    hover_effect(browse_button, "#0053A5", "#0078D7")

    find_button = tk.Button(top_frame, text="Find Duplicates", command=find_duplicates, state=tk.DISABLED, **BUTTON_STYLE)
    find_button.pack(side=tk.LEFT, padx=5)
    hover_effect(find_button, "#0053A5", "#0078D7")

    export_button = tk.Button(top_frame, text="Export Data", command=export_data, state=tk.DISABLED, **BUTTON_STYLE)
    export_button.pack(side=tk.LEFT, padx=5)
    hover_effect(export_button, "#0053A5", "#0078D7")

    clear_button = tk.Button(top_frame, text="Clear", command=clear_data, state=tk.DISABLED, **BUTTON_STYLE)
    clear_button.pack(side=tk.LEFT, padx=5)
    hover_effect(clear_button, "#0053A5", "#0078D7")

    logout_button = tk.Button(top_frame, text="Logout", command=logout, **LOGOUT_BUTTON_STYLE)
    logout_button.pack(side=tk.RIGHT, padx=5)
    hover_effect(logout_button, "#800000", "red")

    columns_frame = tk.Frame(root, bg="#F0F0F0", bd=2, relief=tk.GROOVE)
    columns_frame.pack(side=tk.TOP, pady=10, fill=tk.X, padx=10)

    tk.Label(columns_frame, text="Select Columns for Duplicate Check:", bg="#F0F0F0", font=("Arial", 10)).pack(anchor="w", padx=5, pady=2)

    table_frame = tk.Frame(root, bg="#F0F0F0")
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    columns = ("Index", "Data", "File Name", "Timestamp")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center")
    table.pack(fill=tk.BOTH, expand=True, pady=5)

    # Add context menu for copy option
    table.bind("<Button-3>", lambda event: copy_data(event))

    progress_frame = tk.Frame(root, bg="#F0F0F0")
    progress_frame.pack(side=tk.BOTTOM, pady=5)

    progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress_bar.pack(pady=5)
    progress_label = tk.Label(progress_frame, text="Processing: 0%", bg="#F0F0F0", font=("Arial", 10))
    progress_label.pack()

    time_label = tk.Label(root, text="", bg="#F0F0F0", font=("Arial", 10))
    time_label.pack(side=tk.BOTTOM, pady=5)

    # Footer at the bottom
    footer_label = tk.Label(root, text="© 2024 Rampratap Gupta | All rights reserved", bg="#F0F0F0", font=("Arial", 8), fg="gray")
    footer_label.pack(side=tk.BOTTOM, pady=5)

    update_time()
    root.mainloop()

# Run splash screen before the main application
splash_screen()
login()
