import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import numpy as np
import time
import random

# Sorting algorithms with visualization

# Bubble Sort Algorithm:
# Repeatedly swaps adjacent elements if they are in the wrong order.
# This continues until the entire list is sorted.
def bubble_sort(arr, bars, texts, colors):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            original_colors = colors[:]
            highlight_bars(bars, texts, [j, j + 1], colors)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                colors[j], colors[j + 1] = colors[j + 1], colors[j]  # Maintain original colors after swap
                update_bars(bars, texts, arr, colors)
            restore_colors(bars, texts, original_colors)

# Selection Sort Algorithm:
# Finds the smallest element in the list and swaps it with the first element.
# Repeats the process for the remaining unsorted portion.
def selection_sort(arr, bars, texts, colors):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            original_colors = colors[:]
            highlight_bars(bars, texts, [min_idx, j], colors)
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
        colors[i], colors[min_idx] = colors[min_idx], colors[i]  # Maintain original colors after swap
        update_bars(bars, texts, arr, colors)
        restore_colors(bars, texts, original_colors)

# Insertion Sort Algorithm:
# Takes one element at a time and inserts it into its correct position.
# Works well for small or nearly sorted lists.
def insertion_sort(arr, bars, texts, colors):
    for i in range(1, len(arr)):
        key = arr[i]
        key_color = colors[i]
        j = i - 1
        original_colors = colors[:]  # Ensure original_colors is always defined
        while j >= 0 and arr[j] > key:
            highlight_bars(bars, texts, [j, j + 1], colors)
            arr[j + 1] = arr[j]
            colors[j + 1] = colors[j]  # Maintain original colors after shift
            j -= 1
        arr[j + 1] = key
        colors[j + 1] = key_color
        update_bars(bars, texts, arr, colors)
        restore_colors(bars, texts, original_colors)

# Visualization functions
def highlight_bars(bars, texts, indices, colors):
    temp_colors = colors[:]
    for idx in indices:
        temp_colors[idx] = 'black'  # Selector is black only
    update_bars(bars, texts, heights, temp_colors)
    time.sleep(0.5)

def restore_colors(bars, texts, colors):
    update_bars(bars, texts, heights, colors)
    time.sleep(0.5)

def update_bars(bars, texts, heights, colors):
    for bar, text, height, color in zip(bars, texts, heights, colors):
        bar.set_height(height)
        bar.set_color(color)
        text.set_position((bar.get_x() + bar.get_width() / 2, height + 1))
        text.set_text(str(height))
    plt.pause(0.5)

def start_sorting():
    input_text = entry_numbers.get().strip()
    if not input_text:
        messagebox.showerror("Input Error", "Please enter numbers separated by commas.")
        return
    
    try:
        numbers = list(map(int, input_text.split(',')))
    except ValueError:
        messagebox.showerror("Input Error", "Invalid input. Only numbers separated by commas are allowed.")
        return

    algorithm = combo_alg.get()
    if not algorithm:
        messagebox.showerror("Selection Error", "Please select a sorting algorithm.")
        return

    fig, ax = plt.subplots()
    x_pos = np.arange(len(numbers))
    global heights
    heights = numbers.copy()
    colors = list(plt.cm.tab10.colors[:len(heights)])  # Assign different colors for input bars
    bars = ax.bar(x_pos, heights, color=colors)
    texts = [ax.text(i, v + 1, str(v), ha='center', fontsize=10) for i, v in enumerate(heights)]
    
    plt.xticks(range(0, len(numbers) + 1, 1))
    plt.yticks(range(0, max(numbers) + 10, 10))
    plt.xlabel("Input Numbers")
    plt.ylabel("Values")
    plt.title(f"{algorithm} Sort Visualization")
    plt.ion()
    plt.show()

    if algorithm == "Bubble Sort":
        bubble_sort(heights, bars, texts, colors)
    elif algorithm == "Selection Sort":
        selection_sort(heights, bars, texts, colors)
    elif algorithm == "Insertion Sort":
        insertion_sort(heights, bars, texts, colors)

    for bar, text in zip(bars, texts):
        bar.set_color('green')
        text.set_color('green')
    plt.ioff()
    plt.show()

# GUI Setup
root = tk.Tk()
root.title("Sorting Algorithm Visualizer")
root.geometry("400x300")

tk.Label(root, text="Enter numbers (comma-separated):").pack(pady=5)
entry_numbers = tk.Entry(root, width=30)
entry_numbers.pack(pady=5)

tk.Label(root, text="Select Sorting Algorithm:").pack(pady=5)
combo_alg = ttk.Combobox(root, values=["Bubble Sort", "Selection Sort", "Insertion Sort"], state="readonly")
combo_alg.pack(pady=5)

tk.Button(root, text="Start Sorting", command=start_sorting).pack(pady=20)

root.mainloop()
