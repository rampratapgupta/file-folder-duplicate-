import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import pandas as pd
import os
import time
from datetime import datetime
import pyperclip  # Module to handle clipboard operations

# Global Variables
mode = "file"  # Default mode
selected_file_or_folder = None
has_duplicates = False  # Track if duplicates are found

# Splash screen function
def splash_screen():
    splash = tk.Tk()
    splash.title("Splash Screen")
    splash.geometry("480x330+480+280")
    splash.resizable(False, False)

    bg_color = 'lightblue'
    splash.config(bg=bg_color)

    splash_label = tk.Label(splash, text="Rampratap Gupta", font=("Arial", 28, "bold"), fg="Red", bg=bg_color)
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

# Dummy login credentials
USERNAME = "Rampratap"
PASSWORD = "Ram@2001!!"

def hover_effect(widget, enter_bg, leave_bg):
    """Apply hover effect to buttons."""
    widget.bind("<Enter>", lambda e: widget.config(bg=enter_bg))
    widget.bind("<Leave>", lambda e: widget.config(bg=leave_bg))

def login():
    """Login window to authenticate the user."""
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == USERNAME and password == PASSWORD:
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
    """Main application window for duplicate detection."""
    global mode, selected_file_or_folder, has_duplicates

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

    def clear_data():
        global has_duplicates
        table.delete(*table.get_children())
        has_duplicates = False
        export_button.config(state=tk.DISABLED)
        find_button.config(state=tk.DISABLED)
        clear_button.config(state=tk.DISABLED)
        copy_button.config(state=tk.DISABLED)

    def show_processing_message():
        processing_label = tk.Label(root, text="Please wait, processing...", bg="#F0F0F0", font=("Arial", 12, "italic"), fg="red")
        processing_label.pack(pady=5)
        root.update_idletasks()
        return processing_label

    def find_duplicates():
        global has_duplicates
        if not selected_file_or_folder:
            messagebox.showwarning("No File/Folder Selected", "Please select a file or folder first!")
            return

        # Start showing processing message only after we begin the actual check
        processing_label = show_processing_message()

        progress_bar["value"] = 0
        progress_label.config(text="Processing: 0%")
        root.update_idletasks()

        for i in range(1, 101):
            time.sleep(0.02)
            progress_bar["value"] = i
            progress_label.config(text=f"Processing: {i}%")
            root.update_idletasks()

        processing_label.destroy()  # Remove the processing message once done.

        if mode == "file":
            process_file(selected_file_or_folder)
        else:
            process_folder(selected_file_or_folder)

        # Check completion and show appropriate message
        if has_duplicates:
            export_button.config(state=tk.NORMAL)
            clear_button.config(state=tk.NORMAL)
            copy_button.config(state=tk.NORMAL)
            messagebox.showinfo("Checking Complete", "Duplicate check complete! Duplicates found.")
        else:
            messagebox.showinfo("Checking Complete", "Duplicate check complete! No duplicates found.")

    def process_file(file_path):
        global has_duplicates
        if file_path.endswith(".xlsx") or file_path.endswith(".csv"):
            df = pd.read_excel(file_path) if file_path.endswith(".xlsx") else pd.read_csv(file_path)
            duplicates = df[df.duplicated(keep=False)]
            if not duplicates.empty:
                has_duplicates = True
                show_duplicates_window(duplicates, file_path)
                populate_table(duplicates, file_path)
            else:
                messagebox.showinfo("No Duplicates", f"No duplicates found in {file_path}")
        else:
            messagebox.showerror("Invalid File", "Please select a valid Excel or CSV file.")

    def process_folder(folder_path):
        """Process all files in the selected folder and its subfolders."""
        files = []
        for root_dir, dirs, files_in_dir in os.walk(folder_path):
            for file in files_in_dir:
                if file.endswith((".xlsx", ".csv")):
                    files.append(os.path.join(root_dir, file))

        # Process each file found in the folder or subfolders
        for file in files:
            process_file(file)

    def show_duplicates_window(duplicates, file_name):
        """Show duplicate data in a separate window."""
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

    def populate_table(duplicates, file_name):
        folder_name = os.path.basename(os.path.dirname(file_name))  # Extract folder name
        for idx, row in duplicates.iterrows():
            data = str(row.to_dict())
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            table.insert("", "end", values=(idx, data, file_name, folder_name, current_time))

    def export_data():
        export_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if export_file:
            all_data = [table.item(item)["values"] for item in table.get_children()]
            df = pd.DataFrame(all_data, columns=["Index", "Data", "File Name", "Folder Name", "Timestamp"])
            df.to_csv(export_file, index=False)
            messagebox.showinfo("Export Successful", "Duplicate data exported successfully.")

    def copy_selected_data(event=None):
        selected_items = table.selection()
        if selected_items:
            copied_data = []
            for item in selected_items:
                row_values = table.item(item)["values"]
                copied_data.append("\t".join(str(value) for value in row_values))

            # Join the rows with newline and copy to clipboard
            pyperclip.copy("\n".join(copied_data))
            messagebox.showinfo("Data Copied", "Selected data has been copied to the clipboard.")
        else:
            messagebox.showwarning("No Selection", "Please select rows to copy.")

    def right_click_menu(event):
        right_click_menu = tk.Menu(root, tearoff=0)
        right_click_menu.add_command(label="Copy Selected Data", command=copy_selected_data)
        right_click_menu.post(event.x_root, event.y_root)

    def update_time():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label.config(text=f"Date & Time: {current_time}")
        root.after(1000, update_time)

    def logout():
        root.destroy()
        login()

    def change_credentials():
        def verify_old_credentials():
            old_username = old_username_entry.get()
            old_password = old_password_entry.get()

            if old_username == USERNAME and old_password == PASSWORD:
                change_window.destroy()
                change_username_password()
            else:
                messagebox.showerror("Invalid Credentials", "Old Username or Password is incorrect.")

        change_window = Toplevel(root)
        change_window.title("Change Credentials")
        change_window.geometry("350x250")

        tk.Label(change_window, text="Old Username:", font=("Arial", 12)).pack(pady=5)
        old_username_entry = tk.Entry(change_window, font=("Arial", 12))
        old_username_entry.pack(pady=5)

        tk.Label(change_window, text="Old Password:", font=("Arial", 12)).pack(pady=5)
        old_password_entry = tk.Entry(change_window, show="*", font=("Arial", 12))
        old_password_entry.pack(pady=5)

        verify_button = tk.Button(change_window, text="Verify", command=verify_old_credentials, bg="#0078D7", fg="white", font=("Arial", 12))
        verify_button.pack(pady=20)

    def change_username_password():
        def update_credentials():
            new_username = new_username_entry.get()
            new_password = new_password_entry.get()

            if new_username and new_password:
                global USERNAME, PASSWORD
                USERNAME = new_username
                PASSWORD = new_password
                messagebox.showinfo("Credentials Updated", "Username and Password updated successfully!")
                settings_window.destroy()
            else:
                messagebox.showerror("Error", "Please fill in both fields.")

        settings_window = Toplevel(root)
        settings_window.title("Change Username/Password")
        settings_window.geometry("350x250")

        tk.Label(settings_window, text="New Username:", font=("Arial", 12)).pack(pady=5)
        new_username_entry = tk.Entry(settings_window, font=("Arial", 12))
        new_username_entry.pack(pady=5)

        tk.Label(settings_window, text="New Password:", font=("Arial", 12)).pack(pady=5)
        new_password_entry = tk.Entry(settings_window, show="*", font=("Arial", 12))
        new_password_entry.pack(pady=5)

        update_button = tk.Button(settings_window, text="Update", command=update_credentials, bg="#0078D7", fg="white", font=("Arial", 12))
        update_button.pack(pady=20)

    root = tk.Tk()
    root.title("Duplicate Finder")
    root.geometry("1200x1000")
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

    clear_button = tk.Button(top_frame, text="Clear Data", command=clear_data, state=tk.DISABLED, **BUTTON_STYLE)
    clear_button.pack(side=tk.LEFT, padx=5)
    hover_effect(clear_button, "#0053A5", "#0078D7")

    copy_button = tk.Button(top_frame, text="Copy Selected Data", command=copy_selected_data, state=tk.DISABLED, **BUTTON_STYLE)
    copy_button.pack(side=tk.LEFT, padx=5)
    hover_effect(copy_button, "#0053A5", "#0078D7")

    logout_button = tk.Button(root, text="Logout", command=logout, **LOGOUT_BUTTON_STYLE)
    logout_button.pack(side=tk.BOTTOM, pady=10)
    hover_effect(logout_button, "#800000", "red")

    settings_button = tk.Button(root, text="Change Username/Password", command=change_credentials, **BUTTON_STYLE)
    settings_button.pack(side=tk.BOTTOM, pady=10)
    hover_effect(settings_button, "#0053A5", "#0078D7")

    table_frame = tk.Frame(root, bg="#F0F0F0")
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20)

    columns = ("Index", "Data", "File Name", "Folder Name", "Timestamp")
    table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center")

    table.pack(fill=tk.BOTH, expand=True)

    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode="determinate")
    progress_bar.pack(pady=20)

    progress_label = tk.Label(root, text="Processing: 0%", font=("Arial", 12, "bold"))
    progress_label.pack(pady=5)

    time_label = tk.Label(root, text="", font=("Arial", 10), bg="#F0F0F0")
    time_label.pack(side=tk.BOTTOM)

    update_time()
    root.bind("<Button-3>", right_click_menu)  # Bind right-click

        # Footer at the bottom
    footer_label = tk.Label(root, text="© 2024 Rampratap Gupta | All rights reserved ! Version- 2.9", bg="#F0F0F0", font=("Arial", 8, "bold"), fg="gray")
    footer_label.pack(side=tk.BOTTOM, pady=5)

    root.mainloop()

# Show splash screen and then launch the login
splash_screen()
login()
