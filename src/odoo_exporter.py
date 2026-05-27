import csv
import json
import os

class OdooExporter:
    """
    Exports procurement data to clean, standard Odoo ERP import schemas (CSV & JSON).
    """
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_csv(self, parsed_items, filename="odoo_import_procurement.csv"):
        """
        Generates standard Odoo import CSV for Inventory Adjustments / Purchase Order Lines.
        Odoo import headers used:
        - product_id/default_code: Internal reference SKU
        - product_id/name: Name of the product
        - product_qty: Quantity received
        - price_unit: Unit cost price
        - source_document: Reference invoice or manifest
        """
        filepath = os.path.join(self.output_dir, filename)
        
        # Standard Odoo field mapping headers
        headers = [
            "product_id/default_code",
            "product_id/name",
            "product_qty",
            "price_unit",
            "uom_id",
            "source_document"
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for item in parsed_items:
                writer.writerow([
                    item.get("sku"),
                    item.get("name"),
                    item.get("qty"),
                    item.get("price", 0.0),
                    "pcs",  # Unit of measure default
                    item.get("source", "UNKNOWN")
                ])
                
        return filepath

    def export_json(self, parsed_items, filename="odoo_import_procurement.json"):
        """
        Generates standard Odoo import JSON representation.
        """
        filepath = os.path.join(self.output_dir, filename)
        
        odoo_records = []
        for item in parsed_items:
            odoo_records.append({
                "product_id/default_code": item.get("sku"),
                "product_id/name": item.get("name"),
                "product_qty": item.get("qty"),
                "price_unit": item.get("price", 0.0),
                "uom_id": "pcs",
                "source_document": item.get("source")
            })
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"odoo_import_data": odoo_records}, f, indent=2)
            
        return filepath
