import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from pathlib import Path

# =====================================
# DATABASE CONNECTION
# =====================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "library.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    category TEXT,
    quantity INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    student_name TEXT NOT NULL,
    issue_date TEXT,
    return_date TEXT,
    status TEXT DEFAULT 'Issued',
    FOREIGN KEY(book_id) REFERENCES books(id)
)
""")

conn.commit()

# =====================================
# LOGIN WINDOW
# =====================================

def login():
    username = username_entry.get()
    password = password_entry.get()

    if username == "Radha" and password == "radha1234":
        login_window.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


login_window = tk.Tk()
login_window.title("Smart Library - Admin Login")
login_window.geometry("400x300")
login_window.configure(bg="#e8eef5")
login_window.resizable(False, False)

tk.Label(
    login_window,
    text="SMART LIBRARY",
    font=("Arial", 20, "bold"),
    bg="#e8eef5",
    fg="#17365d"
).pack(pady=25)

tk.Label(login_window, text="Username", bg="#e8eef5").pack()
username_entry = tk.Entry(login_window, width=30)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password", bg="#e8eef5").pack()
password_entry = tk.Entry(login_window, width=30, show="*")
password_entry.pack(pady=5)

tk.Button(
    login_window,
    text="LOGIN",
    command=login,
    bg="#17365d",
    fg="white",
    width=20
).pack(pady=20)


# =====================================
# MAIN DASHBOARD
# =====================================

def open_dashboard():

    root = tk.Tk()
    root.title("Smart Library Management System")
    root.minsize(1000, 650)
    root.configure(bg="#F4F7FC")
    root.configure(bg="#edf2f7")

    # ---------- HEADER ----------

    header = tk.Frame(root, bg="#102A43", height=85)
    header.pack(fill="x")

    tk.Label(
        header,
        text="SMART LIBRARY MANAGEMENT SYSTEM",
        font=("Arial", 20, "bold"),
        bg="#17365d",
        fg="white"
    ).pack(pady=20)

    # ---------- NOTEBOOK ----------

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=15, pady=15)

    book_tab = tk.Frame(notebook, bg="#edf2f7")
    issue_tab = tk.Frame(notebook, bg="#edf2f7")
    stats_tab = tk.Frame(notebook, bg="#edf2f7")

    notebook.add(book_tab, text="Book Management")
    notebook.add(issue_tab, text="Issue / Return")
    notebook.add(stats_tab, text="Statistics & Recommendations")

    # =====================================
    # BOOK MANAGEMENT
    # =====================================

    tk.Label(
        book_tab,
        text="Book Management",
        font=("Arial", 17, "bold"),
        bg="#edf2f7"
    ).pack(pady=10)

    form = tk.Frame(book_tab, bg="#edf2f7")
    form.pack(pady=10)

    labels = ["Book ID", "Book Title", "Author", "Category", "Quantity"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(
            form,
            text=label,
            bg="#edf2f7",
            font=("Arial", 10)
        ).grid(row=i, column=0, padx=10, pady=5, sticky="w")

        entry = tk.Entry(form, width=35)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    id_entry, title_entry, author_entry, category_entry, quantity_entry = entries

    # ---------- TREEVIEW ----------

    columns = ("ID", "Title", "Author", "Category", "Quantity")

    tree = ttk.Treeview(
        book_tab,
        columns=columns,
        show="headings",
        height=10
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=160)

    tree.pack(fill="x", padx=20, pady=10)

    # ---------- LOAD BOOKS ----------

    def load_books(search=""):
        for item in tree.get_children():
            tree.delete(item)

        cursor.execute("""
            SELECT * FROM books
            WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
            ORDER BY id
        """, (f"%{search}%", f"%{search}%", f"%{search}%"))

        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

    # ---------- CLEAR FIELDS ----------

    def clear_fields():
        for entry in entries:
            entry.delete(0, tk.END)

    # ---------- ADD BOOK ----------

    def add_book():
        title = title_entry.get().strip()
        author = author_entry.get().strip()
        category = category_entry.get().strip()
        quantity = quantity_entry.get().strip()

        if not title or not author or not quantity:
            messagebox.showwarning("Warning", "Fill all required fields")
            return

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid non-negative quantity")
            return

        cursor.execute("""
            INSERT INTO books (title, author, category, quantity)
            VALUES (?, ?, ?, ?)
        """, (title, author, category, quantity))

        conn.commit()
        load_books()
        clear_fields()
        messagebox.showinfo("Success", "Book added successfully")

    # ---------- SELECT BOOK ----------

    def select_book(event):
        selected = tree.focus()

        if selected:
            values = tree.item(selected, "values")
            clear_fields()

            for entry, value in zip(entries, values):
                entry.insert(0, value)

    tree.bind("<<TreeviewSelect>>", select_book)

    # ---------- UPDATE BOOK ----------

    def update_book():
        book_id = id_entry.get().strip()

        if not book_id:
            messagebox.showwarning("Warning", "Select a book first")
            return

        try:
            quantity = int(quantity_entry.get())
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity")
            return

        try:
            cursor.execute("""
                UPDATE books
                SET title=?, author=?, category=?, quantity=?
                WHERE id=?
            """, (
                title_entry.get().strip(),
                author_entry.get().strip(),
                category_entry.get().strip(),
                quantity,
                int(book_id)
            ))
            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("Error", "Book not found")
                return

            load_books()
            clear_fields()
            messagebox.showinfo("Success", "Book updated successfully")

        except (ValueError, sqlite3.Error) as e:
            messagebox.showerror("Error", str(e))

    # ---------- DELETE BOOK ----------

    def delete_book():
        book_id = id_entry.get().strip()

        if not book_id:
            messagebox.showwarning("Warning", "Select a book first")
            return

        if not messagebox.askyesno("Confirm", "Delete this book?"):
            return

        try:
            cursor.execute(
                "SELECT COUNT(*) FROM loans WHERE book_id=? AND status='Issued'",
                (int(book_id),)
            )

            if cursor.fetchone()[0] > 0:
                messagebox.showerror(
                    "Error",
                    "This book has an active issue. Return it first."
                )
                return

            cursor.execute("DELETE FROM books WHERE id=?", (int(book_id),))
            conn.commit()
            load_books()
            clear_fields()
            messagebox.showinfo("Success", "Book deleted successfully")

        except (ValueError, sqlite3.Error) as e:
            messagebox.showerror("Error", str(e))

    # ---------- SEARCH BOOK ----------

    search_frame = tk.Frame(book_tab, bg="#edf2f7")
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="Search:", bg="#edf2f7").pack(side="left")

    search_entry = tk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=5)

    def search_book():
        load_books(search_entry.get().strip())

    tk.Button(search_frame, text="Search", command=search_book).pack(side="left", padx=5)
    tk.Button(search_frame, text="Show All", command=lambda: [search_entry.delete(0, tk.END), load_books()]).pack(side="left")

    # ---------- BOOK BUTTONS ----------

    button_frame = tk.Frame(book_tab, bg="#edf2f7")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Add Book", command=add_book, width=15, bg="#198754", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Update Book", command=update_book, width=15, bg="#0d6efd", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Delete Book", command=delete_book, width=15, bg="#dc3545", fg="white").pack(side="left", padx=5)
    tk.Button(button_frame, text="Clear", command=clear_fields, width=15).pack(side="left", padx=5)

    # =====================================
    # ISSUE AND RETURN SYSTEM
    # =====================================

    tk.Label(
        issue_tab,
        text="Book Issue & Return",
        font=("Arial", 18, "bold"),
        bg="#edf2f7"
    ).pack(pady=20)

    issue_form = tk.Frame(issue_tab, bg="#edf2f7")
    issue_form.pack(pady=20)

    tk.Label(issue_form, text="Book ID:", bg="#edf2f7").grid(row=0, column=0, padx=10, pady=10)
    issue_id = tk.Entry(issue_form, width=30)
    issue_id.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(issue_form, text="Student Name:", bg="#edf2f7").grid(row=1, column=0, padx=10, pady=10)
    student_entry = tk.Entry(issue_form, width=30)
    student_entry.grid(row=1, column=1, padx=10, pady=10)

    def issue_book():
        book_id = issue_id.get().strip()
        student = student_entry.get().strip()

        if not book_id or not student:
            messagebox.showwarning("Warning", "Enter Book ID and Student Name")
            return

        try:
            book_id = int(book_id)

            cursor.execute("SELECT quantity FROM books WHERE id=?", (book_id,))
            book = cursor.fetchone()

            if book is None:
                messagebox.showerror("Error", "Book not found")
                return

            if book[0] <= 0:
                messagebox.showerror("Error", "Book is not available")
                return

            cursor.execute("""
                INSERT INTO loans (book_id, student_name, issue_date, status)
                VALUES (?, ?, ?, 'Issued')
            """, (book_id, student, datetime.now().strftime("%Y-%m-%d")))

            cursor.execute("""
                UPDATE books SET quantity=quantity-1 WHERE id=?
            """, (book_id,))

            conn.commit()
            load_books()
            messagebox.showinfo("Success", "Book issued successfully")

        except ValueError:
            messagebox.showerror("Error", "Book ID must be a number")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def return_book():
        book_id = issue_id.get().strip()
        student = student_entry.get().strip()

        if not book_id or not student:
            messagebox.showwarning("Warning", "Enter Book ID and Student Name")
            return

        try:
            book_id = int(book_id)

            cursor.execute("""
                SELECT id FROM loans
                WHERE book_id=? AND student_name=? AND status='Issued'
                ORDER BY id LIMIT 1
            """, (book_id, student))

            loan = cursor.fetchone()

            if loan is None:
                messagebox.showerror("Error", "No active issue found")
                return

            cursor.execute("""
                UPDATE loans
                SET status='Returned', return_date=?
                WHERE id=?
            """, (datetime.now().strftime("%Y-%m-%d"), loan[0]))

            cursor.execute("""
                UPDATE books SET quantity=quantity+1 WHERE id=?
            """, (book_id,))

            conn.commit()
            load_books()
            messagebox.showinfo("Success", "Book returned successfully")

        except ValueError:
            messagebox.showerror("Error", "Invalid Book ID")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(
        issue_tab,
        text="ISSUE BOOK",
        command=issue_book,
        bg="#198754",
        fg="white",
        width=20
    ).pack(pady=10)

    tk.Button(
        issue_tab,
        text="RETURN BOOK",
        command=return_book,
        bg="#0d6efd",
        fg="white",
        width=20
    ).pack(pady=10)

    # =====================================
    # STATISTICS AND RECOMMENDATIONS
    # =====================================

    tk.Label(
        stats_tab,
        text="Library Statistics & Recommendations",
        font=("Arial", 17, "bold"),
        bg="#edf2f7"
    ).pack(pady=20)

    stats_text = tk.Text(
        stats_tab,
        width=90,
        height=25,
        font=("Arial", 12)
    )
    stats_text.pack(padx=20, pady=10)

    def show_statistics():
        stats_text.delete("1.0", tk.END)

        cursor.execute("SELECT COUNT(*) FROM books")
        total_titles = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM books")
        available_books = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM loans WHERE status='Issued'")
        issued_books = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM loans WHERE status='Returned'")
        returned_books = cursor.fetchone()[0]

        stats_text.insert(tk.END, "LIBRARY STATISTICS\n")
        stats_text.insert(tk.END, "=" * 50 + "\n\n")
        stats_text.insert(tk.END, f"Total Book Titles: {total_titles}\n")
        stats_text.insert(tk.END, f"Available Copies: {available_books}\n")
        stats_text.insert(tk.END, f"Currently Issued: {issued_books}\n")
        stats_text.insert(tk.END, f"Total Returned: {returned_books}\n\n")

        stats_text.insert(tk.END, "POPULAR BOOKS\n")
        stats_text.insert(tk.END, "-" * 50 + "\n")

        cursor.execute("""
            SELECT books.title, COUNT(loans.id) AS total
            FROM books
            LEFT JOIN loans ON books.id=loans.book_id
            GROUP BY books.id
            ORDER BY total DESC
            LIMIT 5
        """)

        popular = cursor.fetchall()

        if not popular:
            stats_text.insert(tk.END, "No books available.\n")
        else:
            for title, count in popular:
                stats_text.insert(tk.END, f"{title} - Borrowed {count} times\n")

        stats_text.insert(tk.END, "\nBOOK RECOMMENDATIONS\n")
        stats_text.insert(tk.END, "-" * 50 + "\n")

        cursor.execute("""
            SELECT category, COUNT(*) AS total
            FROM loans
            JOIN books ON loans.book_id=books.id
            GROUP BY category
            ORDER BY total DESC
            LIMIT 1
        """)

        favorite = cursor.fetchone()

        if favorite and favorite[0]:
            cursor.execute("""
                SELECT title, author FROM books
                WHERE category=? AND quantity > 0
                ORDER BY title
                LIMIT 5
            """, (favorite[0],))

            recommendations = cursor.fetchall()

            stats_text.insert(
                tk.END,
                f"Popular Category: {favorite[0]}\n\n"
            )

            if recommendations:
                for title, author in recommendations:
                    stats_text.insert(tk.END, f"• {title} by {author}\n")
            else:
                stats_text.insert(tk.END, "No available books in this category.\n")
        else:
            stats_text.insert(tk.END, "Issue some books to generate recommendations.\n")

    tk.Button(
        stats_tab,
        text="Refresh Statistics",
        command=show_statistics,
        bg="#17365d",
        fg="white",
        width=25
    ).pack(pady=10)

    load_books()
    show_statistics()

    # ---------- CLOSE APPLICATION ----------

    def close_app():
        conn.commit()
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()


# START APPLICATION

login_window.mainloop()
