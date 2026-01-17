# Student Management System using Python and MongoDB

## Project Description:

The Student Management System is a desktop-based application developed using **Python** to replace traditional manual record-keeping with a digital system.
It provides an **easy-to-use graphical user interface (GUI)** that allows users to manage student records efficiently.
The application uses **MongoDB** as a backend database to store and manage data securely and reliably.

The system supports all basic database operations such as **adding, viewing, searching, updating, deleting records**, and also allows **exporting data to CSV format**.

## Scenario Chosen:

**Student Management System**

This system is designed for educational institutions to manage student information such as:

* Student ID
* Name
* Age
* Course
* Email

It helps maintain accurate student records and reduces paperwork.


## Technologies Used:

* **Python** – Core programming language
* **Tkinter** – GUI development
* **MongoDB** – NoSQL database
* **PyMongo** – Python-MongoDB connectivity
* **CSV module** – Exporting records to CSV
* **PyCharm** – Development environment


## How to Run the Project:

### Step 1: Install Prerequisites

* Install **Python 3.x**
* Install **MongoDB Community Server**
* Install **PyCharm** or any Python IDE

---

### Step 2: Start MongoDB Server

Ensure MongoDB service is running on:

```
mongodb://localhost:27017/
```

You can start MongoDB using:

```bash
mongod
```

---

### Step 3: Install Required Python Libraries

Open terminal inside the project folder and run:

```bash
pip install pymongo
```

---

### Step 4: Project Structure

The project contains:

* `source_code/main.py` – Main GUI application  
* `mongodb_connection/mongodb_connection.py` – MongoDB connection script   
* `screenshots/` – GUI screenshots  
* `exported_data/students_data.csv` – Sample CSV file generated from the export feature  
* `requirements.txt` – Required libraries

---

### Step 5: Run the Application

Execute the main Python file:

```bash
python main.py
```

The GUI window will open and allow the user to:

* Add new student records
* View all stored records
* Search records using ID or Name
* Update existing records
* Delete records with confirmation
* Export records to CSV file

---

## Database Information

* **Database Name:** `student_management_db`
* **Collection Name:** `students`

---

## Conclusion

This project demonstrates the practical implementation of **Python GUI programming integrated with MongoDB**.
It provides a complete solution for managing student data digitally, improving efficiency, accuracy, and usability.

