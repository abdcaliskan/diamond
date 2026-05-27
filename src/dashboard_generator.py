import os
import json

class DashboardGenerator:
    """
    Generates a premium dark-themed interactive HTML dashboard (procurement_dashboard.html)
    and a static stock comparison plot (stock_status_plot.png) using Matplotlib.
    """
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_html_dashboard(self, stock_results, parsed_items, html_filename="procurement_dashboard.html"):
        """
        Compiles a modern HTML/CSS/JS dashboard file showing live stock analytics,
        interactive Chart.js plots, and download options.
        """
        filepath = os.path.join(self.output_dir, html_filename)
        
        # Prepare data for Chart.js
        labels = []
        current_stocks = []
        safety_stocks = []
        bar_colors = []
        
        low_stock_alerts = []
        
        for sku, info in stock_results.items():
            labels.append(sku)
            current_stocks.append(info["new_stock"])
            safety_stocks.append(info["safety_stock"])
            
            # Color code based on status
            if info["status"] == "CRITICAL":
                bar_colors.append("rgba(239, 68, 68, 0.8)") # Red
                low_stock_alerts.append(info)
            elif info["status"] == "WARNING":
                bar_colors.append("rgba(245, 158, 11, 0.8)") # Amber
                low_stock_alerts.append(info)
            elif info["status"] == "RESTOCKED":
                bar_colors.append("rgba(16, 185, 129, 0.8)") # Emerald (restocked)
            else:
                bar_colors.append("rgba(6, 182, 212, 0.8)") # Cyan (OK)

        # HTML Template
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Odoo Procurement Automator | Dashboard</title>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(17, 24, 39, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
        }}
        
        body {{
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.08) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(239, 68, 68, 0.05) 0%, transparent 40%);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 1rem;
        }}
        
        .header-title h1 {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(to right, #06b6d4, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .header-title p {{
            color: var(--text-muted);
            margin-top: 0.25rem;
            font-size: 0.95rem;
        }}
        
        .punchline-badge {{
            background: rgba(6, 182, 212, 0.15);
            border: 1px solid var(--primary);
            color: var(--primary);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        @media (min-width: 1024px) {{
            .grid {{
                grid-template-columns: 2fr 1fr;
            }}
        }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        
        .card-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        /* Alert Widgets */
        .alerts-container {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .alert-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem;
            border-radius: 12px;
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #fca5a5;
        }}
        
        .alert-item.warning {{
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.2);
            color: #fcd34d;
        }}
        
        .alert-details {{
            display: flex;
            flex-direction: column;
        }}
        
        .alert-sku {{
            font-weight: 700;
            font-size: 1.05rem;
        }}
        
        .alert-name {{
            font-size: 0.85rem;
            opacity: 0.8;
        }}
        
        .alert-numbers {{
            text-align: right;
        }}
        
        .alert-qty {{
            font-weight: bold;
            font-size: 1.1rem;
        }}
        
        .alert-limit {{
            font-size: 0.75rem;
            opacity: 0.7;
        }}
        
        /* Table styles */
        .table-wrapper {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }}
        
        th {{
            color: var(--text-muted);
            font-weight: 600;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--card-border);
        }}
        
        td {{
            padding: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }}
        
        tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge-critical {{ background: rgba(239, 68, 68, 0.15); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.3); }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.15); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.3); }}
        .badge-restocked {{ background: rgba(16, 185, 129, 0.15); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-ok {{ background: rgba(6, 182, 212, 0.15); color: var(--primary); border: 1px solid rgba(6, 182, 212, 0.3); }}
        
        /* Download links */
        .actions {{
            display: flex;
            gap: 1rem;
        }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
            border: none;
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.9rem;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
        }}
        
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            box-shadow: none;
        }}
        
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.1);
            box-shadow: none;
        }}
        
        .footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 3rem;
            border-top: 1px solid var(--card-border);
            padding-top: 1.5rem;
        }}
    </style>
</head>
<body>

    <header>
        <div class="header-title">
            <h1>Odoo Procurement Automator</h1>
            <p>Data validation and ingestion pipeline for Odoo ERP systems</p>
        </div>
        <div class="punchline-badge">
            "I don't enter supply chain data manually, I secure data quality with code."
        </div>
    </header>

    <div class="grid">
        <!-- Stock Chart Card -->
        <div class="card">
            <div class="card-title">
                <span>Inventory Audit Plot</span>
                <div class="actions">
                    <a href="odoo_import_procurement.csv" class="btn" download>Download Odoo CSV</a>
                    <a href="odoo_import_procurement.json" class="btn btn-secondary" download>Download Odoo JSON</a>
                </div>
            </div>
            <div style="position: relative; height: 350px; width: 100%;">
                <canvas id="stockChart"></canvas>
            </div>
        </div>

        <!-- Low Stock Alerts Card -->
        <div class="card">
            <div class="card-title">
                <span>Low Stock Alerts</span>
                <span class="badge badge-critical">{len(low_stock_alerts)} warnings</span>
            </div>
            <div class="alerts-container">
                {"" if low_stock_alerts else '<div style="color: var(--success); text-align: center; padding: 2rem;">No low stock alerts detected. All items fully restocked!</div>'}
                {"".join([f'''
                <div class="alert-item {"warning" if item["status"] == "WARNING" else ""}">
                    <div class="alert-details">
                        <span class="alert-sku">{item["name"]}</span>
                        <span class="alert-name">SKU: {sku} | {item["category"]}</span>
                    </div>
                    <div class="alert-numbers">
                        <span class="alert-qty">{item["new_stock"]} {item["unit"]}</span>
                        <div class="alert-limit">Min safety: {item["safety_stock"]}</div>
                    </div>
                </div>
                ''' for sku, item in stock_results.items() if item["status"] in ["CRITICAL", "WARNING"]])}
            </div>
        </div>
    </div>

    <div class="grid" style="grid-template-columns: 1fr;">
        <!-- Processed Shipment Items Table -->
        <div class="card">
            <div class="card-title">Processed Procurement Log</div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>SKU</th>
                            <th>Description</th>
                            <th>Qty Received</th>
                            <th>Initial Stock</th>
                            <th>New Stock</th>
                            <th>Min Safety</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f'''
                        <tr>
                            <td style="font-weight: 600; color: var(--primary);">{sku}</td>
                            <td>{info["name"]}</td>
                            <td style="font-weight: 600;">+{info["received_qty"]}</td>
                            <td style="color: var(--text-muted);">{info["initial_stock"]}</td>
                            <td style="font-weight: 600; color: {"var(--danger)" if info["status"] == "CRITICAL" else "var(--warning)" if info["status"] == "WARNING" else "var(--success)" if info["status"] == "RESTOCKED" else "var(--text-main)"}">{info["new_stock"]}</td>
                            <td>{info["safety_stock"]}</td>
                            <td>
                                <span class="badge badge-{info["status"].lower()}">{info["status"]}</span>
                            </td>
                        </tr>
                        ''' for sku, info in stock_results.items()])}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="card" style="margin-top: 1.5rem;">
        <div class="card-title">Parsed Raw Files Summary</div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>SKU</th>
                        <th>Product Description</th>
                        <th>Extracted Qty</th>
                        <th>Extracted Price</th>
                        <th>Source File Reference</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td style="font-weight: 600;">{item["sku"]}</td>
                        <td>{item["name"]}</td>
                        <td>{item["qty"]}</td>
                        <td>${item["price"]:.2f}</td>
                        <td style="color: var(--primary); font-family: monospace;">{item["source"]}</td>
                    </tr>
                    ''' for item in parsed_items])}
                </tbody>
            </table>
        </div>
    </div>

    <div class="footer">
        Odoo Procurement Automator &copy; 2026. Hardware Supply Chain Pipeline.
    </div>

    <!-- Chart Configuration Script -->
    <script>
        const ctx = document.getElementById('stockChart').getContext('2d');
        const labels = {json.dumps(labels)};
        
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: labels,
                datasets: [
                    {{
                        label: 'Current Stock Level',
                        data: {json.dumps(current_stocks)},
                        backgroundColor: {json.dumps(bar_colors)},
                        borderRadius: 6,
                        borderWidth: 0
                    }},
                    {{
                        label: 'Min Safety Threshold',
                        data: {json.dumps(safety_stocks)},
                        type: 'line',
                        borderColor: '#9ca3af',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 4,
                        pointBackgroundColor: '#9ca3af'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#e5e7eb',
                            font: {{
                                family: "'Outfit', sans-serif"
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        grid: {{
                            color: 'rgba(255, 255, 255, 0.05)'
                        }},
                        ticks: {{
                            color: '#9ca3af',
                            font: {{
                                family: "'Outfit', sans-serif"
                            }}
                        }}
                    }},
                    x: {{
                        grid: {{
                            display: false
                        }},
                        ticks: {{
                            color: '#9ca3af',
                            font: {{
                                family: "'Outfit', sans-serif"
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filepath

    def generate_static_plot(self, stock_results, plot_filename="stock_status_plot.png"):
        """
        Generates a premium static chart comparing current stock levels vs safety limits
        using Matplotlib. Saves the resulting file in the output folder.
        """
        filepath = os.path.join(self.output_dir, plot_filename)
        
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("[Warning] matplotlib is not installed. Skipping static plot generation.")
            return None
            
        skus = list(stock_results.keys())
        current_levels = [info["new_stock"] for info in stock_results.values()]
        safety_limits = [info["safety_stock"] for info in stock_results.values()]
        
        # Color palettes matching the HTML dashboard
        colors = []
        for info in stock_results.values():
            if info["status"] == "CRITICAL":
                colors.append("#ef4444")  # Red
            elif info["status"] == "WARNING":
                colors.append("#f59e0b")  # Amber
            elif info["status"] == "RESTOCKED":
                colors.append("#10b981")  # Emerald Green
            else:
                colors.append("#06b6d4")  # Cyan
                
        # Set up dark theme figure
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        fig.patch.set_facecolor('#0b0f19')
        ax.set_facecolor('#111827')
        
        x = np.arange(len(skus))
        width = 0.45
        
        # Draw current stock level bars
        bars = ax.bar(x, current_levels, width, color=colors, edgecolor='none', label='Current Stock Level', zorder=3)
        
        # Draw safety limit lines as steps or markers
        line = ax.step(np.append(x - width/2, x[-1] + width/2), np.append(safety_limits, safety_limits[-1]), 
                       where='post', color='#9ca3af', linestyle='--', linewidth=2, label='Min Safety Limit', zorder=2)
        
        # Add labels, title and grid
        ax.set_title('Quantum Hardware Inventory Audit - Stock Levels vs safety thresholds', 
                     fontsize=14, pad=20, color='#f3f4f6', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(skus, fontsize=10, rotation=15, color='#9ca3af')
        ax.set_ylabel('Quantities (units)', fontsize=11, color='#9ca3af')
        ax.yaxis.grid(True, linestyle=':', alpha=0.3, color='#e5e7eb', zorder=1)
        ax.xaxis.grid(False)
        
        # Style spines
        for spine in ['top', 'right', 'left', 'bottom']:
            ax.spines[spine].set_color('#1f2937')
            
        # Add bar value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, color='#f3f4f6', fontweight='bold')
            
        # Legend with styling
        legend = ax.legend(facecolor='#1f2937', edgecolor='none')
        for text in legend.get_texts():
            text.set_color('#f3f4f6')
            
        plt.tight_layout()
        plt.savefig(filepath, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"[Success] Generated static PNG plot at: {filepath}")
        return filepath
