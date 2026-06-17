"""
Inventory Management System - Visualizations
Reads LIVE data from inventory.db (same folder)
Uses: numpy, matplotlib, seaborn, sqlite3
Run: python inventory_visualizations.py
"""

import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

# ─────────────────────────────────────────────
#  LOAD DATA FROM DATABASE
# ─────────────────────────────────────────────
def load_data():
    try:
        conn = sqlite3.connect("inventory.db")
        rows = conn.execute(
            "SELECT name, category, quantity, price FROM products"
        ).fetchall()
        conn.close()
    except Exception as e:
        print(f"Could not connect to inventory.db: {e}")
        return [], [], [], []

    if not rows:
        print("No products found. Please add products first.")
        return [], [], [], []

    products, categories, quantities, prices = [], [], [], []
    for r in rows:
        products.append(r[0])
        clean_cat = r[1].strip().title()
        if clean_cat in ["Stationary"]:
            clean_cat = "Stationery"
        categories.append(clean_cat)
        quantities.append(r[2])
        prices.append(float(r[3]))

    return products, categories, np.array(quantities), np.array(prices)

# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────
sns.set_theme(style="darkgrid")
plt.rcParams.update({
    "figure.facecolor" : "#1C1C2E",
    "axes.facecolor"   : "#22223A",
    "axes.labelcolor"  : "#EAEAF4",
    "xtick.color"      : "#9090B0",
    "ytick.color"      : "#9090B0",
    "text.color"       : "#EAEAF4",
    "grid.color"       : "#35355A",
    "axes.titlecolor"  : "#A17CF5",
    "axes.titlesize"   : 11,
    "axes.titleweight" : "bold",
})

PURPLE = "#7C5CBF"
GREEN  = "#4CAF82"
RED    = "#E05C5C"
BLUE   = "#5C8FBF"
ORANGE = "#F0A060"
LOW    = 5

def fmt_currency(x, _=None):
    if x >= 1e7:   return f"Rs.{x/1e7:.1f}Cr"
    if x >= 1e5:   return f"Rs.{x/1e5:.1f}L"
    if x >= 1000:  return f"Rs.{x/1000:.0f}K"
    return f"Rs.{int(x)}"

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    products, categories, quantities, prices = load_data()
    if not products:
        return

    values   = quantities * prices
    cat_list = sorted(set(categories))
    n        = len(products)
    short    = [p[:11]+"..." if len(p)>11 else p for p in products]
    COLORS   = [PURPLE, BLUE, GREEN, ORANGE, RED, "#E0A0F5", "#60D0BF"]

    fig = plt.figure(figsize=(19, 11))
    fig.patch.set_facecolor("#1C1C2E")
    fig.suptitle("Inventory Management System - Live Dashboard",
                 fontsize=15, fontweight="bold", color="#A17CF5", y=0.98)

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.52, wspace=0.42)

    # ── 1. BAR — Quantity per product ─────────
    ax1 = fig.add_subplot(gs[0, 0])
    bar_colors = [RED if q <= LOW else PURPLE for q in quantities]
    bars = ax1.bar(range(n), quantities, color=bar_colors,
                   edgecolor="#1C1C2E", linewidth=0.8)
    ax1.set_xticks(range(n))
    ax1.set_xticklabels(short, rotation=35, ha="right", fontsize=7.5)
    ax1.axhline(LOW, color=RED, linestyle="--", linewidth=1.2,
                label=f"Low Stock (<=5)")
    ax1.set_title("Stock Quantity per Product")
    ax1.set_ylabel("Quantity")
    ax1.legend(fontsize=8, facecolor="#2A2A40", edgecolor="#35355A")
    for bar, qty in zip(bars, quantities):
        ax1.text(bar.get_x()+bar.get_width()/2,
                 bar.get_height()+max(quantities)*0.01,
                 str(qty), ha="center", fontsize=7.5, color="#EAEAF4")

    # ── 2. PIE — Category distribution ────────
    ax2 = fig.add_subplot(gs[0, 1])
    cat_counts  = [categories.count(c) for c in cat_list]
    pie_palette = [COLORS[i % len(COLORS)] for i in range(len(cat_list))]
    ax2.pie(cat_counts, labels=cat_list, autopct="%1.1f%%",
            colors=pie_palette, startangle=140,
            textprops={"color": "#EAEAF4", "fontsize": 9},
            wedgeprops={"edgecolor": "#1C1C2E", "linewidth": 2})
    ax2.set_title("Products by Category")

    # ── 3. HORIZONTAL BAR — Value (LOG SCALE FIX) ───
    ax3 = fig.add_subplot(gs[0, 2])
    sidx     = np.argsort(values)
    h_colors = [COLORS[i % len(COLORS)] for i in range(n)]
    h_bars   = ax3.barh([short[i] for i in sidx],
                        [values[i] for i in sidx],
                        color=[h_colors[i] for i in range(n)],
                        edgecolor="#1C1C2E", height=0.65)
    ax3.set_xscale("log")
    ax3.set_title("Inventory Value per Product (Log Scale)")
    ax3.set_xlabel("Value (log scale)")
    ax3.xaxis.set_major_formatter(plt.FuncFormatter(fmt_currency))
    ax3.tick_params(axis='y', labelsize=8)
    ax3.tick_params(axis='x', labelsize=7.5, rotation=20)
    for bar, idx in zip(h_bars, sidx):
        ax3.text(bar.get_width() * 1.08,
                 bar.get_y() + bar.get_height()/2,
                 fmt_currency(values[idx]),
                 va="center", fontsize=7.5, color="#EAEAF4")

    # ── 4. LINE — Total value by category ─────
    ax4 = fig.add_subplot(gs[1, 0])
    cat_vals = [np.sum(values[np.array(categories)==c]) for c in cat_list]
    ax4.plot(cat_list, cat_vals, color=PURPLE, linewidth=2.5,
             marker="o", markersize=8, markerfacecolor=ORANGE)
    ax4.fill_between(cat_list, cat_vals, alpha=0.15, color=PURPLE)
    ax4.set_title("Total Value by Category")
    ax4.set_ylabel("Value (Rs.)")
    ax4.yaxis.set_major_formatter(plt.FuncFormatter(fmt_currency))
    ax4.tick_params(axis='x', labelsize=8.5)
    for cat, val in zip(cat_list, cat_vals):
        ax4.annotate(fmt_currency(val), (cat, val),
                     textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=7.5, color="#EAEAF4")

    # ── 5. HEATMAP — Avg qty vs avg price ─────
    ax5 = fig.add_subplot(gs[1, 1])
    unique_cats = list(dict.fromkeys(cat_list))   # deduplicate
    matrix = []
    for cat in unique_cats:
        mask = np.array(categories) == cat
        matrix.append([
            float(np.mean(quantities[mask])),
            float(np.mean(prices[mask]) / 1000)
        ])
    matrix = np.array(matrix)
    sns.heatmap(matrix, annot=True, fmt=".1f", cmap="mako",
                xticklabels=["Avg Qty", "Avg Price\n(Rs.000s)"],
                yticklabels=unique_cats,
                linewidths=0.5, linecolor="#1C1C2E",
                ax=ax5, cbar_kws={"shrink": 0.75})
    ax5.set_title("Category Heatmap")
    ax5.tick_params(axis='x', labelsize=8.5)
    ax5.tick_params(axis='y', labelsize=8.5, rotation=0)

    # ── 6. SCATTER — Price vs Quantity ────────
    ax6 = fig.add_subplot(gs[1, 2])
    for i, cat in enumerate(unique_cats):
        mask = np.array(categories) == cat
        ax6.scatter(prices[mask], quantities[mask],
                    color=COLORS[i % len(COLORS)],
                    s=110, alpha=0.9, edgecolors="#1C1C2E",
                    linewidth=0.8, label=cat, zorder=3)
    if n > 1 and np.std(prices) > 0 and np.std(quantities) > 0:
        corr = np.corrcoef(np.log1p(prices), quantities)[0, 1]
        title = f"Price vs Quantity  (r = {corr:.2f})" if not np.isnan(corr) else "Price vs Quantity"
    else:
        title = "Price vs Quantity"
    ax6.set_title(title)
    ax6.set_xlabel("Price (Rs.)")
    ax6.set_ylabel("Quantity")
    ax6.xaxis.set_major_formatter(plt.FuncFormatter(fmt_currency))
    ax6.legend(fontsize=8, facecolor="#2A2A40", edgecolor="#35355A")
    for name, px, qty in zip(short, prices, quantities):
        ax6.annotate(name, (px, qty), textcoords="offset points",
                     xytext=(5, 3), fontsize=6.5, color="#9090B0")

    plt.savefig("inventory_dashboard.png", dpi=150,
                bbox_inches="tight", facecolor="#1C1C2E")
    print(f"Dashboard saved -- {n} products loaded from inventory.db")
    plt.show()


if __name__ == "__main__":
    main()