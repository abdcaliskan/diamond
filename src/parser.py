import os
import re
import csv

class ProcurementParser:
    """
    Parses messy supplier invoices and shipping manifests of various file formats.
    Extracts SKU codes, names, and quantities.
    """
    def __init__(self):
        # Regex to parse text-based invoices: e.g. QD-CHIP-99X  Quantum Diamond Proc  10  $1,250.00
        self.txt_item_regex = re.compile(
            r'(QD-[A-Z0-9\-]+)\s+(.+?)\s+(\d+)\s+\$([\d,]+\.\d{2})'
        )
        
        # Regex to parse HTML-based manifests: e.g. <td>QD-SENS-881</td> ... <td>15</td>
        self.html_row_regex = re.compile(
            r'<tr>\s*<td>\s*(QD-[A-Z0-9\-]+)\s*</td>\s*<td>\s*(.+?)\s*</td>\s*<td>\s*(\d+)\s*</td>\s*<td>\s*(.+?)\s*</td>\s*</tr>',
            re.DOTALL
        )

    def parse_file(self, filepath):
        """
        Determines file type and delegates parsing.
        Returns a list of dictionaries: [{'sku': ..., 'name': ..., 'qty': ..., 'source': ...}]
        """
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.txt':
            return self._parse_txt(filepath, filename)
        elif ext == '.html' or ext == '.htm':
            return self._parse_html(filepath, filename)
        elif ext == '.csv':
            return self._parse_csv(filepath, filename)
        else:
            print(f"[Warning] Unsupported file extension {ext} for file: {filename}. Skipping.")
            return []

    def _parse_txt(self, filepath, filename):
        items = []
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = self.txt_item_regex.findall(content)
        for match in matches:
            sku, name, qty, price = match
            items.append({
                'sku': sku.strip(),
                'name': name.strip(),
                'qty': int(qty),
                'price': float(price.replace(',', '')),
                'source': filename
            })
        return items

    def _parse_html(self, filepath, filename):
        items = []
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = self.html_row_regex.findall(content)
        for match in matches:
            sku, name, qty, unit = match
            items.append({
                'sku': sku.strip(),
                'name': name.strip(),
                'qty': int(qty),
                'price': 0.0,  # Manifests might not have prices
                'source': filename
            })
        return items

    def _parse_csv(self, filepath, filename):
        items = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle varying header formats (case-insensitive and whitespace-trimmed keys)
                normalized_row = {k.strip().lower(): v for k, v in row.items()}
                
                sku = None
                for key in ['sku', 'item code', 'product code', 'id']:
                    if key in normalized_row:
                        sku = normalized_row[key]
                        break
                        
                name = None
                for key in ['product name', 'description', 'name']:
                    if key in normalized_row:
                        name = normalized_row[key]
                        break
                        
                qty = 0
                for key in ['quantity ordered', 'qty', 'quantity', 'amount']:
                    if key in normalized_row:
                        try:
                            qty = int(normalized_row[key])
                        except ValueError:
                            qty = 0
                        break
                        
                price = 0.0
                for key in ['unit cost', 'price', 'unit_price', 'cost']:
                    if key in normalized_row:
                        try:
                            price = float(normalized_row[key])
                        except ValueError:
                            price = 0.0
                        break

                if sku:
                    items.append({
                        'sku': sku.strip(),
                        'name': name.strip() if name else sku,
                        'qty': qty,
                        'price': price,
                        'source': filename
                    })
        return items
