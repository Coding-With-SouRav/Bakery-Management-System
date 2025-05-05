import configparser
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# Data storage files
INGREDIENTS_FILE = "ingredients.json"
PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"
STAFF_FILE = "staff.json"
WINDOW_STATE_FILE = "window_state.json"



def resource_path(relative_path):
    """ Get absolute path to resources for both dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    # Handle nested icon paths
    if 'icons' in relative_path:
        full_path = os.path.join(base_path, relative_path.replace('\\', os.sep))
    else:
        full_path = os.path.join(base_path, relative_path)
        
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path

class Ingredient:
    def __init__(self, name, quantity, unit, reorder_level):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.reorder_level = reorder_level

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "reorder_level": self.reorder_level
        }

class Product:
    def __init__(self, name, price, recipe, quantity=0):
        self.name = name
        self.price = price
        self.recipe = recipe 
        self.quantity = quantity

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "recipe": self.recipe,
            "quantity": self.quantity 
        }

class Order:
    def __init__(self, customer_name, items, order_id=None, total=0, status="Pending", timestamp=None):
        self.order_id = order_id if order_id else datetime.now().strftime("%Y%m%d%H%M%S")
        self.customer_name = customer_name
        self.items = items
        self.total = total
        self.status = status
        self.timestamp = datetime.fromisoformat(timestamp) if timestamp else datetime.now()

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "items": self.items,
            "total": self.total,
            "status": self.status,
            "timestamp": self.timestamp.isoformat()
        }

class Staff:
    def __init__(self, name, role, shifts):
        self.name = name
        self.role = role
        self.shifts = shifts

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "shifts": self.shifts
        }

class BakeryManager:
    def __init__(self):
        self.ingredients = self.load_data(INGREDIENTS_FILE, Ingredient)
        self.products = self.load_data(PRODUCTS_FILE, Product)
        self.orders = self.load_data(ORDERS_FILE, Order)
        self.staff = self.load_data(STAFF_FILE, Staff)

    @staticmethod
    def load_data(file, cls):
        try:
            with open(file, "r") as f:
                data = json.load(f)
                return [cls(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_data(self):
        with open(INGREDIENTS_FILE, "w") as f:
            json.dump([i.to_dict() for i in self.ingredients], f, indent=4)
        with open(PRODUCTS_FILE, "w") as f:
            json.dump([p.to_dict() for p in self.products], f, indent=4)
        with open(ORDERS_FILE, "w") as f:
            json.dump([o.to_dict() for o in self.orders], f, indent=4)
        with open(STAFF_FILE, "w") as f:
            json.dump([s.to_dict() for s in self.staff], f, indent=4)

    def add_ingredient(self, name, quantity, unit, reorder_level):
        self.ingredients.append(Ingredient(name, quantity, unit, reorder_level))
        self.save_data()

    def restock_ingredient(self, name, quantity):
        for ingredient in self.ingredients:
            if ingredient.name == name:
                ingredient.quantity += quantity
                self.save_data()
                return True
        return False

    def check_low_stock(self):
        return [ing for ing in self.ingredients if ing.quantity < ing.reorder_level]

    def add_product(self, name, price, recipe, quantity):
        self.products.append(Product(name, price, recipe, quantity))
        self.save_data() 

    def create_order(self, customer_name, items):
        for product_name, qty in items.items():
            product = next((p for p in self.products if p.name == product_name), None)
            if not product or product.quantity < qty:
                return False

        # Deduct product quantities
        for product_name, qty in items.items():
            product = next(p for p in self.products if p.name == product_name)
            product.quantity -= qty

        # Create order
        order = Order(customer_name, items)
        order.total = sum(self.get_product_price(name) * qty for name, qty in items.items())
        self.orders.append(order)
        self.save_data()  
        return True

    def get_product_price(self, product_name):
        product = next((p for p in self.products if p.name == product_name), None)
        return product.price if product else 0

    def add_staff(self, name, role, shifts):
        self.staff.append(Staff(name, role, shifts))
        self.save_data()  

    def generate_sales_report(self):
        total_sales = sum(order.total for order in self.orders if order.status == "Completed")
        return {
            "total_sales": total_sales,
            "total_orders": len(self.orders),
            "popular_products": self.get_popular_products()
        }

    def get_popular_products(self):
        product_counts = {}
        for order in self.orders:
            for product, qty in order.items.items():
                product_counts[product] = product_counts.get(product, 0) + qty
        return sorted(product_counts.items(), key=lambda x: x[1], reverse=True)

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.default_fg = self.cget('foreground')
        self.placeholder_color = 'gray30'
        
        self.bind("<FocusIn>", self.clear_placeholder)
        self.bind("<FocusOut>", self.set_placeholder)
        
        self.set_placeholder()

    def clear_placeholder(self, event=None):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg, font=('Arial', 11))

    def set_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground=self.placeholder_color, font=('Arial', 10, 'italic'))

    def get_value(self):
        value = self.get().strip()
        return "" if value == self.placeholder else value

class BakeryGUI:

    def __init__(self, master):
        self.master = master
        self.manager = BakeryManager()
        master.title("Bakery Management System")
        window_icon_path = resource_path(r"icons\icon.ico")
        self.master.iconbitmap(window_icon_path)  
        
        master.configure(bg='blue')
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Color scheme
        self.config_file = "config.ini"
        self.bg_color = "gray80"
        self.primary_color = "#0e6c00"
        self.secondary_color = "#7ce4b8"
        self.heading_color = "blue"
        self.entry_label_color = "black"
        self.label_font_style = ('Calisto MT', 12,'bold')

        # Configure widget styles
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 15, 'bold'), padding=6, 
                           background=self.primary_color, foreground='white')
        self.style.map('TButton',
                      background=[('active', self.secondary_color), ('disabled', '#E0E0E0')],
                      foreground=[('active', 'black')])
        
        self.style.configure('Header.TLabel', font=('Times New Roman', 25, 'bold'), 
                           foreground=self.heading_color)
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 11, 'bold'))
        self.style.configure('TEntry', font=('Arial', 10), padding=5)
        
        # Main container structure
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill='both', expand=True)
        
        # Content frame for dynamic views
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_main_menu()
        self.load_window_geometry()
        master.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_window_geometry(self):
        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)
            if "Geometry" in config:
                geometry = config["Geometry"].get("size", "")
                state = config["Geometry"].get("state", "normal")
                if geometry:
                    self.master.geometry(geometry)
                    self.master.update_idletasks()
                    self.master.update()
                if state == "zoomed":
                    self.master.state("zoomed")  # Restore maximized state
                elif state == "iconic":
                    self.master.iconify()  # Restore minimized state

    def save_window_geometry(self):
        config = configparser.ConfigParser()
        config["Geometry"] = {
            "size": self.master.geometry(),
            "state": self.master.state()  # Save window state (normal, maximized, etc.)
        }
        with open(self.config_file, "w") as f:
            config.write(f)

    def on_close(self):
        """Handle window close event"""
        self.save_window_geometry()
        self.master.destroy()

    def create_main_menu(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Main Menu", style='Header.TLabel').pack(pady=20)
        
        menu_items = [
            ("Inventory Management", self.inventory_management),
            ("Product Management", self.product_management),
            ("Order Management", self.order_management),
            ("Staff Management", self.staff_management),
            ("Sells Report", self.sells_report_management),
            ("Exit", self.on_close)
        ]
        
        for text, command in menu_items:
            btn = ttk.Button(self.content_frame, text=text, command=command)
            btn.pack(fill='x', pady=5, padx=40, ipady=8)

    def clear_content(self):
        """Clears only the dynamic content area"""
        if self.content_frame.winfo_exists():  # Check if frame exists
            for widget in self.content_frame.winfo_children():
                widget.destroy()

    def inventory_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Inventory Management", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Add Ingredient", self.add_ingredient_window),
            ("Restock Ingredient", self.restock_ingredient_window),
            ("View Inventory", self.view_inventory),
            ("Return to Main Menu", self.create_main_menu)
        ]
        
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command).pack(fill='x', pady=4, padx=30, ipady=5)

    def add_ingredient_window(self):
        self.clear_content()

        ttk.Label(self.content_frame, text="Add Ingredient", style='Header.TLabel').pack(pady=10)

        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(padx=20, pady=20)

        fields = [
            ("Name:", "name_entry", "Enter ingredient name"),
            ("Initial Quantity:", "quantity_entry", "Enter quantity"),
            ("Unit:", "unit_entry", "e.g., grams"),
            ("Reorder Level:", "reorder_entry", "Enter reorder level")
        ]

        self.entries = {}  # Store for access in back button
        for row, (label, entry_name, placeholder) in enumerate(fields):
            ttk.Label(form_frame, text=label, foreground=self.entry_label_color, font=self.label_font_style).grid(row=row, column=0, sticky='w', pady=5)
            entry = PlaceholderEntry(form_frame, placeholder=placeholder)
            entry.grid(row=row, column=1, pady=5, padx=10)
            self.entries[entry_name] = entry

        def submit():
            try:
                values = {
                    key: entry.get_value() for key, entry in self.entries.items()
                }

                if any(v == "" for v in values.values()):
                    messagebox.showerror("Error", "All fields are required.")
                    return

                self.manager.add_ingredient(
                    values['name_entry'],
                    float(values['quantity_entry']),
                    values['unit_entry'],
                    float(values['reorder_entry'])
                )
                messagebox.showinfo("Success", "Ingredient added!")
                self.clear_content()
                self.add_ingredient_window()
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric input!")

        def move_to_inventory_management():
            for entry in self.entries.values():
                if entry.get_value() != "":
                    if messagebox.askyesno("Confirmation", "Are you sure, do you want to leave?"):
                        self.inventory_management()
                    return
            self.inventory_management()

        ttk.Button(form_frame, text="Submit", command=submit).grid(row=4, columnspan=2, pady=15)
        ttk.Button(form_frame, text="◄ Back", command=move_to_inventory_management).grid(row=5, columnspan=2, pady=15)

    def product_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Product Management", style='Header.TLabel').pack(pady=10)
        
        buttons = [
            ("Add Product", self.add_product_window),
            ("Product Status", self.product_status_window),
            ("View Products", self.view_products),
            ("Return to Main Menu", self.create_main_menu)
        ] 
        for text, command in buttons:
            ttk.Button(self.content_frame, text=text, command=command).pack(fill='x', pady=4, padx=30, ipady=5)

    def view_products(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Products", style='Header.TLabel').pack(pady=10)
        
        # Create container frame for centering
        container = ttk.Frame(self.content_frame)
        container.pack(fill='both', expand=True)
        
        # Centered frame for treeview
        tree_frame = ttk.Frame(container)
        tree_frame.place(relx=0.5, rely=0.4, anchor='center')  # Center alignment

        tree = ttk.Treeview(tree_frame, columns=("Product", "Price","Quantity", "Recipe", 'Action'), show='headings', height=12)
        
        # Configure columns
        tree.column("Product", width=200, anchor='center', minwidth=50)
        tree.column("Price", width=100, anchor='center', minwidth=80)
        tree.column("Quantity", width=100, anchor='center', minwidth=80)
        tree.column("Recipe", width=450, anchor='center', minwidth=100)
        tree.column("Action", width=100, anchor='center', minwidth=80)
        
        # Configure headings
        tree.heading("Product", text="Product Name")
        tree.heading("Price", text="Price")
        tree.heading("Quantity", text="Quantity")
        tree.heading("Recipe", text="Recipe Requirements")
        tree.heading("Action", text="Action")
        
        # Insert data
        for product in self.manager.products:
            recipe_str = ", ".join([f"{ing}: {qty}" for ing, qty in product.recipe.items()])
            tree.insert("", "end", values=(
                product.name,
                f"${product.price:.2f}",
                product.quantity,
                recipe_str,
                "❌ Delete"
            ))
        
        def on_tree_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)
                
                if column == "#5":  # Action column
                    product_name = tree.item(item, "values")[0]
                    delete_product(product_name)

        tree.bind("<Button-1>", on_tree_click)

        def delete_product(product_name):
            confirm = messagebox.askyesno("Confirm Delete", f"Delete {product_name}?")
            if confirm:
                # Remove from manager and save
                self.manager.products = [p for p in self.manager.products if p.name != product_name]
                self.manager.save_data()
                # Refresh the view
                self.view_products()
                
        # Add scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Return button (centered below tree)
        ttk.Button(container, 
                text="◄ Back", 
                command=self.product_management
                ).pack(side='bottom', pady=10, anchor='center')

    def add_product_window(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Add Product", style='Header.TLabel').pack(pady=10)
        
        main_frame = ttk.Frame(self.content_frame)
        main_frame.place(relx=0.5, rely=0.55, anchor='center')
        
        # Product Info
        ttk.Label(main_frame, text="Product Name:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=0, column=2, pady = 10,)
        name_entry = PlaceholderEntry(main_frame, placeholder="Enter product name")
        name_entry.grid(row=0, column=3)

        # Price Entry
        ttk.Label(main_frame, text="Price:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=1, column=2,)
        price_entry = PlaceholderEntry(main_frame, placeholder="Enter price")
        price_entry.grid(row=1, column=3,)

        ttk.Label(main_frame, text="Initial Quantity:", foreground=self.entry_label_color,font=self.label_font_style).grid(row=2, column=2)
        quantity_entry = PlaceholderEntry(main_frame, placeholder="Enter initial quantity")
        quantity_entry.grid(row=2, column=3, pady= 7)

        # Ingredients container with scrollbar
        container = ttk.Frame(main_frame)
        container.grid(row=3, column=2, columnspan=2, sticky='nsew', pady=10)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons below the scroll area
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=2, columnspan=2, pady=10)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        scrollable_frame.bind("<Configure>", on_frame_configure)

        def on_mousewheel(event):
            if canvas.winfo_exists(): 
                if event.delta:
                    canvas.yview_scroll(-1 * int(event.delta/120), "units")
                else:
                    if event.num == 4:
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:
                        canvas.yview_scroll(1, "units")
        
        # Bind mousewheel to canvas and scrollable_frame
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel)
        canvas.bind_all("<Button-5>", on_mousewheel)

        # IN BAKERYGUI CLASS - add_product_window()
        def submit_product(name_entry, price_entry, quantity_entry, ingredients_frame):  # Modified
            try:
                recipe = {}
                # Collect ingredient entries
                for row_frame in ingredients_frame.winfo_children():
                    entries = row_frame.winfo_children()
                    if len(entries) >= 2:
                        ingredient_entry = entries[0]
                        quantity_entry = entries[1]
                        
                        ingredient = ingredient_entry.get_value()
                        quantity = quantity_entry.get_value()
                        
                        if ingredient and quantity:
                            recipe[ingredient] = float(quantity)

                # Validate inputs
                product_name = name_entry.get_value()
                price = price_entry.get_value()
                quantity = quantity_entry.get_value()  # NEW quantity field
                
                if not product_name or not recipe or not quantity:
                    messagebox.showerror("Error", "Product name, quantity, and at least one ingredient are required!")
                    return
                
                # Convert numeric values
                price = float(price)
                quantity = float(quantity)  # NEW quantity conversion

                self.manager.add_product(
                    product_name,
                    price,
                    recipe,
                    quantity  # NEW quantity parameter
                )
                messagebox.showinfo("Success", "Product added!")
                self.clear_content()
                self.add_product_window()
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric input!")

        def add_ingredient_row(parent_frame, canvas):
            row_frame = ttk.Frame(parent_frame, borderwidth=0, relief="solid")
            row_frame.pack(fill=tk.X, pady=2, expand=True, anchor='center')
            
            # Ingredient entry
            ing_entry = PlaceholderEntry(row_frame, placeholder="Ingredient name")
            ing_entry.pack(side='left', padx=5, expand=True, fill='x')
            
            # Quantity entry
            qty_entry = PlaceholderEntry(row_frame, placeholder="Quantity", width=8)
            qty_entry.pack(side='left', padx=5, expand=True, fill='x')
            
            # Delete button
            ttk.Button(row_frame, 
                    text="❌", 
                    width=3,
                    command=lambda: delete_ingredient_row(row_frame, canvas)
                    ).pack(side='right', padx=5, fill='x', expand=True)

            parent_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(1.0)  

            def delete_ingredient_row( row_frame, canvas):
                row_frame.destroy()
                canvas.config(scrollregion=canvas.bbox("all"))
        
        def back():
            if name_entry.get_value() or price_entry.get_value():
                if messagebox.askyesno("Confirmation", "Are you sure, do you want to leave?"):
                    self.product_management()
            else:
                self.product_management()    
        
        ttk.Button(button_frame, text="◄ Back", command=back).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, 
                text="Add Ingredient", 
                command=lambda: add_ingredient_row(scrollable_frame, canvas),
                ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, 
                text="Submit", 
                command=lambda: submit_product(name_entry, price_entry, quantity_entry, scrollable_frame)
                ).pack(side=tk.LEFT, padx=5)
                
    def order_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Order Management", style='Header.TLabel').pack(pady=10)
        
        ttk.Button(self.content_frame, text="Create New Order", command=self.create_order_window).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="View All Orders", command=self.view_orders).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="Update Order Status", command=self.update_order_status_window).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="Return to Main Menu", command=self.create_main_menu).pack(pady=5, fill='x', ipady=5)

    def create_order_window(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="New Order", style='Header.TLabel').pack(pady=10)
        
        main_frame = ttk.Frame(self.content_frame)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Customer Info
        ttk.Label(main_frame, text="Customer Name:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=0, column=0, pady=10)
        customer_entry = PlaceholderEntry(main_frame, placeholder="Enter Customer name")
        customer_entry.grid(row=0, column=1, padx=10)

        # Order Items container with scrollbar
        container = ttk.Frame(main_frame)
        container.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=10)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Buttons below the scroll area
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        def add_item_row(parent_frame, canvas):
            row_frame = ttk.Frame(parent_frame)
            row_frame.pack(fill=tk.X, pady=2, expand=True)
            
            # Product entry
            product_entry = PlaceholderEntry(row_frame, placeholder="Available Product name")
            product_entry.pack(side='left', padx=5, expand=True, fill='x')
            
            # Quantity entry
            qty_entry = PlaceholderEntry(row_frame, placeholder="Quantity", width=8)
            qty_entry.pack(side='left', padx=5, expand=True, fill='x')
            
            # Delete button
            ttk.Button(row_frame, 
                    text="❌", 
                    width=3,
                    command=lambda: delete_item_row(row_frame, canvas)
                    ).pack(side='right', padx=5)

            parent_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(1.0)

        def delete_item_row(row_frame, canvas):
            row_frame.destroy()
            canvas.config(scrollregion=canvas.bbox("all"))

        def submit_order():
            try:
                items = {}
                # Collect all valid item entries
                for row_frame in scrollable_frame.winfo_children():
                    entries = row_frame.winfo_children()
                    if len(entries) >= 2:
                        product_entry = entries[0]
                        qty_entry = entries[1]
                        
                        product = product_entry.get_value()
                        quantity = qty_entry.get_value()
                        
                        if product and quantity:
                            items[product] = int(quantity)
                
                customer = customer_entry.get_value()
                
                if not customer or not items:
                    messagebox.showerror("Error", "Customer name and items are required!")
                    return

                # Validate product names
                invalid_products = []
                for product_name in items:
                    if not any(p.name == product_name for p in self.manager.products):
                        invalid_products.append(product_name)
                
                if invalid_products:
                    messagebox.showerror("Error", f"Product(s) not found: {', '.join(invalid_products)}")
                    return
                
                if self.manager.create_order(customer, items):
                    if hasattr(self, 'products_view_open') and self.products_view_open:
                        self.view_products()
                    messagebox.showinfo("Success", "Order created successfully!")
                    self.clear_content()
                    self.create_order_window()
                else:
                    messagebox.showerror("Error", "Insufficient stock for some ingredients!")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity input!")

        def back():
            if customer_entry.get_value() or any(row.winfo_children() for row in scrollable_frame.winfo_children()):
                if messagebox.askyesno("Confirmation", "Are you sure, you want to leave?"):
                    self.order_management()
            else:
                self.order_management()

        # Control buttons
        ttk.Button(button_frame, text="◄ Back", command=back).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, 
                text="Add Item", 
                command=lambda: add_item_row(scrollable_frame, canvas)
                ).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, 
                text="Submit Order", 
                command=submit_order
                ).pack(side=tk.LEFT, padx=5)

        # Add initial empty row
        add_item_row(scrollable_frame, canvas)

    def view_orders(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="View Orders", style='Header.TLabel').pack(pady=10)
        
        # Create container frame for Treeview and scrollbars
        container = ttk.Frame(self.content_frame)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create Treeview
        tree = ttk.Treeview(container, columns=("ID", "Customer Name", "Items", "Total", "Status", "Action"), show='headings')
        
        tree.column("ID", anchor="center", width=150)
        tree.column("Customer Name", anchor="center", width=200)
        tree.column("Items", anchor="center", width=400)
        tree.column("Total", anchor="center", width=100)
        tree.column("Status", anchor="center", width=80)
        tree.column("Action", anchor="center", width=60)

        columns = ["ID", "Customer Name", "Items", "Total", "Status", "Action"]

        for col in columns:
            tree.heading(col, text=col, anchor="center")

        # Add scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights for resizing
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Insert data
        for order in self.manager.orders:
            items_str = ", ".join([f"{k} ({v})" for k, v in order.items.items()])
            tree.insert("", "end", values=(
                order.order_id,
                order.customer_name,
                items_str,
                f"${order.total:.2f}",
                order.status,
                '❌'
            ))
        
        # Click handler for deletion
        def on_tree_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)
                values = tree.item(item, "values")

                if column == "#6":  # Action column
                    order_id = tree.item(item, "values")[0]
                    
                    for idx, order in enumerate(self.manager.orders):
                        if order.order_id == order_id:
                            if messagebox.askyesno("Confirm Delete", f"Delete order {order_id}?"):
                                del self.manager.orders[idx]
                                self.manager.save_data()
                                self.view_orders()  # Refresh view
                            break
                
                if column == "#1":  # ID column
                    order_id = values[0]
                    show_copy_id_popup(order_id)
                
        def show_copy_id_popup(order_id):
            popup = tk.Toplevel()
            popup.title("Copy Order ID")
            popup.geometry("300x100")
            
            ttk.Label(popup, text=f"Order ID: {order_id}", font=('Arial', 12)).pack(pady=10)
            
            def copy_id():
                self.master.clipboard_clear()
                self.master.clipboard_append(order_id)
                popup.destroy()
                
            ttk.Button(popup, text="Copy", command=copy_id).pack(pady=5)
            ttk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)
                    
        def on_horizontal_scroll(event):
            if event.delta:
                factor = -1 * (event.delta // 120) * 12  # Scroll 12 times faster
            else:
                # For Linux (Button 6: left, Button 7: right)
                factor = -3 if event.num == 6 else 3
            tree.xview_scroll(factor, "units")
        
        # Bind horizontal scroll events
        tree.bind("<Shift-MouseWheel>", on_horizontal_scroll)
        tree.bind("<Button-4>", on_horizontal_scroll)
        tree.bind("<Button-5>", on_horizontal_scroll)
        
        tree.bind("<Button-1>", on_tree_click)
        
        ttk.Button(self.content_frame, text="◄ Back", command=self.order_management).pack(pady=10)
     
    def update_order_status_window(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Update Order & Product Quantity", style='Header.TLabel').pack(pady=10)
        
        container = ttk.Frame(self.content_frame)
        container.place(relx=0.5, rely=0.4, anchor='center')

        # Order ID Entry
        ttk.Label(container, text="Order ID:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=0, column=0, pady=10)
        order_id_entry = PlaceholderEntry(container, placeholder="Enter order ID")
        order_id_entry.grid(row=0, column=1, pady=10)
        
        # Product Name Entry
        ttk.Label(container, text="Product Name:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=1, column=0, pady=10, padx=5)
        product_entry = PlaceholderEntry(container, placeholder="Enter product name")
        product_entry.grid(row=1, column=1, pady=10)
        
        # Quantity Entry
        ttk.Label(container, text="Quantity:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=2, column=0, pady=10, padx=5)
        quantity_entry = PlaceholderEntry(container, placeholder="Enter quantity")
        quantity_entry.grid(row=2, column=1, pady=10)
        
        def submit():
            order_id = order_id_entry.get_value()
            product_name = product_entry.get_value()
            quantity = quantity_entry.get_value()
            
            # Validate all fields
            if not all([order_id, product_name, quantity]):
                messagebox.showerror("Error", "All fields are required!")
                return
                
            try:
                quantity = float(quantity)
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity! Must be positive number.")
                return

            # Find order
            order = next((o for o in self.manager.orders if o.order_id == order_id), None)
            if not order:
                messagebox.showerror("Error", "Order not found!")
                return

            # Find product
            product = next((p for p in self.manager.products if p.name == product_name), None)
            if not product:
                messagebox.showerror("Error", "Product not found!")
                return

            # Check stock
            if product.quantity < quantity:
                messagebox.showerror("Error", f"Only {product.quantity} {product_name} available!")
                return

            # Update order items
            if product_name in order.items:
                order.items[product_name] += quantity
            else:
                order.items[product_name] = quantity

            # Update order total
            order.total += product.price * quantity
            
            # Update product quantity
            product.quantity -= quantity
            
            # Update order status
            order.status = "Updated"
            
            self.manager.save_data()
            messagebox.showinfo("Success", f"Added {quantity} {product_name} to Order {order_id}")
            self.update_order_status_window()

        def back():
            if any([order_id_entry.get_value(), product_entry.get_value(), quantity_entry.get_value()]):
                if messagebox.askyesno("Confirm Exit", "Discard changes?"):
                    self.order_management()
            else:
                self.order_management()

        ttk.Button(container, text="◄ Back", command=back).grid(row=3, column=0, pady=20, padx=(75,0))
        ttk.Button(container, text="Update", command=submit).grid(row=3, column=1, pady=20)

    def staff_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Staff Management", style='Header.TLabel').pack(pady=10)
        
        ttk.Button(self.content_frame, text="Add Staff Member", command=self.add_staff_window).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="View Staff Members", command=self.view_staff).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="Return to Main Menu", command=self.create_main_menu).pack(pady=5, fill='x', ipady=5)

    def add_staff_window(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Add Staff Member", style='Header.TLabel').pack(pady=10)
        
        main_frame = ttk.Frame(self.content_frame)
        main_frame.place(relx=0.5, rely=0.4, anchor='center')
        
        ttk.Label(main_frame, text="Name:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=0, column=0)
        name_entry = PlaceholderEntry(main_frame, placeholder="Staff name")
        name_entry.grid(row=0, column=1)
        
        ttk.Label(main_frame, text="Role:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=1, column=0, padx=10)
        roll_entry = PlaceholderEntry(main_frame, placeholder="e.g., 1234567890")
        roll_entry.grid(row=1, column=1, pady=10)
        
        ttk.Label(main_frame, text="Shifts (comma-separated):", foreground=self.entry_label_color, font=self.label_font_style).grid(row=2, column=0)
        shifts_entry = PlaceholderEntry(main_frame, placeholder="e.g., Mon 8:00 AM - 5:00 PM")
        shifts_entry.grid(row=2, column=1)
        
        def submit():
            name = name_entry.get_value()
            roll = roll_entry.get_value()
            shifts_input = shifts_entry.get_value()
            
            # Validate inputs
            if not name and not roll and not shifts_input:
                messagebox.showerror("Error", "All fields are required!")
                return
            
            if not name:
                messagebox.showerror("Error", "Name is required!")
                return
            if not roll:
                messagebox.showerror("Error", "Role is required!")
                return
            
            try:
                role_id = int(roll)  # Convert to integer
            except ValueError:
                messagebox.showerror("Error", "Role must be a numeric ID ")
                return
            
            if not shifts_input:
                messagebox.showerror("Error", "Shifts are required!")
                return
            
            # Check if role already exists
            existing_staff = next((s for s in self.manager.staff if s.role == roll), None)
            if existing_staff:
                messagebox.showerror("Error", f"Role {roll} already exists for staff member: {existing_staff.name}")
                return
            
            # Process shifts
            shifts = [shift.strip() for shift in shifts_input.split(',') if shift.strip()]
            if not shifts:
                messagebox.showerror("Error", "At least one valid shift must be provided!")
                return
            
            # Add staff and return to management
            self.manager.add_staff(name, roll, shifts)
            messagebox.showinfo("Success", "Staff member added!")
            self.add_staff_window()

        def back():
            if any([name_entry.get_value(), roll_entry.get_value(), shifts_entry.get_value()]):
                if messagebox.askyesno("Confirm Exit", "Discard changes?"):
                    self.staff_management()
            else:
                self.staff_management()

        ttk.Button(main_frame, text="◄ Back", command=back).grid(row=3, column=0, pady=30, padx=(75,0))
        ttk.Button(main_frame, text="Submit", command=submit).grid(row=3, column=1, pady=30)

    def view_staff(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="View Staff Members", style='Header.TLabel').pack(pady=10)
        
        # Create container frame for Treeview and scrollbar
        container = ttk.Frame(self.content_frame)
        container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create Treeview with columns
        tree = ttk.Treeview(
            container, 
            columns=("Name", "Role", "Shifts", "Action"), 
            show='headings'
        )
        
        # Configure column properties (widths and alignment)
        tree.column("#0", width=50, anchor='center', minwidth=50)  # ID column
        tree.column("Name", width=200, anchor='center', minwidth=100)
        tree.column("Role", width=150, anchor='center', minwidth=80)
        tree.column("Shifts", width=300, anchor='center', minwidth=150)
        tree.column("Action", width=70, anchor='center', minwidth=60)
        
        # Configure headings (text and alignment)
        tree.heading("#0", text="ID", anchor='center')
        tree.heading("Name", text="Name", anchor='center')
        tree.heading("Role", text="Role", anchor='center')
        tree.heading("Shifts", text="Shifts", anchor='center')
        tree.heading("Action", text="Action", anchor='center')
        
        # Add vertical scrollbar
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Configure grid expansion
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Insert data with centered alignment
        for idx, staff in enumerate(self.manager.staff):
            tree.insert(
                "", "end", 
                text=str(idx+1),  # ID in #0 column
                values=(staff.name, staff.role, ", ".join(staff.shifts), '❌ Delete'),
                tags=(str(idx),)  # Store the index as a string in tags
            )
        
        # Click event handler for delete button
        def on_tree_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)
                
                if column == "#4":  # Action column
                    if item:
                        # Get the stored index from tags
                        item_tags = tree.item(item, "tags")
                        if item_tags:
                            try:
                                index = int(item_tags[0])
                                delete_staff(index)
                            except (ValueError, IndexError):
                                messagebox.showerror("Error", "Invalid item selection!", parent=self.content_frame)

        tree.bind("<1>", on_tree_click)
        
        def delete_staff(index):
            try:
                if 0 <= index < len(self.manager.staff):
                    confirm = messagebox.askyesno(
                        "Confirm Delete", 
                        f"Are you sure you want to delete {self.manager.staff[index].name}?",
                        parent=self.content_frame  # Keep focus on current window
                    )
                    if confirm:
                        del self.manager.staff[index]
                        self.manager.save_data()
                        self.view_staff()  # Refresh the view
                else:
                    messagebox.showerror("Error", "Invalid staff member selection!", parent=self.content_frame)
            except (IndexError, TypeError):
                messagebox.showerror("Error", "Invalid staff member selection!", parent=self.content_frame)

        # Back button
        ttk.Button(self.content_frame, text="◄ Back", command=self.staff_management).pack(pady=10)

    def restock_ingredient_window(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Restock Ingredient", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(padx=20, pady=20)

        ttk.Label(form_frame, text="Ingredient Name:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=0, column=0, padx=10, pady=10)
        name_entry = PlaceholderEntry(form_frame, placeholder="Ingredient name")
        name_entry.grid(row=0, column=1, padx=10)

        ttk.Label(form_frame, text="Quantity to Add:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=1, column=0, padx=10, pady=10)
        quantity_entry = PlaceholderEntry(form_frame, placeholder="Quantity")
        quantity_entry.grid(row=1, column=1, padx=10)

        def submit():
            name = name_entry.get_value()
            quantity = quantity_entry.get_value()

            if not name or not quantity:
                return            
            try:
                quantity = float(quantity)
                if self.manager.restock_ingredient(name, quantity):
                    messagebox.showinfo("Success", "Restocked successfully!")
                    self.clear_content()
                    self.restock_ingredient_window()
                else:
                    messagebox.showerror("Error", "Ingredient not found!")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity input! \nPlease add Numeric Input")

        def back():
            if name_entry.get_value() or quantity_entry.get_value():
                if messagebox.askyesno("Confirmation", "Are you sure, you want to leave??"):
                    self.inventory_management()
            else:
                self.inventory_management()

        ttk.Button(form_frame, text="Restock", command=submit).grid(row=2, columnspan=2, pady=10)
        ttk.Button(form_frame, text="◄ Back", command=back).grid(row=3, columnspan=2, pady=10)

    def view_inventory(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Current Inventory", style='Header.TLabel').pack(pady=10)

        # Create Treeview with scrollbar
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True)

        columns = ("Name", "Quantity", "Unit", "Reorder Level", "Action")
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='none')

        def _on_mousewheel(event):
            if event.delta:
                tree.yview_scroll(-1 * int(event.delta/120), "units")
            else:
                if event.num == 4:
                    tree.yview_scroll(-1, "units")
                elif event.num == 5:
                    tree.yview_scroll(1, "units")

        # Bind for Windows/Mac
        tree.bind("<MouseWheel>", _on_mousewheel)
        # Bind for Linux
        tree.bind("<Button-4>", _on_mousewheel)
        tree.bind("<Button-5>", _on_mousewheel)

        
        # Configure column headings and alignment
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center', width=120)
        tree.column("Name", width=180)
        tree.column("Action", width=80)

        # Add scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Insert data with delete buttons
        for idx, ing in enumerate(self.manager.ingredients):
            tree.insert("", "end", 
                    values=(ing.name, f"{ing.quantity}", ing.unit, f"{ing.reorder_level}", "❌ Delete"),
                    tags=(idx,))  # Store index in tags

        # Configure tag for delete button styling
        tree.tag_configure('delete', foreground='red', font=('Arial', 9, 'bold'))
        
        # Click event handler
        def on_tree_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)
                
                if column == "#5":  # Action column
                    index = int(tree.item(item, "tags")[0])
                    delete_ingredient(index)

        tree.bind("<Button-1>", on_tree_click)
        ttk.Button(self.content_frame, text="◄ Back", command=self.inventory_management).pack(pady=10)

        def delete_ingredient(index):
            try:
                ingredient = self.manager.ingredients[index]
                confirm = messagebox.askyesno(
                    "Confirm Delete", 
                    f"Are you sure you want to delete {ingredient.name}?",
                    parent=self.content_frame  # Keep focus on inventory window
                )
                if confirm:
                    del self.manager.ingredients[index]
                    self.manager.save_data()
                    self.view_inventory()  # Refresh the view
            except (IndexError, TypeError):
                messagebox.showerror("Error", "Ingredient not found!", parent=self.content_frame)

    def product_status_window(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Update Product Quantity", style='Header.TLabel').pack(pady=10)

        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(padx=20, pady=20)

        # Product Name Entry
        ttk.Label(form_frame, text="Product Name:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=0, column=0, sticky='w', pady=5)
        product_entry = PlaceholderEntry(form_frame, placeholder="Enter product name")
        product_entry.grid(row=0, column=1, pady=5, padx=10)

        # Quantity Entry
        ttk.Label(form_frame, text="Quantity to Add:", foreground=self.entry_label_color, font=self.label_font_style).grid(row=1, column=0, sticky='w', pady=5)
        quantity_entry = PlaceholderEntry(form_frame, placeholder="Enter quantity")
        quantity_entry.grid(row=1, column=1, pady=5, padx=10)

        def submit():
            product_name = product_entry.get_value()
            quantity = quantity_entry.get_value()
            
            if not product_name or not quantity:
                messagebox.showerror("Error", "Both fields are required!")
                return
                
            try:
                quantity = float(quantity)
                product = next((p for p in self.manager.products if p.name == product_name), None)
                
                if product:
                    product.quantity += quantity
                    self.manager.save_data()
                    messagebox.showinfo("Success", f"Added {quantity} units to {product_name}!")
                    self.product_status_window()
                else:
                    messagebox.showerror("Error", "Product not found!")
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity input!")

        def back():
            if product_entry.get_value() or quantity_entry.get_value():
                if messagebox.askyesno("Confirm", "Discard changes and return?"):
                    self.product_management()
            else:
                self.product_management()

        ttk.Button(form_frame, text="Submit", command=submit).grid(row=2, columnspan=2, pady=10)
        ttk.Button(form_frame, text="◄ Back", command=back).grid(row=3, columnspan=2, pady=5)
        
    def sells_report_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Sells Report", style='Header.TLabel').pack(pady=10)
        
        ttk.Button(self.content_frame, text="Pending Orders", command=self.pending_orders).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="Sold Items", command=self.sold_items).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="Earnings", command=self.earning).pack(pady=5, fill='x', ipady=5)
        ttk.Button(self.content_frame, text="Return to Main Menu", command=self.create_main_menu).pack(pady=5, fill='x', ipady=5)

    def pending_orders(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Pending Orders", style='Header.TLabel').pack(pady=10)
        
        # Create container frame for Treeview and scrollbars
        container = ttk.Frame(self.content_frame)
        container.pack(fill='both', expand=True, padx=20, pady=10)

        # Create Treeview with columns
        tree = ttk.Treeview(
            container,
            columns=("Select", "Order ID", "Customer Name", "Items", "Total", "Timestamp"),
            show='headings',
            selectmode='none'
        )

        # Configure column headings and alignment
        tree.column("Select", width=80, anchor='center')
        tree.column("Order ID", width=150, anchor='center')
        tree.column("Customer Name", width=150, anchor='center')
        tree.column("Items", width=300, anchor='center')
        tree.column("Total", width=100, anchor='center')
        tree.column("Timestamp", width=150, anchor='center')

        tree.heading("Select", text="Select", anchor='center')
        tree.heading("Order ID", text="Order ID", anchor='center')
        tree.heading("Customer Name", text="Customer Name", anchor='center')
        tree.heading("Items", text="Items", anchor='center')
        tree.heading("Total", text="Total", anchor='center')
        tree.heading("Timestamp", text="Timestamp", anchor='center')

        # Add scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Checkbox images
        self.checked_img = tk.PhotoImage(width=18, height=18)
        self.unchecked_img = tk.PhotoImage(width=18, height=18)
        self.checked_img.put(("green",), to=(0, 0, 17, 17))
        self.unchecked_img.put(("white",), to=(0, 0, 17, 17))

        # Track selected orders
        self.selected_orders = set()

        # Insert data with checkboxes
        for order in self.manager.orders:
            if order.status == "Pending":
                items_str = ", ".join([f"{k} ({v})" for k, v in order.items.items()])
                tree.insert("", "end", 
                        values=("☐", order.order_id, order.customer_name, items_str,
                                f"${order.total:.2f}", 
                                order.timestamp.strftime("%Y-%m-%d %I:%M %p")),
                        tags=(order.order_id,))

        # Click handler for checkboxes
        def on_tree_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)
                
                if column == "#1":  # Select column
                    order_id = tree.item(item, "tags")[0]
                    current_val = tree.item(item, "values")[0]
                    
                    if current_val == "☐":
                        tree.item(item, values=("✓", *tree.item(item, "values")[1:]))
                        self.selected_orders.add(order_id)
                    else:
                        tree.item(item, values=("☐", *tree.item(item, "values")[1:]))
                        self.selected_orders.discard(order_id)
                    
                    # Toggle button visibility
                    btn_mark.pack() if self.selected_orders else btn_mark.pack_forget()

        tree.bind("<Button-1>", on_tree_click)

        # Mark as Sold button
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        btn_mark = ttk.Button(
            btn_frame,
            text="Mark as Sold",
            command=lambda: self.mark_orders_complete(),
            style='TButton'
        )
        btn_mark.pack_forget()  # Initially hidden

        def mark_orders_complete():
            for order in self.manager.orders:
                if order.order_id in self.selected_orders:
                    order.status = "Completed"
            self.manager.save_data()
            self.selected_orders.clear()
            self.sold_items()  # Directly refresh the sold items view

        self.mark_orders_complete = mark_orders_complete
        
        ttk.Button(self.content_frame, 
                text="◄ Back", 
                command=self.sells_report_management).pack(pady=10)

    def sold_items(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Sold Items Report", style='Header.TLabel').pack(pady=10)

        # Create container frame for Treeview and scrollbars
        container = ttk.Frame(self.content_frame)
        container.pack(fill='both', expand=True, padx=20, pady=10)

        # Create Treeview with updated columns
        tree = ttk.Treeview(
            container,
            columns=("Customer Name", "Order ID", "Product Name", "Quantity Sold", "Total Revenue", 'Action'),
            show='headings',
            selectmode='none'
        )

        # Configure column headings and alignment
        tree.column("Customer Name", width=150, anchor='center')
        tree.column("Order ID", width=120, anchor='center')
        tree.column("Product Name", width=150, anchor='center')
        tree.column("Quantity Sold", width=100, anchor='center')
        tree.column("Total Revenue", width=120, anchor='center')
        tree.column("Action", width=80, anchor='center')

        tree.heading("Customer Name", text="Customer Name", anchor='center')
        tree.heading("Order ID", text="Order ID", anchor='center')
        tree.heading("Product Name", text="Product Name", anchor='center')
        tree.heading("Quantity Sold", text="Quantity Sold", anchor='center')
        tree.heading("Total Revenue", text="Total Revenue", anchor='center')
        tree.heading("Action", text="Action", anchor='center')

        # Add scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Insert data
        total_revenue = 0
        for order in self.manager.orders:
            if order.status == "Completed":
                for product_name, qty in order.items.items():
                    price = self.manager.get_product_price(product_name)
                    revenue = price * qty
                    total_revenue += revenue
                    tree.insert("", "end", values=(
                        order.customer_name,
                        order.order_id,
                        product_name,
                        qty,
                        f"${revenue:.2f}",
                        '❌ Delete'
                    ))

        # Add totals row
        tree.insert("", "end", values=("TOTAL", "", "", "", f"${total_revenue:.2f}"), tags=('total',))
        tree.tag_configure('total', background='#e8f4ff', font=('Arial', 10, 'bold'))

        # Click event handler for delete button
        def on_tree_click(event):
            region = tree.identify("region", event.x, event.y)
            if region == "cell":
                column = tree.identify_column(event.x)
                item = tree.identify_row(event.y)

                if column == "#6":  # Action column
                    product_name = tree.item(item, "values")[2]
                    order_id = tree.item(item, "values")[1]

                    confirm = messagebox.askyesno(
                        "Confirm Delete",
                        f"Are you sure you want to delete {product_name} from Order {order_id}?"
                    )
                    if confirm:
                        # Remove the item from the order
                        for order in self.manager.orders:
                            if order.order_id == order_id:
                                if product_name in order.items:
                                    del order.items[product_name]
                                    # Save changes
                                    self.manager.save_data()
                                    # Refresh the view
                                    self.sold_items()
                                break

        tree.bind("<1>", on_tree_click)

        ttk.Button(self.content_frame, text="◄ Back", command=self.sells_report_management).pack(pady=10)

    def earning(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Earnings Report", style='Header.TLabel').pack(pady=10)

        # Time period calculations
        now = datetime.now()
        daily_total = 0
        weekly_total = 0
        monthly_total = 0

        for order in self.manager.orders:
            if order.status == "Completed":
                order_date = order.timestamp
                if order_date.date() == now.date():
                    daily_total += order.total
                if order_date.isocalendar()[1] == now.isocalendar()[1]:
                    weekly_total += order.total
                if order_date.month == now.month:
                    monthly_total += order.total

        # Display metrics
        metrics_frame = ttk.Frame(self.content_frame)
        metrics_frame.pack(pady=20)

        periods = [
            ("Today's Earnings", daily_total),
            ("Weekly Earnings", weekly_total),
            ("Monthly Earnings", monthly_total),
            ("Total Earnings", sum(o.total for o in self.manager.orders if o.status == "Completed"))
        ]

        for i, (label, value) in enumerate(periods):
            ttk.Label(metrics_frame, text=label, font=('Arial', 12, 'bold')).grid(row=i, column=0, padx=20, pady=8, sticky='w')
            ttk.Label(metrics_frame, text=f"${value:.2f}", font=('Arial', 12)).grid(row=i, column=1, padx=20, pady=8, sticky='e')

        ttk.Button(self.content_frame, text="◄ Back", command=self.sells_report_management).pack(pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    app = BakeryGUI(root)
    root.mainloop()