import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
import psycopg2
import os
import shutil
from dotenv import load_dotenv

# ------------------ Load Environment Variables ------------------
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 5432))


# ------------------ Database Connection ------------------
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


# ------------------ Main App ------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Rooms App")
        self.root.geometry("800x650")
        self.root.configure(bg="#eef2f7")

        self.current_user = None

        # Create a "rooms" directory if not exists
        self.rooms_dir = "rooms"
        if not os.path.exists(self.rooms_dir):
            os.makedirs(self.rooms_dir)

        # ---- Global Styles ----
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 14), background="#eef2f7", foreground="#333")
        style.configure("TEntry", font=("Arial", 13), padding=5)
        style.configure("TButton", font=("Arial", 13, "bold"), padding=10, relief="raised", borderwidth=3)

        self.login_screen()

    # ------------------ Login Screen ------------------
    def login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="🔑 Login", font=("Arial", 20, "bold"), bg="#eef2f7").pack(pady=20)

        ttk.Label(self.root, text="Username").pack(pady=5)
        self.username_entry = ttk.Entry(self.root, width=25)
        self.username_entry.pack(pady=5)

        ttk.Label(self.root, text="Password").pack(pady=5)
        self.password_entry = ttk.Entry(self.root, show="*", width=25)
        self.password_entry.pack(pady=5)

        btn_frame = tk.Frame(self.root, bg="#eef2f7")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Login", command=self.login).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Signup", command=self.signup_screen).grid(row=0, column=1, padx=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            self.current_user = username
            self.main_app_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    # ------------------ Signup Screen ------------------
    def signup_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="📝 Signup", font=("Arial", 20, "bold"), bg="#eef2f7").pack(pady=20)

        ttk.Label(self.root, text="Choose Username").pack(pady=5)
        self.new_username_entry = ttk.Entry(self.root, width=25)
        self.new_username_entry.pack(pady=5)

        ttk.Label(self.root, text="Choose Password").pack(pady=5)
        self.new_password_entry = ttk.Entry(self.root, show="*", width=25)
        self.new_password_entry.pack(pady=5)

        btn_frame = tk.Frame(self.root, bg="#eef2f7")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Create Account", command=self.signup).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Back to Login", command=self.login_screen).grid(row=0, column=1, padx=10)

    def signup(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Account created successfully!")
            self.login_screen()
        except psycopg2.errors.UniqueViolation:
            messagebox.showerror("Error", "Username already exists")
            conn.rollback()
            conn.close()

    # ------------------ Main Screen After Login ------------------
    def main_app_screen(self):
        self.clear_screen()

        tk.Label(self.root, text=f"📂 Welcome {self.current_user}!", font=("Arial", 18, "bold"), bg="#eef2f7").pack(pady=15)

        btn_frame = tk.Frame(self.root, bg="#eef2f7")
        btn_frame.pack(pady=30)

        ttk.Button(btn_frame, text="➕ Add Room", command=self.add_room_screen).grid(row=0, column=0, padx=20, ipadx=20, ipady=20)
        ttk.Button(btn_frame, text="📂 Explore Rooms", command=self.explore_rooms_screen).grid(row=0, column=1, padx=20, ipadx=20, ipady=20)

        ttk.Button(self.root, text="Logout", command=self.logout).pack(pady=15)

    # ------------------ Add Room ------------------
    def add_room_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="➕ Add a New Room", font=("Arial", 20, "bold"), bg="#eef2f7").pack(pady=20)

        ttk.Label(self.root, text="Room Name").pack(pady=5)
        self.room_name_entry = ttk.Entry(self.root, width=25)
        self.room_name_entry.pack(pady=10)

        ttk.Label(self.root, text="Room Password").pack(pady=5)
        self.room_password_entry = ttk.Entry(self.root, width=25, show="*")
        self.room_password_entry.pack(pady=10)

        btn_frame = tk.Frame(self.root, bg="#eef2f7")
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Create", command=self.create_room).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Back", command=self.main_app_screen).grid(row=0, column=1, padx=10)

    def create_room(self):
        room_name = self.room_name_entry.get().strip()
        room_password = self.room_password_entry.get().strip()

        if not room_name or not room_password:
            messagebox.showwarning("Warning", "Room name and password cannot be empty")
            return

        room_path = os.path.join(self.rooms_dir, room_name)

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO rooms (name, creator, password) VALUES (%s, %s, %s)", 
                        (room_name, self.current_user, room_password))
            conn.commit()

            if not os.path.exists(room_path):
                os.makedirs(room_path)

            messagebox.showinfo("Success", f"Room '{room_name}' created successfully")
            self.main_app_screen()
        except psycopg2.errors.UniqueViolation:
            messagebox.showerror("Error", "Room already exists")
            conn.rollback()
        finally:
            conn.close()

    # ------------------ Explore Rooms ------------------
    def explore_rooms_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="📂 Explore Rooms", font=("Arial", 20, "bold"), bg="#eef2f7").pack(pady=20)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, creator FROM rooms")
        rooms = cur.fetchall()
        conn.close()

        rooms_frame = tk.Frame(self.root, bg="#eef2f7")
        rooms_frame.pack(pady=10)

        for i, (room, creator) in enumerate(rooms):
            btn = tk.Button(
                rooms_frame,
                text=f"{room}\n~ {creator}",
                width=18,
                height=6,
                font=("Arial", 12, "bold"),
                bg="#d9eaf7",
                relief="raised",
                command=lambda r=room: self.verify_room_password(r)
            )
            btn.grid(row=i // 3, column=i % 3, padx=15, pady=15)

        ttk.Button(self.root, text="Back", command=self.main_app_screen).pack(pady=15)

    # ------------------ Room Password Verification ------------------
    def verify_room_password(self, room_name):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM rooms WHERE name=%s", (room_name,))
        result = cur.fetchone()
        conn.close()

        if not result:
            messagebox.showerror("Error", "Room not found")
            return

        correct_password = result[0]
        entered_password = simpledialog.askstring("Room Password", f"Enter password for '{room_name}':", show="*")

        if entered_password == correct_password:
            self.open_room(room_name)
        else:
            messagebox.showerror("Error", "Incorrect password")

    # ------------------ Inside a Room ------------------
    def open_room(self, room_name):
        self.clear_screen()
        tk.Label(self.root, text=f"📁 Room: {room_name}", font=("Arial", 18, "bold"), bg="#eef2f7").pack(pady=15)

        room_path = os.path.join(self.rooms_dir, room_name)
        files = [f for f in os.listdir(room_path) if f.endswith(".txt")]

        files_frame = tk.Frame(self.root, bg="#eef2f7")
        files_frame.pack(pady=10)

        for i, file in enumerate(files):
            btn = tk.Button(
                files_frame,
                text=file,
                width=20,
                height=2,
                bg="#f1f1f1",
                font=("Arial", 11),
                command=lambda f=file: self.open_file(room_path, f)
            )
            btn.grid(row=i, column=0, pady=5)

        btn_frame = tk.Frame(self.root, bg="#eef2f7")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Delete Room", command=lambda: self.delete_room(room_name)).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Back", command=self.explore_rooms_screen).grid(row=0, column=1, padx=10)

    # ------------------ File Operations ------------------
    def open_file(self, room_path, filename):
        file_path = os.path.join(room_path, filename)
        self.clear_screen()

        tk.Label(self.root, text=f"📄 {filename}", font=("Arial", 16, "bold"), bg="#eef2f7").pack(pady=10)

        self.text_area = tk.Text(self.root, height=15, width=70, font=("Consolas", 12))
        self.text_area.pack(pady=10)

        with open(file_path, "r") as f:
            self.text_area.insert(tk.END, f.read())

        btn_frame = tk.Frame(self.root, bg="#eef2f7")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Save", command=lambda: self.save_file(file_path)).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Back", command=lambda: self.open_room(os.path.basename(room_path))).grid(row=0, column=1, padx=10)

    def save_file(self, file_path):
        with open(file_path, "w") as f:
            f.write(self.text_area.get(1.0, tk.END).strip())
        messagebox.showinfo("Saved", f"File '{os.path.basename(file_path)}' saved successfully!")

    # ------------------ Delete Room ------------------
    def delete_room(self, room_name):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete room '{room_name}'?")
        if not confirm:
            return

        room_path = os.path.join(self.rooms_dir, room_name)

        # Delete folder
        if os.path.exists(room_path):
            shutil.rmtree(room_path)

        # Delete from DB
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM rooms WHERE name=%s", (room_name,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", f"Room '{room_name}' deleted successfully")
        self.explore_rooms_screen()

    # ------------------ Logout ------------------
    def logout(self):
        self.current_user = None
        self.login_screen()

    # ------------------ Helper ------------------
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# ------------------ Run ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
