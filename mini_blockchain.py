import hashlib
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, messagebox

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()
    
    def compute_hash(self):
        block_contents = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_contents.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def create_genesis_block(self):
        # Manually create first block with arbitrary values
        return Block(0, datetime.now(), "Genesis Block", "0")
    
    def get_latest_block(self):
        return self.chain[-1]
    
    def add_block(self, new_data):
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=datetime.now(),
            data=new_data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
    
    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block.compute_hash():
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

class BlockchainGUI:
    def __init__(self, master):
        self.master = master
        master.title("Mini Blockchain Explorer")
        
        self.blockchain = Blockchain()
        
        # Create GUI elements
        self.frame = tk.Frame(master, padx=10, pady=10)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.input_label = tk.Label(self.frame, text="New Block Data:")
        self.input_label.grid(row=0, column=0, sticky=tk.W)
        
        self.data_entry = tk.Entry(self.frame, width=40)
        self.data_entry.grid(row=0, column=1, padx=5)
        
        self.add_button = tk.Button(self.frame, text="Add Block", command=self.add_block)
        self.add_button.grid(row=0, column=2, padx=5)
        
        self.validate_button = tk.Button(self.frame, text="Validate Chain", command=self.validate_chain)
        self.validate_button.grid(row=1, column=0, pady=5)
        
        self.tamper_button = tk.Button(self.frame, text="Tamper with Block 1", command=self.tamper_block)
        self.tamper_button.grid(row=1, column=1, pady=5)
        
        self.chain_display = scrolledtext.ScrolledText(self.frame, width=60, height=15)
        self.chain_display.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.update_display()
    
    def add_block(self):
        data = self.data_entry.get()
        if data:
            self.blockchain.add_block(data)
            self.data_entry.delete(0, tk.END)
            self.update_display()
            messagebox.showinfo("Success", "Block added successfully!")
        else:
            messagebox.showwarning("Input Error", "Please enter block data")
    
    def validate_chain(self):
        is_valid = self.blockchain.validate_chain()
        status = "valid" if is_valid else "invalid"
        messagebox.showinfo("Validation Result", f"Blockchain is {status}")
    
    def tamper_block(self):
        if len(self.blockchain.chain) > 1:
            # Get reference to the block we're tampering with
            tampered_block = self.blockchain.chain[1]
            
            # Modify multiple properties
            tampered_block.data = "Tampered data!"
            tampered_block.timestamp = datetime.now()  # Update timestamp
            
            # Force recomputation of Block 1's hash but don't update Block 2's previous_hash
            # This will break the chain since Block 2's previous_hash won't match Block 1's new hash
            tampered_block.hash = tampered_block.compute_hash()
            
            self.update_display()
            messagebox.showwarning("Tamper Alert", "Block 1 has been tampered with!\n")
    
    def update_display(self):
        self.chain_display.delete(1.0, tk.END)
        for block in self.blockchain.chain:
            self.chain_display.insert(tk.END, 
                f"Block {block.index}\n"
                f"Timestamp: {block.timestamp}\n"
                f"Data: {block.data}\n"
                f"Previous Hash: {block.previous_hash[:10]}...\n"
                f"Hash: {block.hash[:10]}...\n"
                f"{'-'*40}\n"
            )

if __name__ == "__main__":
    root = tk.Tk()
    gui = BlockchainGUI(root)
    root.mainloop() 
