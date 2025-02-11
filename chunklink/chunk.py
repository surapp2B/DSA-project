import hashlib
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import tempfile

class ChunkNode:
    def __init__(self, index, data):
        self.index = index
        self.data = data
        self.next_checksum = None
        self.next_node = None
        
    def compute_checksum(self, data):
        return hashlib.sha256(data).hexdigest()

class ChunkLink:
    def __init__(self):
        self.head = None
        self.chunk_size = 1024  # Default 1KB chunks
        
    def split_file(self, file_path, chunk_size=1024):
        self.chunk_size = chunk_size
        self.head = None
        nodes = []
        
        with open(file_path, 'rb') as f:
            index = 0
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                node = ChunkNode(index, chunk)
                nodes.append(node)
                index += 1
                
        # Link nodes and set checksums
        for i in range(len(nodes)-1):
            nodes[i].next_node = nodes[i+1]
            nodes[i].next_checksum = nodes[i].compute_checksum(nodes[i+1].data)
            
        self.head = nodes[0] if nodes else None
        return nodes
    
    def validate_chain(self):
        current = self.head
        while current and current.next_node:
            actual_checksum = current.compute_checksum(current.next_node.data)
            if actual_checksum != current.next_checksum:
                return False
            current = current.next_node
        return True
    
    def reconstruct_file(self, output_path):
        if not self.head:
            raise ValueError("No chunks to reconstruct")
            
        current = self.head
        full_data = bytearray()
        
        while current:
            full_data.extend(current.data)
            current = current.next_node
            
        with open(output_path, 'wb') as f:
            f.write(full_data)
        return output_path

class ChunkLinkGUI:
    def __init__(self, master):
        self.master = master
        master.title("Chunk-Link File Manager")
        
        self.chunklink = ChunkLink()
        self.current_file = None
        
        # GUI Layout
        self.frame = tk.Frame(master, padx=10, pady=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # File Selection
        self.file_button = tk.Button(self.frame, text="Select File", command=self.load_file)
        self.file_button.grid(row=0, column=0, pady=5)
        
        # Chunk Controls
        self.reconstruct_button = tk.Button(self.frame, text="Reconstruct File", command=self.reconstruct)
        self.reconstruct_button.grid(row=0, column=1, padx=5)
        
        self.validate_button = tk.Button(self.frame, text="Validate Chain", command=self.validate)
        self.validate_button.grid(row=0, column=2, padx=5)
        
        # Add chunk size controls
        self.chunk_size_label = tk.Label(self.frame, text="Chunk Size (bytes):")
        self.chunk_size_label.grid(row=0, column=3, padx=5)
        
        self.chunk_size_entry = tk.Entry(self.frame, width=8)
        self.chunk_size_entry.insert(0, "1024")  # Default value
        self.chunk_size_entry.grid(row=0, column=4, padx=5)
        
        # Add temporary corruption button
        self.corrupt_button = tk.Button(self.frame, text="Simulate Corruption", command=self.simulate_corruption)
        self.corrupt_button.grid(row=0, column=5, padx=5)
        
        # Info Display
        self.info_display = scrolledtext.ScrolledText(self.frame, width=80, height=20)
        self.info_display.grid(row=1, column=0, columnspan=3, pady=10)
        
    def load_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                chunk_size = int(self.chunk_size_entry.get())
                if chunk_size < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid chunk size! Using default 1024 bytes")
                chunk_size = 1024
                
            self.current_file = file_path
            nodes = self.chunklink.split_file(file_path, chunk_size)
            self.update_display()
            messagebox.showinfo("Success", f"File split into {len(nodes)} chunks!")
            
    def reconstruct(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file loaded!")
            return
            
        output_path = filedialog.asksaveasfilename()
        if output_path:
            try:
                self.chunklink.reconstruct_file(output_path)
                messagebox.showinfo("Success", f"File reconstructed to {output_path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def validate(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file loaded!")
            return
            
        self.full_validation()
        
    def update_display(self):
        self.info_display.delete(1.0, tk.END)
        current = self.chunklink.head
        while current:
            self.info_display.insert(tk.END, 
                f"Chunk {current.index}\n"
                f"Data: {current.data[:20].hex()}...\n"
                f"Next Checksum: {current.next_checksum[:10] if current.next_checksum else 'END'}\n"
                f"{'-'*60}\n"
            )
            current = current.next_node

    def simulate_corruption(self):
        if self.chunklink.head and self.chunklink.head.next_node:
            self.chunklink.head.next_node.data = b"CORRUPTED_DATA"
            self.update_display()

    def full_validation(self):
        """Combines chain validation and file comparison"""
        if not self.current_file:
            messagebox.showerror("Error", "No file loaded!")
            return
        
        # 1. Chain Validation
        chain_valid = self.chunklink.validate_chain()
        
        # 2. File Comparison
        try:
            # Create temporary reconstructed file
            temp_path = tempfile.mktemp()  # Cross-platform
            
            # Add debug output
            print("Corrupted Data During Validation:", self.chunklink.head.next_node.data)
            
            self.chunklink.reconstruct_file(temp_path)
            
            # Compare hashes
            original_hash = self.file_hash(self.current_file)
            reconstructed_hash = self.file_hash(temp_path)
            file_valid = original_hash == reconstructed_hash
            
            # Cleanup
            os.remove(temp_path)
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {str(e)}")
            return
        
        # Combine results
        result = []
        result.append(f"Chain Integrity: {'Valid' if chain_valid else 'Invalid'}")
        result.append(f"File Integrity: {'Matched' if file_valid else 'Mismatched'}")
        result.append(f"Original Hash: {original_hash}")
        result.append(f"Reconstructed Hash: {reconstructed_hash}")
        
        messagebox.showinfo("Full Validation", "\n".join(result))
    
    def file_hash(self, file_path):
        """Calculate SHA-256 hash of a file"""
        sha = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)  # 64KB chunks
                if not data:
                    break
                sha.update(data)
        return sha.hexdigest()

if __name__ == "__main__":
    root = tk.Tk()
    gui = ChunkLinkGUI(root)
    root.mainloop() 