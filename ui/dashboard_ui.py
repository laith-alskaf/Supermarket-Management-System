import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from utils.arabic_helper import prepare_arabic_text
import matplotlib.font_manager as fm
import pytz

class DashboardUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        # توقيت سوريا (GMT+3)
        self.syria_tz = pytz.timezone('Asia/Damascus')
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة لوحة التحكم"""
        # إنشاء Canvas و Scrollbar للسكرول
        main_canvas = tk.Canvas(self.parent)
        scrollbar = ttk.Scrollbar(self.parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # تفعيل السكرول بالماوس
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # العنوان
        title = ttk.Label(
            scrollable_frame,
            text="لوحة التحكم",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار الإحصائيات السريعة
        stats_frame = ttk.Frame(scrollable_frame)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        # الحصول على البيانات
        syria_time = datetime.now(self.syria_tz)
        today = syria_time.strftime('%Y-%m-%d')
        
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
        charts_frame = ttk.Frame(scrollable_frame)
        charts_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # رسم بياني للمبيعات الأسبوعية
        self.create_weekly_sales_chart(charts_frame)
        
        # عرض Canvas و Scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
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
        
        syria_time = datetime.now(self.syria_tz)
        for i in range(6, -1, -1):
            date = (syria_time - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)
            
            result = self.db.fetch_one(
                "SELECT SUM(total_syp) FROM sales WHERE DATE(sale_date) = ?",
                (date,)
            )
            sales.append(result[0] if result[0] else 0)
        
        # إنشاء الرسم البياني مع دعم العربية
        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # إعداد النصوص العربية
        xlabel_text = prepare_arabic_text('التاريخ')
        ylabel_text = prepare_arabic_text('المبيعات (ل.س)')
        title_text = prepare_arabic_text('المبيعات الأسبوعية')
        
        ax.bar(range(len(dates)), sales, color='#3498db', alpha=0.7, width=0.6)
        ax.set_xlabel(xlabel_text, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel_text, fontsize=12, fontweight='bold')
        ax.set_title(title_text, fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(range(len(dates)))
        
        # تنسيق التواريخ بشكل أفضل
        date_labels = [d.split('-')[2] + '/' + d.split('-')[1] for d in dates]
        ax.set_xticklabels(date_labels, rotation=0, fontsize=10)
        
        # إضافة شبكة للوضوح
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # تحسين المظهر
        fig.tight_layout()
        
        # إضافة الرسم إلى الواجهة
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)
