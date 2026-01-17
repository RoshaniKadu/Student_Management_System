import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import csv, re, os, platform, subprocess
from datetime import datetime

# ---------------- MongoDB Connection ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["student_db"]
collection = db["students"]
users = db["users"]

if users.count_documents({}) == 0:
    users.insert_one({"username": "admin", "password": "admin123"})

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Student Management System")
root.geometry("1000x650")
root.config(bg="#e6f2ff")

# ---------------- Variables ----------------
vars = {k: tk.StringVar() for k in
        ["sid","name","age","course","email","search","username","password"]}

session_entries = []
last_csv_file = ""

# ---------------- Helpers ----------------
def clear_fields():
    for v in vars.values():
        v.set("")

def confirm_action(action):
    return messagebox.askyesno("Confirm", f"Are you sure you want to {action}?")

def validate_student(sid, name, age, course, email):
    if not sid or not name:
        return "ID and Name required"
    if not sid.isdigit() or not age.isdigit():
        return "ID and Age must be numeric"
    if not name.replace(" ","").isalpha():
        return "Name must contain only letters"
    if not course.replace(" ","").isalpha():
        return "Course must contain only letters"
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return "Invalid Email"
    return None

# ---------------- Login ----------------
def login():
    if users.find_one({"username": vars["username"].get(),
                       "password": vars["password"].get()}):
        login_frame.pack_forget()
        main_frame.pack(fill=tk.BOTH, expand=True)
        refresh_session_table()
    else:
        messagebox.showerror("Error", "Invalid username or password")

# ---------------- CRUD ----------------
def add_student():
    data = {k: vars[k].get() for k in ["sid","name","age","course","email"]}
    error = validate_student(**data)
    if error:
        messagebox.showerror("Error", error)
        return

    data["sid"], data["age"] = int(data["sid"]), int(data["age"])

    if collection.find_one({"sid": data["sid"]}):
        messagebox.showerror("Error", "Student ID already exists")
        return

    collection.insert_one(data)
    session_entries.append(data)
    refresh_session_table()
    messagebox.showinfo("Success", "Student Added Successfully")
    clear_fields()

def update_student():
    sid = vars["sid"].get()
    if not sid.isdigit():
        messagebox.showerror("Error", "Enter valid ID")
        return

    if not collection.find_one({"sid": int(sid)}):
        messagebox.showerror("Error", "Student ID not found")
        return

    data = {k: vars[k].get() for k in ["name","age","course","email"]}
    error = validate_student(sid, **data)
    if error:
        messagebox.showerror("Error", error)
        return

    if confirm_action("update this student"):
        data["age"] = int(data["age"])
        collection.update_one({"sid": int(sid)}, {"$set": data})
        for s in session_entries:
            if s["sid"] == int(sid):
                s.update(data)
        refresh_session_table()
        messagebox.showinfo("Success", "Student Updated Successfully")
        clear_fields()

def delete_student():
    sid = vars["sid"].get()
    if not sid.isdigit():
        messagebox.showerror("Error", "Enter valid ID")
        return

    if not collection.find_one({"sid": int(sid)}):
        messagebox.showerror("Error", "Student ID not found")
        return

    if confirm_action("delete this student"):
        collection.delete_one({"sid": int(sid)})
        session_entries[:] = [s for s in session_entries if s["sid"] != int(sid)]
        refresh_session_table()
        messagebox.showinfo("Success", "Student Deleted Successfully")
        clear_fields()

# ---------------- Table ----------------
def refresh_session_table():
    tree.delete(*tree.get_children())
    for s in session_entries:
        tree.insert("", tk.END,
                    values=(s["sid"], s["name"], s["age"], s["course"], s["email"]))

def search_student():
    query = vars["search"].get()
    tree.delete(*tree.get_children())
    if not query:
        refresh_session_table()
        return
    sid = int(query) if query.isdigit() else -1
    for s in collection.find({"$or": [
        {"sid": sid},
        {"name": {"$regex": query, "$options": "i"}},
        {"course": {"$regex": query, "$options": "i"}}
    ]}):
        tree.insert("", tk.END,
                    values=(s["sid"], s["name"], s["age"], s["course"], s["email"]))

# ---------------- CSV ----------------
def export_csv():
    global last_csv_file
    last_csv_file = f"students_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with open(last_csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID","Name","Age","Course","Email"])
        for s in collection.find():
            writer.writerow([s[k] for k in ["sid","name","age","course","email"]])
    messagebox.showinfo("Success", f"CSV Exported as {last_csv_file}")

def open_csv():
    if not last_csv_file:
        messagebox.showerror("Error", "No CSV exported yet!")
        return
    try:
        if platform.system() == "Windows":
            os.startfile(last_csv_file)
        elif platform.system() == "Darwin":
            subprocess.call(["open", last_csv_file])
        else:
            subprocess.call(["xdg-open", last_csv_file])
    except:
        messagebox.showerror("Error", "Could not open CSV file")

def new_page():
    session_entries.clear()
    refresh_session_table()
    clear_fields()
    vars["search"].set("")

# ---------------- GUI Frames (UNCHANGED) ----------------
login_frame = tk.Frame(root, bg="#cce6ff", padx=50, pady=50)
login_frame.pack(fill=tk.BOTH, expand=True)

tk.Label(login_frame, text="LOGIN", font=("Arial",16,"bold"),
         bg="#cce6ff").pack(pady=10)
tk.Label(login_frame, text="Username", bg="#cce6ff").pack()
tk.Entry(login_frame, textvariable=vars["username"]).pack()
tk.Label(login_frame, text="Password", bg="#cce6ff").pack()
tk.Entry(login_frame, textvariable=vars["password"], show="*").pack(pady=10)
tk.Button(login_frame, text="Login", command=login,
          bg="#3399ff", fg="white", width=20).pack()

main_frame = tk.Frame(root, bg="#e6f2ff")

form = tk.Frame(main_frame, bg="#cce6ff", padx=20, pady=20)
form.pack(side=tk.LEFT, fill=tk.Y)

for i,f in enumerate(["sid","name","age","course","email"]):
    tk.Label(form, text=f.upper(), bg="#cce6ff",
             font=("Arial",11,"bold")).grid(row=i, column=0, pady=5, sticky="w")
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

for i,(t,cmd) in enumerate(buttons):
    tk.Button(form, text=t, command=cmd, width=20,
              bg="#3399ff" if t not in ["New Page","Open CSV"]
              else "#ff9933" if t=="New Page" else "#ff6600",
              fg="white").grid(row=6+i, column=0, columnspan=2, pady=5)

right = tk.Frame(main_frame, padx=10, pady=10, bg="#e6f2ff")
right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

search_frame = tk.Frame(right, bg="#e6f2ff")
search_frame.pack(fill=tk.X, pady=5)
tk.Entry(search_frame, textvariable=vars["search"],
         width=30).pack(side=tk.LEFT, padx=5)
tk.Button(search_frame, text="Search",
          command=search_student,
          bg="#3399ff", fg="white").pack(side=tk.LEFT)
tk.Button(search_frame, text="Show All",
          command=refresh_session_table,
          bg="#33cc33", fg="white").pack(side=tk.LEFT, padx=5)

columns = ("ID","Name","Age","Course","Email")
tree = ttk.Treeview(right, columns=columns, show="headings")
for c in columns:
    tree.heading(c, text=c)
    tree.column(c, width=120)
tree.pack(fill=tk.BOTH, expand=True)

def select_student(event):
    item = tree.focus()
    if item:
        for k,v in zip(["sid","name","age","course","email"],
                       tree.item(item,"values")):
            vars[k].set(v)

tree.bind("<ButtonRelease-1>", select_student)

root.mainloop()
