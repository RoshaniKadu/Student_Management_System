import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import csv
import re
from datetime import datetime
import os
import platform
import subprocess

# ---------------- MongoDB Connection ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["student_db"]
collection = db["students"]
users = db["users"]

# Insert default admin if collection empty
if users.count_documents({}) == 0:
    users.insert_one({"username": "admin", "password": "admin123"})

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Student Management System")
root.geometry("1000x650")
root.config(bg="#e6f2ff")

# ---------------- Tkinter Variables ----------------
vars = {
    "sid": tk.StringVar(),
    "name": tk.StringVar(),
    "age": tk.StringVar(),
    "course": tk.StringVar(),
    "email": tk.StringVar(),
    "search": tk.StringVar(),
    "username": tk.StringVar(),
    "password": tk.StringVar()
}

# ---------------- Session List for New Entries ----------------
session_entries = []

# ---------------- Last Exported CSV ----------------
last_csv_file = ""

# ---------------- Validation Functions ----------------
def is_int(value):
    return value.isdigit()

def is_alpha(value):
    return value.replace(" ", "").isalpha()

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

def clear_fields():
    for v in vars.values():
        v.set("")

def confirm_action(action_name):
    return messagebox.askyesno("Confirm", f"Are you sure you want to {action_name}?")

# ---------------- Login Function ----------------
def login():
    uname = vars['username'].get()
    pwd = vars['password'].get()
    user = users.find_one({"username": uname, "password": pwd})
    if user:
        login_frame.pack_forget()
        main_frame.pack(fill=tk.BOTH, expand=True)
        refresh_session_table()
    else:
        messagebox.showerror("Error", "Invalid username or password")

# ---------------- CRUD Functions ----------------
def add_student():
    sid_input = vars['sid'].get()
    name = vars['name'].get()
    age_input = vars['age'].get()
    course = vars['course'].get()
    email = vars['email'].get()

    if not sid_input or not name:
        messagebox.showerror("Error", "ID and Name required")
        return
    if not is_int(sid_input):
        messagebox.showerror("Error", "ID must be numeric")
        return
    if not is_int(age_input):
        messagebox.showerror("Error", "Age must be numeric")
        return
    if not is_alpha(name):
        messagebox.showerror("Error", "Name must contain only letters")
        return
    if not is_alpha(course):
        messagebox.showerror("Error", "Course must contain only letters")
        return
    if not validate_email(email):
        messagebox.showerror("Error", "Invalid Email")
        return

    sid = int(sid_input)
    age = int(age_input)

    if collection.find_one({"sid": sid}):
        messagebox.showerror("Error", "Student ID already exists")
        return

    # Insert into MongoDB
    collection.insert_one({
        "sid": sid,
        "name": name,
        "age": age,
        "course": course,
        "email": email
    })

    # Add to session list
    session_entries.append({
        "sid": sid,
        "name": name,
        "age": age,
        "course": course,
        "email": email
    })

    refresh_session_table()
    messagebox.showinfo("Success", "Student Added Successfully")
    clear_fields()

# ---------------- Refresh Table for Current Session ----------------
def refresh_session_table():
    tree.delete(*tree.get_children())
    for s in session_entries:
        tree.insert('', 'end', values=(s['sid'], s['name'], s['age'], s['course'], s['email']))

# ---------------- Update Student ----------------
def update_student():
    sid_input = vars['sid'].get()
    if not sid_input:
        messagebox.showerror("Error", "Enter ID to update")
        return
    if not is_int(sid_input):
        messagebox.showerror("Error", "ID must be numeric")
        return
    sid = int(sid_input)

    student = collection.find_one({"sid": sid})
    if not student:
        messagebox.showerror("Error", "Student ID not found")
        return

    name = vars['name'].get()
    age_input = vars['age'].get()
    course = vars['course'].get()
    email = vars['email'].get()

    if not is_int(age_input):
        messagebox.showerror("Error", "Age must be numeric")
        return
    if not is_alpha(name):
        messagebox.showerror("Error", "Name must contain only letters")
        return
    if not is_alpha(course):
        messagebox.showerror("Error", "Course must contain only letters")
        return
    if not validate_email(email):
        messagebox.showerror("Error", "Invalid Email")
        return

    age = int(age_input)

    if confirm_action("update this student"):
        collection.update_one(
            {"sid": sid},
            {"$set": {
                "name": name,
                "age": age,
                "course": course,
                "email": email
            }}
        )
        # Update session list if exists
        for s in session_entries:
            if s['sid'] == sid:
                s.update({"name": name, "age": age, "course": course, "email": email})
        refresh_session_table()
        messagebox.showinfo("Success", "Student Updated Successfully")
        clear_fields()

# ---------------- Delete Student ----------------
def delete_student():
    sid_input = vars['sid'].get()
    if not sid_input:
        messagebox.showerror("Error", "Enter ID to delete")
        return
    if not is_int(sid_input):
        messagebox.showerror("Error", "ID must be numeric")
        return
    sid = int(sid_input)

    student = collection.find_one({"sid": sid})
    if not student:
        messagebox.showerror("Error", "Student ID not found")
        return

    if confirm_action("delete this student"):
        collection.delete_one({"sid": sid})
        # Remove from session list if exists
        global session_entries
        session_entries = [s for s in session_entries if s['sid'] != sid]
        refresh_session_table()
        messagebox.showinfo("Success", "Student Deleted Successfully")
        clear_fields()

# ---------------- Search Student ----------------
def search_student():
    query = vars['search'].get()
    tree.delete(*tree.get_children())
    if query == "":
        refresh_session_table()
        return
    sid = int(query) if is_int(query) else -1
    for s in collection.find({"$or": [
        {"sid": sid},
        {"name": {"$regex": query, "$options": "i"}},
        {"course": {"$regex": query, "$options": "i"}}
    ]}):
        tree.insert('', 'end', values=(s['sid'], s['name'], s['age'], s['course'], s['email']))

# ---------------- Export CSV ----------------
def export_csv():
    global last_csv_file
    last_csv_file = f"students_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(last_csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Age", "Course", "Email"])
        for s in collection.find():
            writer.writerow([s['sid'], s['name'], s['age'], s['course'], s['email']])
    messagebox.showinfo("Success", f"CSV Exported as {last_csv_file}")

# ---------------- Open CSV ----------------
def open_csv():
    global last_csv_file
    if last_csv_file == "":
        messagebox.showerror("Error", "No CSV exported yet!")
        return
    try:
        if platform.system() == "Windows":
            os.startfile(last_csv_file)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", last_csv_file])
        else:  # Linux
            subprocess.call(["xdg-open", last_csv_file])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open CSV file: {e}")

# ---------------- New Page Function ----------------
def new_page():
    clear_fields()
    session_entries.clear()
    refresh_session_table()
    vars['search'].set("")

# ---------------- GUI Frames ----------------
login_frame = tk.Frame(root, bg="#cce6ff", padx=50, pady=50)
login_frame.pack(fill=tk.BOTH, expand=True)
tk.Label(login_frame, text="LOGIN", font=("Arial", 16, "bold"), bg="#cce6ff").pack(pady=10)
tk.Label(login_frame, text="Username", bg="#cce6ff").pack()
tk.Entry(login_frame, textvariable=vars['username']).pack()
tk.Label(login_frame, text="Password", bg="#cce6ff").pack()
tk.Entry(login_frame, textvariable=vars['password'], show="*").pack(pady=10)
tk.Button(login_frame, text="Login", command=login, bg="#3399ff", fg="white", width=20).pack()

main_frame = tk.Frame(root, bg="#e6f2ff")

# Left Frame (Form)
form = tk.Frame(main_frame, bg="#cce6ff", padx=20, pady=20)
form.pack(side=tk.LEFT, fill=tk.Y)
fields = ['sid', 'name', 'age', 'course', 'email']
for i, f in enumerate(fields):
    tk.Label(form, text=f.upper(), bg="#cce6ff", font=("Arial", 11, "bold")).grid(row=i, column=0, pady=5, sticky="w")
    tk.Entry(form, textvariable=vars[f], width=25).grid(row=i, column=1, pady=5)

buttons = [
    ("Add", add_student),
    ("Update", update_student),
    ("Delete", delete_student),
    ("Clear Fields", clear_fields),
    ("Export CSV", export_csv),
    ("Open CSV", open_csv),
    ("New Page", new_page)
]
for i, (t, cmd) in enumerate(buttons):
    tk.Button(form, text=t, command=cmd, width=20, bg="#3399ff" if t not in ["New Page","Open CSV"] else "#ff9933" if t=="New Page" else "#ff6600", fg="white").grid(row=6+i, column=0, columnspan=2, pady=5)

# Right Frame (Table + Search)
right = tk.Frame(main_frame, padx=10, pady=10, bg="#e6f2ff")
right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

search_frame = tk.Frame(right, bg="#e6f2ff")
search_frame.pack(fill=tk.X, pady=5)
tk.Entry(search_frame, textvariable=vars['search'], width=30).pack(side=tk.LEFT, padx=5)
tk.Button(search_frame, text="Search", command=search_student, bg="#3399ff", fg="white").pack(side=tk.LEFT)
tk.Button(search_frame, text="Show All", command=refresh_session_table, bg="#33cc33", fg="white").pack(side=tk.LEFT, padx=5)

columns = ("ID", "Name", "Age", "Course", "Email")
tree = ttk.Treeview(right, columns=columns, show="headings")
for c in columns:
    tree.heading(c, text=c)
    tree.column(c, width=120)
tree.pack(fill=tk.BOTH, expand=True)

def select_student(event):
    selected = tree.focus()
    if selected:
        values = tree.item(selected, 'values')
        vars['sid'].set(values[0])
        vars['name'].set(values[1])
        vars['age'].set(values[2])
        vars['course'].set(values[3])
        vars['email'].set(values[4])

tree.bind("<ButtonRelease-1>", select_student)

root.mainloop()
