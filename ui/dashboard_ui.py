import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class DashboardUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة لوحة التحكم"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="لوحة التحكم",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار الإحصائيات السريعة
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # الحصول على البيانات
        today = datetime.now().strftime('%Y-%m-%d')
        
        # مبيعات اليوم
        sales_today = self.db.fetch_one(
            "SELECT SUM(total_syp) FROM sales WHERE DATE(sale_date) = ?",
            (today,)
        )
        sales_today = sales_today[0] if sales_today[0] else 0
        
        # عدد المنتجات
        products_count = self.db.fetch_one("SELECT COUNT(*) FROM products")
        products_count = products_count[0] if products_count else 0
        
        # المنتجات القريبة من النفاد
        low_stock = self.db.fetch_one(
            "SELECT COUNT(*) FROM products WHERE quantity <= min_quantity"
        )
        low_stock = low_stock[0] if low_stock else 0
        
        # عدد الموردين
        suppliers_count = self.db.fetch_one("SELECT COUNT(*) FROM suppliers")
        suppliers_count = suppliers_count[0] if suppliers_count else 0
        
        # عرض البطاقات
        self.create_stat_card(stats_frame, "مبيعات اليوم", f"{sales_today:,.0f} ل.س", "success", 0)
        self.create_stat_card(stats_frame, "عدد المنتجات", str(products_count), "info", 1)
        self.create_stat_card(stats_frame, "منتجات قريبة من النفاد", str(low_stock), "warning", 2)
        self.create_stat_card(stats_frame, "عدد الموردين", str(suppliers_count), "primary", 3)
        
        # إطار الرسوم البيانية
        charts_frame = ttk.Frame(self.parent)
        charts_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # رسم بياني للمبيعات الأسبوعية
        self.create_weekly_sales_chart(charts_frame)
        
    def create_stat_card(self, parent, title, value, color, column):
        """إنشاء بطاقة إحصائيات"""
        card = ttk.Frame(parent, style=f'{color}.TFrame', relief='raised', borderwidth=2)
        card.grid(row=0, column=column, padx=10, pady=10, sticky='ew')
        parent.columnconfigure(column, weight=1)
        
        # العنوان
        title_label = ttk.Label(
            card,
            text=title,
            font=('Arial', 12),
            style=f'{color}.TLabel'
        )
        title_label.pack(pady=(15, 5))
        
        # القيمة
        value_label = ttk.Label(
            card,
            text=value,
            font=('Arial', 24, 'bold'),
            style=f'{color}.TLabel'
        )
        value_label.pack(pady=(5, 15))
    
    def create_weekly_sales_chart(self, parent):
        """إنشاء رسم بياني للمبيعات الأسبوعية"""
        # الحصول على بيانات آخر 7 أيام
        dates = []
        sales = []
        
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)
            
            result = self.db.fetch_one(
                "SELECT SUM(total_syp) FROM sales WHERE DATE(sale_date) = ?",
                (date,)
            )
            sales.append(result[0] if result[0] else 0)
        
        # إنشاء الرسم البياني
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.bar(range(len(dates)), sales, color='#3498db', alpha=0.7)
        ax.set_xlabel('التاريخ', fontsize=10)
        ax.set_ylabel('المبيعات (ل.س)', fontsize=10)
        ax.set_title('المبيعات الأسبوعية', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels([d.split('-')[2] + '/' + d.split('-')[1] for d in dates], rotation=0)
        ax.grid(True, alpha=0.3)
        
        # إضافة الرسم إلى الواجهة
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
