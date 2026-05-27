import os
import sys

# Add current folder to path to make src imports reliable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser import ProcurementParser
from src.stock_manager import StockManager
from src.odoo_exporter import OdooExporter
from src.dashboard_generator import DashboardGenerator

def print_rich_summary(stock_results, low_alerts):
    """
    Tries to print a beautiful console layout of stock updates using the rich library.
    Falls back to normal printing if rich is not installed.
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        console.clear()
        
        # Display Header
        console.print(Panel(
            "[bold cyan]ODOO PROCUREMENT AUTOMATOR[/bold cyan]\n"
            "[italic gray54]\"I don't enter supply chain data manually, I secure data quality with code.\"[/italic gray54]",
            title="[bold white]Hardware Supply Chain Pipeline[/bold white]",
            subtitle="[bold green]Active[/bold green]",
            expand=False
        ))
        
        # Display Stock Table
        table = Table(title="Inventory Audit (Stock Adjustment)", title_style="bold magenta")
        table.add_column("SKU", style="cyan", no_wrap=True)
        table.add_column("Item Name", style="white")
        table.add_column("Received Qty", justify="right", style="green")
        table.add_column("Initial Stock", justify="right", style="dim")
        table.add_column("New Stock", justify="right", style="bold")
        table.add_column("Min Safety Limit", justify="right", style="yellow")
        table.add_column("Alert Status", justify="center")
        
        for sku, info in stock_results.items():
            status = info["status"]
            if status == "CRITICAL":
                status_formatted = "[bold red]CRITICAL[/bold red]"
            elif status == "WARNING":
                status_formatted = "[bold yellow]WARNING[/bold yellow]"
            elif status == "RESTOCKED":
                status_formatted = "[bold green]RESTOCKED[/bold green]"
            else:
                status_formatted = "[cyan]OK[/cyan]"
                
            table.add_row(
                sku,
                info["name"],
                f"+{info['received_qty']}",
                str(info["initial_stock"]),
                str(info["new_stock"]),
                str(info["safety_stock"]),
                status_formatted
            )
            
        console.print(table)
        
        # Display warning panel if any low stock alerts exist
        if low_alerts:
            console.print("\n[bold red][!] LOW STOCK ALERTS DETECTED:[/bold red]")
            for sku, info in low_alerts.items():
                console.print(f"  - [bold yellow]{sku}[/bold yellow] ({info['name']}): [bold red]{info['new_stock']}[/bold red] {info['unit']} in stock (Safety Limit: {info['safety_stock']})")
        else:
            console.print("\n[bold green][OK] All stock levels secure. No safety violations detected.[/bold green]")
            
        console.print("\n[bold green][SUCCESS][/bold green] Ingested and generated all outputs:")
        console.print("  [white]1. Odoo CSV Import:[/white] [cyan]output/odoo_import_procurement.csv[/cyan]")
        console.print("  [white]2. Odoo JSON Import:[/white] [cyan]output/odoo_import_procurement.json[/cyan]")
        console.print("  [white]3. HTML Visual Dashboard:[/white] [cyan]output/procurement_dashboard.html[/cyan]")
        console.print("  [white]4. Static Status Plot Image:[/white] [cyan]output/stock_status_plot.png[/cyan]\n")
        
    except ImportError:
        # Fallback to standard command-line print
        print("="*60)
        print(" ODOO PROCUREMENT AUTOMATOR - STATUS SUMMARY ")
        print("="*60)
        print("SKU          | Name                      | Received | New Stock | Min Safety | Status")
        print("-"*85)
        for sku, info in stock_results.items():
            print(f"{sku:<12} | {info['name'][:25]:<25} | +{info['received_qty']:<8} | {info['new_stock']:<9} | {info['safety_stock']:<10} | {info['status']}")
        print("="*60)
        
        if low_alerts:
            print("[!] LOW STOCK ALERTS:")
            for sku, info in low_alerts.items():
                print(f"  * {sku} ({info['name']}): {info['new_stock']} pcs (Min Safety: {info['safety_stock']})")
        else:
            print("[OK] All stock levels are normal.")
            
        print("\nAll export outputs generated in output/ folder successfully.")

def main():
    # Setup directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    invoices_dir = os.path.join(data_dir, "raw_invoices")
    output_dir = os.path.join(base_dir, "output")
    stock_db_path = os.path.join(data_dir, "odoo_stock.json")
    
    # 1. Initialize Parser, StockManager, Exporter, and DashboardGenerator
    parser = ProcurementParser()
    stock_manager = StockManager(stock_db_path)
    exporter = OdooExporter(output_dir)
    dashboard_gen = DashboardGenerator(output_dir)
    
    # 2. Scan and parse all raw invoice files
    print(f"Scanning for invoice files in {invoices_dir}...")
    if not os.path.exists(invoices_dir):
        print(f"[Error] Directory not found: {invoices_dir}")
        return
        
    raw_files = [os.path.join(invoices_dir, f) for f in os.listdir(invoices_dir) if os.path.isfile(os.path.join(invoices_dir, f))]
    
    all_parsed_items = []
    for filepath in raw_files:
        print(f"Parsing raw procurement input: {os.path.basename(filepath)}...")
        items = parser.parse_file(filepath)
        all_parsed_items.extend(items)
        
    if not all_parsed_items:
        print("[Warning] No raw procurement items were parsed. Check invoice files format.")
        return
        
    print(f"Successfully extracted {len(all_parsed_items)} line items from raw inputs.")
    
    # 3. Update stock registry database and verify levels
    stock_results = stock_manager.process_shipment(all_parsed_items)
    
    # Identify safety violations
    low_alerts = {sku: info for sku, info in stock_results.items() if info["status"] in ["CRITICAL", "WARNING"]}
    
    # 4. Export clean Odoo Import formatted files
    exporter.export_csv(all_parsed_items)
    exporter.export_json(all_parsed_items)
    
    # 5. Generate interactive HTML Dashboard and static Matplotlib plot image
    dashboard_gen.generate_html_dashboard(stock_results, all_parsed_items)
    dashboard_gen.generate_static_plot(stock_results)
    
    # 6. Output log report to console
    print_rich_summary(stock_results, low_alerts)

if __name__ == "__main__":
    main()
