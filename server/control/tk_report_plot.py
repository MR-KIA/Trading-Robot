import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys
from plotting import plot_prediction_vs_truth


def center_window(root, width=300, height=200):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


def select_file():
    initial_dir = os.path.join(
        os.getcwd(), "G:\\AI_trading_bot\\server\\reports\\predictions")
    if not os.path.exists(initial_dir):
        os.makedirs(initial_dir)

    file_path = filedialog.askopenfilename(
        initialdir=initial_dir, filetypes=[("CSV files", "*.csv")])
    if file_path:
        folder_name = simpledialog.askstring(
            "Input", "Enter folder name to save the plot:")
        if folder_name:
            save_path = filedialog.askdirectory(
                initialdir=os.getcwd(), title="Select Folder to Save Plot")
            if save_path:
                full_save_path = os.path.join(save_path, folder_name)
                if os.path.exists(full_save_path):
                    messagebox.showerror("Error", f"Folder '{
                                         folder_name}' already exists. Please choose a different name.")
                else:
                    os.makedirs(full_save_path)
                    try:
                        plot_prediction_vs_truth(file_path)
                        plt.savefig(os.path.join(full_save_path, "plot.png"))
                        messagebox.showinfo(
                            "Success", f"Plot saved in folder '{full_save_path}'")
                    except Exception as e:
                        messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CSV Plotter")

    center_window(root, width=400, height=300)

    btn_open_file = tk.Button(
        root, text="Select CSV File", command=select_file)
    btn_open_file.pack(pady=20)

    root.mainloop()
