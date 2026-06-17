import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import subprocess
import sys
from datetime import datetime

# ──────────────────────────────────────────────
#  DATABASE SETUP
# ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("inventory.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            category TEXT    NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            price    REAL    NOT NULL DEFAULT 0.0,
            added_on TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect("inventory.db")

# ──────────────────────────────────────────────
#  COLOUR & FONT TOKENS
# ──────────────────────────────────────────────
BG        = "#1C1C2E"
PANEL     = "#2A2A40"
ACCENT    = "#7C5CBF"
ACCENT2   = "#A17CF5"
DANGER    = "#E05C5C"
SUCCESS   = "#4CAF82"
TEXT      = "#EAEAF4"
SUBTEXT   = "#9090B0"
ROW_A     = "#22223A"
ROW_B     = "#1C1C2E"
LOW_STOCK = 5

FONT_HEAD  = ("Segoe UI", 22, "bold")
FONT_LABEL = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 9)

# ──────────────────────────────────────────────
#  MAIN APPLICATION
# ──────────────────────────────────────────────
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1100x700")
        self.minsize(900, 580)
        self.configure(bg=BG)
        init_db()
        self._build_ui()
        self.load_products()

    # ── UI SKELETON ──────────────────────────
    def _build_ui(self):
        self._build_header()
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._build_form(main)
        self._build_table(main)
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=PANEL, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="📦  Inventory Manager", font=FONT_HEAD,
                 bg=PANEL, fg=ACCENT2).pack(side="left", padx=20, pady=12)
        sf = tk.Frame(hdr, bg=PANEL)
        sf.pack(side="right", padx=20, pady=14)
        tk.Label(sf, text="Search:", font=FONT_LABEL, bg=PANEL, fg=SUBTEXT).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.load_products())
        se = tk.Entry(sf, textvariable=self.search_var, font=FONT_LABEL,
                      bg="#35355A", fg=TEXT, insertbackground=TEXT,
                      relief="flat", width=22)
        se.pack(side="left", padx=(6, 0), ipady=4)

    def _build_form(self, parent):
        frm = tk.LabelFrame(parent, text="  Add / Update Product  ",
                            font=FONT_BOLD, bg=PANEL, fg=ACCENT2,
                            bd=0, labelanchor="nw")
        frm.pack(fill="x", pady=(12, 8))

        fields = [
            ("Product Name", "name_var", 30),
            ("Category",     "cat_var",  20),
            ("Quantity",     "qty_var",  10),
            ("Price (Rs.)",  "price_var",12),
        ]

        inner = tk.Frame(frm, bg=PANEL)
        inner.pack(fill="x", padx=12, pady=10)

        for col, (label, attr, width) in enumerate(fields):
            tk.Label(inner, text=label, font=FONT_SMALL, bg=PANEL,
                     fg=SUBTEXT).grid(row=0, column=col*2, padx=(12,2), sticky="w")
            var = tk.StringVar()
            setattr(self, attr, var)
            ent = tk.Entry(inner, textvariable=var, font=FONT_LABEL,
                           bg="#35355A", fg=TEXT, insertbackground=TEXT,
                           relief="flat", width=width)
            ent.grid(row=1, column=col*2, padx=(12,2), ipady=5, sticky="w")

        self.selected_id = None

        # ── ROW 1 buttons: CRUD ──
        btn_frame1 = tk.Frame(frm, bg=PANEL)
        btn_frame1.pack(anchor="w", padx=12, pady=(8, 2))
        self._btn(btn_frame1, "➕ Add Product",  self.add_product,    ACCENT).pack(side="left", padx=4)
        self._btn(btn_frame1, "✏️ Update",        self.update_product, SUCCESS).pack(side="left", padx=4)
        self._btn(btn_frame1, "🗑 Delete",         self.delete_product, DANGER).pack(side="left", padx=4)
        self._btn(btn_frame1, "🔄 Clear",          self.clear_form,     SUBTEXT).pack(side="left", padx=4)

        # ── ROW 2 buttons: Import/Export/Charts ──
        btn_frame2 = tk.Frame(frm, bg=PANEL)
        btn_frame2.pack(anchor="w", padx=12, pady=(2, 10))
        self._btn(btn_frame2, "📂 Import CSV",    self.import_csv,     "#4A7C59").pack(side="left", padx=4)
        self._btn(btn_frame2, "📤 Export CSV",    self.export_csv,     "#5C8FBF").pack(side="left", padx=4)
        self._btn(btn_frame2, "📊 Show Charts",   self.show_charts,    "#A17CF5").pack(side="left", padx=4)

    def _btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, font=FONT_SMALL,
                         bg=color, fg="white", relief="flat",
                         padx=10, pady=5, cursor="hand2",
                         activebackground=ACCENT2, activeforeground="white")

    def _build_table(self, parent):
        cols = ("ID", "Name", "Category", "Quantity", "Price (Rs.)", "Added On", "Status")
        tf = tk.Frame(parent, bg=BG)
        tf.pack(fill="both", expand=True)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background=ROW_A, foreground=TEXT,
                        fieldbackground=ROW_A, rowheight=28,
                        font=FONT_LABEL, borderwidth=0)
        style.configure("Treeview.Heading",
                        background=PANEL, foreground=ACCENT2,
                        font=FONT_BOLD, relief="flat")
        style.map("Treeview", background=[("selected", ACCENT)])

        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        widths = [50, 200, 130, 90, 110, 140, 90]
        for c, w in zip(cols, widths):
            self.tree.heading(c, text=c, command=lambda col=c: self._sort(col))
            self.tree.column(c, width=w, anchor="center" if c not in ("Name","Category") else "w")

        self.tree.tag_configure("low", background="#3A1E1E", foreground=DANGER)
        self.tree.tag_configure("ok",  background=ROW_A)
        self.tree.tag_configure("alt", background=ROW_B)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_statusbar(self):
        sb = tk.Frame(self, bg=PANEL, height=28)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(sb, textvariable=self.status_var, font=FONT_SMALL,
                 bg=PANEL, fg=SUBTEXT, anchor="w").pack(side="left", padx=12)
        self.total_var = tk.StringVar()
        tk.Label(sb, textvariable=self.total_var, font=FONT_SMALL,
                 bg=PANEL, fg=ACCENT2, anchor="e").pack(side="right", padx=12)

    # ── SORTING ──────────────────────────────
    def _sort(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            data.sort(key=lambda x: float(x[0].replace("Rs.","").replace(",","")))
        except ValueError:
            data.sort()
        for i, (_, k) in enumerate(data):
            self.tree.move(k, "", i)

    # ── CRUD ─────────────────────────────────
    def _get_fields(self):
        name  = self.name_var.get().strip()
        cat   = self.cat_var.get().strip()
        qty   = self.qty_var.get().strip()
        price = self.price_var.get().strip()
        if not name or not cat or not qty or not price:
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return None
        try:
            qty   = int(qty)
            price = float(price)
        except ValueError:
            messagebox.showerror("Invalid Input", "Quantity must be a whole number and Price a number.")
            return None
        if qty < 0 or price < 0:
            messagebox.showerror("Invalid Input", "Quantity and Price cannot be negative.")
            return None
        return name, cat, qty, price

    def add_product(self):
        vals = self._get_fields()
        if not vals:
            return
        name, cat, qty, price = vals
        conn = get_conn()
        conn.execute("INSERT INTO products (name,category,quantity,price,added_on) VALUES (?,?,?,?,?)",
                     (name, cat, qty, price, datetime.now().strftime("%Y-%m-%d")))
        conn.commit(); conn.close()
        self.clear_form()
        self.load_products()
        self.status_var.set(f"✅  '{name}' added successfully.")

    def update_product(self):
        if not self.selected_id:
            messagebox.showinfo("No Selection", "Please select a product from the table first.")
            return
        vals = self._get_fields()
        if not vals:
            return
        name, cat, qty, price = vals
        conn = get_conn()
        conn.execute("UPDATE products SET name=?,category=?,quantity=?,price=? WHERE id=?",
                     (name, cat, qty, price, self.selected_id))
        conn.commit(); conn.close()
        self.clear_form()
        self.load_products()
        self.status_var.set("✏️  Product updated.")

    def delete_product(self):
        if not self.selected_id:
            messagebox.showinfo("No Selection", "Please select a product to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            return
        conn = get_conn()
        conn.execute("DELETE FROM products WHERE id=?", (self.selected_id,))
        conn.commit(); conn.close()
        self.clear_form()
        self.load_products()
        self.status_var.set("🗑  Product deleted.")

    def clear_form(self):
        for attr in ("name_var","cat_var","qty_var","price_var"):
            getattr(self, attr).set("")
        self.selected_id = None

    # ── LOAD / DISPLAY ───────────────────────
    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = self.search_var.get().strip().lower()
        conn  = get_conn()
        rows  = conn.execute(
            "SELECT id,name,category,quantity,price,added_on FROM products ORDER BY id DESC"
        ).fetchall()
        conn.close()

        total_val = 0.0
        low_count = 0
        shown = 0
        for i, (pid, name, cat, qty, price, date) in enumerate(rows):
            if query and query not in name.lower() and query not in cat.lower():
                continue
            status = "Low" if qty <= LOW_STOCK else "OK"
            tag = "low" if qty <= LOW_STOCK else ("ok" if i % 2 == 0 else "alt")
            self.tree.insert("", "end", iid=pid, tags=(tag,),
                             values=(pid, name, cat, qty,
                                     f"Rs.{price:,.2f}", date, status))
            total_val += qty * price
            if qty <= LOW_STOCK:
                low_count += 1
            shown += 1

        self.total_var.set(
            f"Total: {shown}   |   Value: Rs.{total_val:,.2f}"
            + (f"   |   Low Stock: {low_count}" if low_count else ""))

    def on_select(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        conn = get_conn()
        row = conn.execute("SELECT name,category,quantity,price FROM products WHERE id=?",
                           (pid,)).fetchone()
        conn.close()
        if row:
            self.selected_id = pid
            self.name_var.set(row[0])
            self.cat_var.set(row[1])
            self.qty_var.set(str(row[2]))
            self.price_var.set(str(row[3]))
            self.status_var.set(f"Selected: {row[0]}  (ID {pid})")

    # ── CSV IMPORT ────────────────────────────
    def import_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)

                # Check required columns
                required = {"name", "category", "quantity", "price"}
                if not required.issubset(set(k.strip().lower() for k in reader.fieldnames)):
                    messagebox.showerror(
                        "Invalid CSV",
                        "CSV must have these columns:\n  name, category, quantity, price"
                    )
                    return

                conn    = get_conn()
                added   = 0
                skipped = 0
                today   = datetime.now().strftime("%Y-%m-%d")

                for row in reader:
                    try:
                        name  = row["name"].strip()
                        cat   = row["category"].strip().title()
                        qty   = int(float(row["quantity"].strip()))
                        price = float(row["price"].strip())

                        if not name or qty < 0 or price < 0:
                            skipped += 1
                            continue

                        conn.execute(
                            "INSERT INTO products (name,category,quantity,price,added_on) VALUES (?,?,?,?,?)",
                            (name, cat, qty, price, today)
                        )
                        added += 1
                    except (ValueError, KeyError):
                        skipped += 1
                        continue

                conn.commit()
                conn.close()

            self.load_products()
            self.status_var.set(f"CSV Imported: {added} added, {skipped} skipped.")
            messagebox.showinfo(
                "Import Complete",
                f"Successfully imported {added} products!\n"
                f"Skipped {skipped} invalid rows."
            )

        except Exception as e:
            messagebox.showerror("Import Error", f"Could not read file:\n{e}")

    # ── CHARTS ───────────────────────────────
    def show_charts(self):
        subprocess.Popen([sys.executable, "inventory_visualizations.py"])

    # ── EXPORT ───────────────────────────────
    def export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not filepath:
            return
        conn = get_conn()
        rows = conn.execute(
            "SELECT id,name,category,quantity,price,added_on FROM products"
        ).fetchall()
        conn.close()
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Name","Category","Quantity","Price","Added On"])
            writer.writerows(rows)
        messagebox.showinfo("Export Successful", f"Data exported to:\n{filepath}")
        self.status_var.set(f"Exported to {filepath}")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()