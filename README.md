# inventory_prjec  
Inventory Management System with Live Analytics Dashboard
A feature-rich Inventory Management application built using Python, Tkinter, and SQLite3. This system features a custom dark-themed user interface for managing stock records alongside a dynamic 6-in-1 Matplotlib data visualization dashboard for real-time business insights.

Features
Complete CRUD Operations: Easily Add, Update, View, and Delete product records through an intuitive interface.

Smart CSV Integration: Import bulk product data from any standard CSV file or export your current database instantly for backups.

Automated Low Stock Alerts: Visual color-coded warning indicators automatically highlight any products falling below the safety threshold of 5 units or less.

Advanced 6-in-1 Dynamic Dashboard: Generates real-time business analytics including:

Stock Quantity Bar Chart: Displays current stock levels with an explicit low-stock reference line.

Category Distribution Pie Chart: Breaks down inventory share percentage by product categories.

Inventory Value Horizontal Bar Chart: Uses custom financial scaling with notation in Crores (Cr) and Lakhs (L) to cleanly display total valuations without text overlaps.

Total Value Trend Line: Tracks cumulative capital distribution across categories.

Category Heatmap: Compares average quantities against average prices.

Price vs Quantity Scatter Plot: Highlights statistical correlation coefficients (r-value) between asset costs and volume.

Tech Stack
Frontend UI: Python Tkinter with a Custom Dark-Theme Style

Backend Database: SQLite3

Data Science and Analytics: Matplotlib, Seaborn, NumPy

Setup and Installation
1. Prerequisites
Ensure you have Python installed on your system. Next, open your terminal or command prompt and install the required library dependencies:

Bash
pip install matplotlib seaborn numpy
2. How to Run the Project
Clone or download the files into a single directory and launch the main application interface:

Bash
python inventory_management.py
To view the dynamic analytics panel, simply click on the Show Charts button located on the main application interface.

CSV Format Specification for Import
When preparing a custom bulk data upload via the Import CSV feature, ensure your file structure adheres to the following column order without an ID requirement:
Product Name, Category, Quantity, Price

Author
GitHub Profile: https://github.com/Abdullah-W-tech
