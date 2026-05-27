import json
import os

class StockManager:
    """
    Manages stock records, updates stock based on parsed procurement invoices,
    and flags components falling below safety thresholds.
    """
    def __init__(self, stock_db_path):
        self.stock_db_path = stock_db_path
        self.inventory = {}
        self.load_inventory()

    def load_inventory(self):
        """Loads inventory from JSON file or initializes default values if file missing."""
        if os.path.exists(self.stock_db_path):
            with open(self.stock_db_path, 'r', encoding='utf-8') as f:
                self.inventory = json.load(f)
        else:
            self.inventory = {}

    def save_inventory(self):
        """Saves current inventory back to the JSON database."""
        with open(self.stock_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.inventory, f, indent=2)

    def process_shipment(self, parsed_items):
        """
        Processes a list of parsed items. Updates stock levels and records logs.
        Returns a dict containing update results for reporting.
        """
        results = {}
        
        # Initialize results with existing stock info
        for sku, info in self.inventory.items():
            results[sku] = {
                "name": info["name"],
                "initial_stock": info["stock"],
                "received_qty": 0,
                "new_stock": info["stock"],
                "safety_stock": info["safety_stock"],
                "unit": info.get("unit", "pcs"),
                "category": info.get("category", "General"),
                "status": "OK"
            }

        # Accumulate incoming items
        for item in parsed_items:
            sku = item['sku']
            qty = item['qty']
            
            if sku in results:
                results[sku]["received_qty"] += qty
                results[sku]["new_stock"] += qty
            else:
                # New SKU discovered that was not in stock database
                results[sku] = {
                    "name": item.get('name', sku),
                    "initial_stock": 0,
                    "received_qty": qty,
                    "new_stock": qty,
                    "safety_stock": 10,  # Default safety stock for new items
                    "unit": "pcs",
                    "category": "New Component",
                    "status": "NEW"
                }

        # Update actual database & determine status
        for sku, info in results.items():
            # If the SKU is existing, update inventory dict
            if sku in self.inventory:
                self.inventory[sku]["stock"] = info["new_stock"]
            else:
                # Add to inventory dict
                self.inventory[sku] = {
                    "name": info["name"],
                    "stock": info["new_stock"],
                    "safety_stock": info["safety_stock"],
                    "unit": info["unit"],
                    "category": info["category"]
                }
            
            # Determine stock alert status
            new_stock = info["new_stock"]
            safety = info["safety_stock"]
            initial = info["initial_stock"]
            
            if new_stock < safety:
                info["status"] = "CRITICAL"  # Still below safety even after shipment!
            elif initial < safety and new_stock >= safety:
                info["status"] = "RESTOCKED"  # Saved by shipment!
            elif new_stock <= safety * 1.2:
                info["status"] = "WARNING"    # Nearing threshold (within 20% margin)
            else:
                info["status"] = "OK"

        self.save_inventory()
        return results
