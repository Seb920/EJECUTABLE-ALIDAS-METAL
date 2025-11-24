import tkinter as tk
from tkinter import ttk, messagebox

class CustomWidgets:
    @staticmethod
    def create_entry(frame, label_text, row, column, width=20):
        label = tk.Label(frame, text=label_text)
        label.grid(row=row, column=column, padx=5, pady=5, sticky="w")
        entry = tk.Entry(frame, width=width)
        entry.grid(row=row, column=column+1, padx=5, pady=5)
        return entry
    
    @staticmethod
    def create_combobox(frame, label_text, row, column, values, width=18):
        label = tk.Label(frame, text=label_text)
        label.grid(row=row, column=column, padx=5, pady=5, sticky="w")
        combobox = ttk.Combobox(frame, values=values, width=width)
        combobox.grid(row=row, column=column+1, padx=5, pady=5)
        return combobox
    
    @staticmethod
    def create_button(frame, text, command, row, column, columnspan=1):
        button = tk.Button(frame, text=text, command=command, 
                          bg="#2E86AB", fg="white", font=("Arial", 10))
        button.grid(row=row, column=column, columnspan=columnspan, 
                   padx=5, pady=5, sticky="ew")
        return button

class TableWidget:
    def __init__(self, parent, columns, grid_options=None):
        self.parent = parent
        self.columns = columns
        
        # Frame para la tabla y scrollbar
        self.frame = tk.Frame(parent)
        
        # Usar grid si se especifican opciones, sino usar pack
        if grid_options:
            self.frame.grid(**grid_options)
        else:
            self.frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=15)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        
        # Empaquetar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def update_data(self, data):
        # Limpiar tabla existente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar nuevos datos
        for row in data:
            self.tree.insert("", "end", values=row)