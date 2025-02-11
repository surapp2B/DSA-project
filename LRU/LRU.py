import tkinter as tk
from tkinter import ttk, messagebox

class Node:
    def __init__(self, key, val):
        self.key, self.val = key, val  # Initialize key and value for the node
        self.prev = self.next = None  # Initialize pointers for doubly linked list

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity  # Store the capacity of the cache
        self.cache = {}    # Dictionary to store key-node pairs for O(1) access

        # Dummy head and tail nodes to simplify linked list operations
        self.left, self.right = Node(0, 0), Node(0, 0)
        self.left.next, self.right.prev = self.right, self.left  # Connect head and tail

    def remove(self, node):
        """Remove node from the doubly linked list."""
        prev, nxt = node.prev, node.next  # Get previous and next nodes
        prev.next, nxt.prev = nxt, prev  # Update pointers to remove the node

    def insert(self, node):
        """Insert node at the right (most recently used) end of the list."""
        prev, nxt = self.right.prev, self.right  # Get the node before tail and tail
        prev.next = nxt.prev = node  # Insert the new node between them
        node.next, node.prev = nxt, prev  # Update new node's pointers

    def get(self, key: int) -> int:
        if key in self.cache:  # Check if key exists in the cache
            self.remove(self.cache[key])  # Move the accessed node to the right (MRU)
            self.insert(self.cache[key])
            return self.cache[key].val  # Return the value
        return -1  # Return -1 if key not found

    def put(self, key: int, value: int) -> None:
        if key in self.cache:  # If key already exists
            self.remove(self.cache[key])  # Remove the old node
        self.cache[key] = Node(key, value)  # Create/update the node with new value
        self.insert(self.cache[key])  # Insert the node at the right (MRU)

        if len(self.cache) > self.cap:  # If cache is full
            lru = self.left.next  # Get the LRU node (left.next)
            self.remove(lru)  # Remove LRU node from the list
            del self.cache[lru.key]  # Remove LRU entry from the cache dictionary

# Initialize LRU Cache with default capacity 3
cache = LRUCache(3)

# --- UI Functions ---
def handle_get():
    key = entry_key.get()  # Get the key from the entry field
    if key.isdigit():  # Check if the key is a digit
        result = cache.get(int(key))  # Call the get method of the cache
        if result != -1:
            messagebox.showinfo("Get Result", f"Key: {key}, Value: {result}")  # Show the result in a message box
        else:
            messagebox.showerror("Get Error", f"Key {key} not found!")  # Show error if key is not found
    else:
        messagebox.showerror("Input Error", "Please enter a valid integer key.")  # Show error for invalid input

def handle_put():
    key = entry_key.get()  # Get the key from the entry field
    value = entry_value.get()  # Get the value from the entry field
    if key.isdigit() and value.isdigit():  # Check if both key and value are digits
        cache.put(int(key), int(value))  # Call the put method of the cache
        messagebox.showinfo("Put Operation", f"Key: {key}, Value: {value} added!")  # Show success message
        update_cache_view()  # Update the cache view in the UI
    else:
        messagebox.showerror("Input Error", "Please enter valid integer key and value.")  # Show error for invalid input

def update_cache_view():
    """Update the listbox displaying the current state of the cache."""
    cache_listbox.delete(0, tk.END)  # Clear the current listbox content
    node = cache.left.next  # Start from the first actual node (after the dummy head)
    while node != cache.right:  # Iterate until the dummy tail is reached
        cache_listbox.insert(tk.END, f"Key: {node.key}, Value: {node.val}")  # Insert key-value pair into listbox
        node = node.next  # Move to the next node

# --- UI Setup ---
root = tk.Tk()
root.title("LRU Cache Manager")  # Set the title of the window

# Key Entry Frame
frame_key = ttk.LabelFrame(root, text="Key-Value Input")  # Create a labeled frame for input
frame_key.pack(padx=10, pady=5, fill="x")  # Pack the frame with padding and fill horizontally
ttk.Label(frame_key, text="Key: ").grid(row=0, column=0, padx=5, pady=5)  # Label for key input
entry_key = ttk.Entry(frame_key)  # Entry field for key
entry_key.grid(row=0, column=1, padx=5, pady=5)  # Place the entry field
ttk.Label(frame_key, text="Value: ").grid(row=0, column=2, padx=5, pady=5)  # Label for value input
entry_value = ttk.Entry(frame_key)  # Entry field for value
entry_value.grid(row=0, column=3, padx=5, pady=5)  # Place the entry field

# Buttons Frame
frame_buttons = ttk.Frame(root)  # Frame to hold the buttons
frame_buttons.pack(padx=10, pady=5, fill="x")  # Pack the frame
btn_get = ttk.Button(frame_buttons, text="Get", command=handle_get)  # Create Get button
btn_get.pack(side="left", padx=5)  # Place the button
btn_put = ttk.Button(frame_buttons, text="Put", command=handle_put)  # Create Put button
btn_put.pack(side="left", padx=5)  # Place the button

# Cache View Frame
frame_cache = ttk.LabelFrame(root, text="Cache State")  # Labeled frame to show the cache state
frame_cache.pack(padx=10, pady=5, fill="both", expand=True)  # Pack and allow it to expand
cache_listbox = tk.Listbox(frame_cache, height=10)  # Listbox to display cache contents
cache_listbox.pack(padx=5, pady=5, fill="both", expand=True)  # Pack and allow listbox to expand

# Initial Cache View Update
update_cache_view()  # Populate the listbox initially

# Run the Tkinter main loop
root.mainloop()