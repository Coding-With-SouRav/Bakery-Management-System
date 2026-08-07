# FEATURES
## Core Data Models
Ingredients: Track name, quantity, unit, and reorder levels.

Products: Manage name, price, recipe (ingredient requirements), and stock quantity.

Orders: Handle customer details, items, totals, status (Pending/Completed), and timestamps.

Staff: Store employee names, roles, and shifts.

## Basic Features
### 1. Inventory Management

Add/restock ingredients.

View inventory with delete functionality.

Low-stock alerts based on reorder levels.

### 2. Product Management

Add products with dynamic recipe inputs.

View/delete products in a scrollable table.

Update product quantities.

### 3. Order Management

Create orders with customer names and items.

Validate stock availability during order creation.

View orders in a table with copyable IDs and deletion.

## Intermediate Features
### 4. Staff Management

Add staff members with roles and shifts.

View/delete staff in an interactive table.

### 5. Sales Reporting

Pending Orders: Track incomplete orders with checkboxes to mark as "Completed."

Sold Items: View completed orders with revenue breakdown and deletion of individual items.

Earnings Report: Display daily, weekly, monthly, and total earnings.

## Advanced Features
### 6. Dynamic UI Components

Scrollable forms for adding ingredients/items.

Placeholder input fields with validation.

Interactive tables (Treeview) with embedded delete buttons.

### 7. Data Persistence

JSON storage for all data (ingredients, products, orders, staff).

Auto-save on changes.

### 8. Window State Management

Save/restore window size and state (maximized/minimized) via config.ini.

### 9. Error Handling & Validation

Input validation for numeric fields (e.g., price, quantity).

Alert messages for invalid operations (e.g., insufficient stock).

## Specialized Tools
Recipe Builder: Dynamically add/remove ingredients when creating products.

Sales Analytics: Time-based revenue calculations (daily/weekly/monthly).

Clipboard Integration: Copy order IDs directly from the UI.

## Summary
This system streamlines bakery operations with a focus on inventory control, order processing, staff management, and sales analytics. Its modular design and GUI make it suitable for small to medium-sized bakeries needing a centralized tool for day-to-day tasks and reporting.

# DEMO Images

![Screenshot 2025-05-05 212042](https://github.com/user-attachments/assets/d8c5d554-35ca-49b8-a89e-656b0866dd67)
![Screenshot 2025-05-05 212016](https://github.com/user-attachments/assets/8d58e73b-4416-49ad-8233-e23e1a8ec543)
![Screenshot 2025-05-05 212122](https://github.com/user-attachments/assets/5e1d5024-bead-4f1d-89bd-579adf6c5125)
![Screenshot 2025-05-05 212108](https://github.com/user-attachments/assets/110ab814-7f2c-425c-8e04-a6116ec4b7d4)
![Screenshot 2025-05-05 212055](https://github.com/user-attachments/assets/50da764b-0405-47f9-8912-35a15cf34334)

