import tkinter as tk
from tkinter import ttk, messagebox

class Node:
    def __init__(self, key, val):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = {}  # Map key to node

        # Left = LRU, Right = Most Recent
        self.left, self.right = Node(0, 0), Node(0, 0)
        self.left.next, self.right.prev = self.right, self.left

    def remove(self, node):
        """Remove node from the list."""
        prev, nxt = node.prev, node.next
        prev.next, nxt.prev = nxt, prev

    def insert(self, node):
        """Insert node at the right."""
        prev, nxt = self.right.prev, self.right
        prev.next = nxt.prev = node
        node.next, node.prev = nxt, prev

    def get(self, key: int) -> int:
        if key in self.cache:
            self.remove(self.cache[key])
            self.insert(self.cache[key])
            return self.cache[key].val
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.remove(self.cache[key])
        self.cache[key] = Node(key, value)
        self.insert(self.cache[key])

        if len(self.cache) > self.cap:
            # Remove from the list and delete the LRU from the hash map
            lru = self.left.next
            self.remove(lru)
            del self.cache[lru.key]

# Initialize LRU Cache with default capacity
cache = LRUCache(3)

# UI Functions
def handle_get():
    key = entry_key.get()
    if key.isdigit():
        result = cache.get(int(key))
        if result != -1:
            messagebox.showinfo("Get Result", f"Key: {key}, Value: {result}")
        else:
            messagebox.showerror("Get Error", f"Key {key} not found!")
    else:
        messagebox.showerror("Input Error", "Please enter a valid integer key.")

def handle_put():
    key = entry_key.get()
    value = entry_value.get()
    if key.isdigit() and value.isdigit():
        cache.put(int(key), int(value))
        messagebox.showinfo("Put Operation", f"Key: {key}, Value: {value} added!")
        update_cache_view()
    else:
        messagebox.showerror("Input Error", "Please enter valid integer key and value.")

def update_cache_view():
    """Update the current state of the cache."""
    cache_listbox.delete(0, tk.END)
    node = cache.left.next
    while node != cache.right:
        cache_listbox.insert(tk.END, f"Key: {node.key}, Value: {node.val}")
        node = node.next

# UI Setup
root = tk.Tk()
root.title("LRU Cache Manager")

# Key Entry
frame_key = ttk.LabelFrame(root, text="Key-Value Input")
frame_key.pack(padx=10, pady=5, fill="x")
ttk.Label(frame_key, text="Key: ").grid(row=0, column=0, padx=5, pady=5)
entry_key = ttk.Entry(frame_key)
entry_key.grid(row=0, column=1, padx=5, pady=5)
ttk.Label(frame_key, text="Value: ").grid(row=0, column=2, padx=5, pady=5)
entry_value = ttk.Entry(frame_key)
entry_value.grid(row=0, column=3, padx=5, pady=5)

# Buttons
frame_buttons = ttk.Frame(root)
frame_buttons.pack(padx=10, pady=5, fill="x")
btn_get = ttk.Button(frame_buttons, text="Get", command=handle_get)
btn_get.pack(side="left", padx=5)
btn_put = ttk.Button(frame_buttons, text="Put", command=handle_put)
btn_put.pack(side="left", padx=5)

# Cache View
frame_cache = ttk.LabelFrame(root, text="Cache State")
frame_cache.pack(padx=10, pady=5, fill="both", expand=True)
cache_listbox = tk.Listbox(frame_cache, height=10)
cache_listbox.pack(padx=5, pady=5, fill="both", expand=True)

# Initial Cache View Update
update_cache_view()

# Run the application
root.mainloop()
