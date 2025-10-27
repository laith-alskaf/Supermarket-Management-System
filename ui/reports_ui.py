import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ReportsUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة التقارير"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="التقارير والإحصائيات",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار الفلاتر
        filter_frame = ttk.LabelFrame(self.parent, text="خيارات التقرير", padding=15)
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        # نوع التقرير
        ttk.Label(filter_frame, text="نوع التقرير:", font=('Arial', 11)).grid(row=0, column=3, padx=10, pady=10, sticky='e')
        self.report_var = tk.StringVar(value='sales')
        report_combo = ttk.Combobox(filter_frame, textvariable=self.report_var, 
                                     font=('Arial', 11), width=20, state='readonly')
        report_combo['values'] = ['المبيعات', 'المشتريات', 'المصروفات', 'الأرباح', 'أفضل المنتجات', 'الموردين']
        report_combo.grid(row=0, column=2, padx=10, pady=10)
        
        # الفترة
        ttk.Label(filter_frame, text="الفترة:", font=('Arial', 11)).grid(row=0, column=1, padx=10, pady=10, sticky='e')
        self.period_var = tk.StringVar(value='month')
        period_combo = ttk.Combobox(filter_frame, textvariable=self.period_var, 
                                     font=('Arial', 11), width=15, state='readonly')
        period_combo['values'] = ['اليوم', 'الأسبوع', 'الشهر', 'السنة', 'مخصص']
        period_combo.grid(row=0, column=0, padx=10, pady=10)
        period_combo.bind('<<ComboboxSelected>>', self.toggle_date_entries)
        
        # التواريخ المخصصة
        date_frame = ttk.Frame(filter_frame)
        date_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Label(date_frame, text="من:", font=('Arial', 11)).pack(side='right', padx=10)
        self.from_date_entry = ttk.Entry(date_frame, font=('Arial', 11), width=15, state='disabled')
        self.from_date_entry.pack(side='right', padx=10)
        
        ttk.Label(date_frame, text="إلى:", font=('Arial', 11)).pack(side='right', padx=10)
        self.to_date_entry = ttk.Entry(date_frame, font=('Arial', 11), width=15, state='disabled')
        self.to_date_entry.pack(side='right', padx=10)
        
        # زر إنشاء التقرير
        ttk.Button(
            filter_frame,
            text="إنشاء التقرير",
            command=self.generate_report,
            style='primary.TButton'
        ).grid(row=2, column=0, columnspan=4, pady=15)
        
        # إطار عرض التقرير
        self.report_frame = ttk.Frame(self.parent)
        self.report_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
    def toggle_date_entries(self, event=None):
        """تفعيل/تعطيل حقول التاريخ"""
        if self.period_var.get() == 'مخصص':
            self.from_date_entry.config(state='normal')
            self.to_date_entry.config(state='normal')
            self.from_date_entry.delete(0, 'end')
            self.from_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            self.to_date_entry.delete(0, 'end')
            self.to_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        else:
            self.from_date_entry.config(state='disabled')
            self.to_date_entry.config(state='disabled')
    
    def get_date_range(self):
        """الحصول على نطاق التاريخ"""
        period = self.period_var.get()
        today = datetime.now()
        
        if period == 'اليوم':
            from_date = today.strftime('%Y-%m-%d')
            to_date = today.strftime('%Y-%m-%d')
        elif period == 'الأسبوع':
            from_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
            to_date = today.strftime('%Y-%m-%d')
        elif period == 'الشهر':
            from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            to_date = today.strftime('%Y-%m-%d')
        elif period == 'السنة':
            from_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')
            to_date = today.strftime('%Y-%m-%d')
        else:  # مخصص
            from_date = self.from_date_entry.get()
            to_date = self.to_date_entry.get()
        
        return from_date, to_date
    
    def generate_report(self):
        """إنشاء التقرير"""
        # مسح الإطار
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        report_type = self.report_var.get()
        from_date, to_date = self.get_date_range()
        
        if report_type == 'المبيعات':
            self.show_sales_report(from_date, to_date)
        elif report_type == 'المشتريات':
            self.show_purchases_report(from_date, to_date)
        elif report_type == 'المصروفات':
            self.show_expenses_report(from_date, to_date)
        elif report_type == 'الأرباح':
            self.show_profit_report(from_date, to_date)
        elif report_type == 'أفضل المنتجات':
            self.show_top_products_report(from_date, to_date)
        elif report_type == 'الموردين':
            self.show_suppliers_report()
    
    def show_sales_report(self, from_date, to_date):
        """تقرير المبيعات"""
        # العنوان
        ttk.Label(self.report_frame, text=f"تقرير المبيعات من {from_date} إلى {to_date}", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # الإحصائيات
        stats = self.db.fetch_one("""
            SELECT COUNT(*), SUM(total_syp), SUM(total_usd), SUM(discount_syp), SUM(discount_usd)
            FROM sales
            WHERE DATE(sale_date) BETWEEN ? AND ?
        """, (from_date, to_date))
        
        if stats and stats[0]:
            count, total_syp, total_usd, discount_syp, discount_usd = stats
            total_syp = total_syp or 0
            total_usd = total_usd or 0
            discount_syp = discount_syp or 0
            discount_usd = discount_usd or 0
            
            stats_frame = ttk.Frame(self.report_frame)
            stats_frame.pack(fill='x', pady=10)
            
            self.create_stat_box(stats_frame, "عدد المبيعات", str(count), 0)
            self.create_stat_box(stats_frame, "الإجمالي (ل.س)", f"{total_syp:,.2f}", 1)
            self.create_stat_box(stats_frame, "الإجمالي ($)", f"{total_usd:,.2f}", 2)
            self.create_stat_box(stats_frame, "الخصومات (ل.س)", f"{discount_syp:,.2f}", 3)
            
            # جدول المبيعات
            table_frame = ttk.LabelFrame(self.report_frame, text="تفاصيل المبيعات", padding=10)
            table_frame.pack(fill='both', expand=True, pady=10)
            
            columns = ('id', 'total_syp', 'total_usd', 'payment', 'date')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
            
            tree.heading('id', text='رقم')
            tree.heading('total_syp', text='المبلغ (ل.س)')
            tree.heading('total_usd', text='المبلغ ($)')
            tree.heading('payment', text='طريقة الدفع')
            tree.heading('date', text='التاريخ')
            
            tree.pack(fill='both', expand=True)
            
            sales = self.db.fetch_all("""
                SELECT id, total_syp, total_usd, payment_method, sale_date
                FROM sales
                WHERE DATE(sale_date) BETWEEN ? AND ?
                ORDER BY id DESC
            """, (from_date, to_date))
            
            for sale in sales:
                tree.insert('', 'end', values=sale)
        else:
            ttk.Label(self.report_frame, text="لا توجد مبيعات في هذه الفترة", 
                     font=('Arial', 12)).pack(pady=50)
    
    def show_purchases_report(self, from_date, to_date):
        """تقرير المشتريات"""
        ttk.Label(self.report_frame, text=f"تقرير المشتريات من {from_date} إلى {to_date}", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        stats = self.db.fetch_one("""
            SELECT COUNT(*), SUM(total_syp), SUM(total_usd)
            FROM purchases
            WHERE DATE(purchase_date) BETWEEN ? AND ?
        """, (from_date, to_date))
        
        if stats and stats[0]:
            count, total_syp, total_usd = stats
            total_syp = total_syp or 0
            total_usd = total_usd or 0
            
            stats_frame = ttk.Frame(self.report_frame)
            stats_frame.pack(fill='x', pady=10)
            
            self.create_stat_box(stats_frame, "عدد المشتريات", str(count), 0)
            self.create_stat_box(stats_frame, "الإجمالي (ل.س)", f"{total_syp:,.2f}", 1)
            self.create_stat_box(stats_frame, "الإجمالي ($)", f"{total_usd:,.2f}", 2)
            
            # جدول المشتريات
            table_frame = ttk.LabelFrame(self.report_frame, text="تفاصيل المشتريات", padding=10)
            table_frame.pack(fill='both', expand=True, pady=10)
            
            columns = ('id', 'supplier', 'total_syp', 'total_usd', 'date')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
            
            tree.heading('id', text='رقم')
            tree.heading('supplier', text='المورد')
            tree.heading('total_syp', text='المبلغ (ل.س)')
            tree.heading('total_usd', text='المبلغ ($)')
            tree.heading('date', text='التاريخ')
            
            tree.pack(fill='both', expand=True)
            
            purchases = self.db.fetch_all("""
                SELECT p.id, COALESCE(s.name, 'غير محدد'), p.total_syp, p.total_usd, p.purchase_date
                FROM purchases p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE DATE(p.purchase_date) BETWEEN ? AND ?
                ORDER BY p.id DESC
            """, (from_date, to_date))
            
            for purchase in purchases:
                tree.insert('', 'end', values=purchase)
        else:
            ttk.Label(self.report_frame, text="لا توجد مشتريات في هذه الفترة", 
                     font=('Arial', 12)).pack(pady=50)
    
    def show_expenses_report(self, from_date, to_date):
        """تقرير المصروفات"""
        ttk.Label(self.report_frame, text=f"تقرير المصروفات من {from_date} إلى {to_date}", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        stats = self.db.fetch_one("""
            SELECT COUNT(*), SUM(amount_syp), SUM(amount_usd)
            FROM expenses
            WHERE DATE(expense_date) BETWEEN ? AND ?
        """, (from_date, to_date))
        
        if stats and stats[0]:
            count, total_syp, total_usd = stats
            total_syp = total_syp or 0
            total_usd = total_usd or 0
            
            stats_frame = ttk.Frame(self.report_frame)
            stats_frame.pack(fill='x', pady=10)
            
            self.create_stat_box(stats_frame, "عدد المصروفات", str(count), 0)
            self.create_stat_box(stats_frame, "الإجمالي (ل.س)", f"{total_syp:,.2f}", 1)
            self.create_stat_box(stats_frame, "الإجمالي ($)", f"{total_usd:,.2f}", 2)
            
            # جدول حسب الفئات
            table_frame = ttk.LabelFrame(self.report_frame, text="المصروفات حسب الفئة", padding=10)
            table_frame.pack(fill='both', expand=True, pady=10)
            
            columns = ('category', 'count', 'total_syp', 'total_usd')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
            
            tree.heading('category', text='الفئة')
            tree.heading('count', text='العدد')
            tree.heading('total_syp', text='المجموع (ل.س)')
            tree.heading('total_usd', text='المجموع ($)')
            
            tree.pack(fill='both', expand=True)
            
            expenses = self.db.fetch_all("""
                SELECT category, COUNT(*), SUM(amount_syp), SUM(amount_usd)
                FROM expenses
                WHERE DATE(expense_date) BETWEEN ? AND ?
                GROUP BY category
                ORDER BY SUM(amount_syp) DESC
            """, (from_date, to_date))
            
            for expense in expenses:
                tree.insert('', 'end', values=expense)
        else:
            ttk.Label(self.report_frame, text="لا توجد مصروفات في هذه الفترة", 
                     font=('Arial', 12)).pack(pady=50)
    
    def show_profit_report(self, from_date, to_date):
        """تقرير الأرباح"""
        ttk.Label(self.report_frame, text=f"تقرير الأرباح والخسائر من {from_date} إلى {to_date}", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # الإيرادات (المبيعات)
        sales_stats = self.db.fetch_one("""
            SELECT SUM(total_syp), SUM(total_usd)
            FROM sales
            WHERE DATE(sale_date) BETWEEN ? AND ?
        """, (from_date, to_date))
        
        sales_syp = sales_stats[0] if sales_stats and sales_stats[0] else 0
        sales_usd = sales_stats[1] if sales_stats and sales_stats[1] else 0
        
        # تكلفة البضاعة المباعة
        cogs_stats = self.db.fetch_one("""
            SELECT SUM(si.quantity * p.purchase_price_syp), 
                   SUM(si.quantity * p.purchase_price_usd)
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
        """, (from_date, to_date))
        
        cogs_syp = cogs_stats[0] if cogs_stats and cogs_stats[0] else 0
        cogs_usd = cogs_stats[1] if cogs_stats and cogs_stats[1] else 0
        
        # المصروفات
        expenses_stats = self.db.fetch_one("""
            SELECT SUM(amount_syp), SUM(amount_usd)
            FROM expenses
            WHERE DATE(expense_date) BETWEEN ? AND ?
        """, (from_date, to_date))
        
        expenses_syp = expenses_stats[0] if expenses_stats and expenses_stats[0] else 0
        expenses_usd = expenses_stats[1] if expenses_stats and expenses_stats[1] else 0
        
        # حساب الأرباح
        gross_profit_syp = sales_syp - cogs_syp
        gross_profit_usd = sales_usd - cogs_usd
        
        net_profit_syp = gross_profit_syp - expenses_syp
        net_profit_usd = gross_profit_usd - expenses_usd
        
        # عرض النتائج
        results_frame = ttk.LabelFrame(self.report_frame, text="ملخص الأرباح", padding=20)
        results_frame.pack(fill='both', expand=True, pady=20, padx=20)
        
        # الليرة السورية
        syp_frame = ttk.LabelFrame(results_frame, text="بالليرة السورية", padding=15)
        syp_frame.pack(side='right', fill='both', expand=True, padx=10)
        
        ttk.Label(syp_frame, text=f"الإيرادات: {sales_syp:,.2f}", 
                 font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(syp_frame, text=f"تكلفة البضاعة: {cogs_syp:,.2f}", 
                 font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(syp_frame, text=f"الربح الإجمالي: {gross_profit_syp:,.2f}", 
                 font=('Arial', 12, 'bold'), foreground='blue').pack(anchor='e', pady=5)
        ttk.Label(syp_frame, text=f"المصروفات: {expenses_syp:,.2f}", 
                 font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(syp_frame, text=f"الربح الصافي: {net_profit_syp:,.2f}", 
                 font=('Arial', 14, 'bold'), 
                 foreground='green' if net_profit_syp >= 0 else 'red').pack(anchor='e', pady=10)
        
        # الدولار
        usd_frame = ttk.LabelFrame(results_frame, text="بالدولار", padding=15)
        usd_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        ttk.Label(usd_frame, text=f"الإيرادات: {sales_usd:,.2f}", 
                 font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(usd_frame, text=f"تكلفة البضاعة: {cogs_usd:,.2f}", 
                 font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(usd_frame, text=f"الربح الإجمالي: {gross_profit_usd:,.2f}", 
                 font=('Arial', 12, 'bold'), foreground='blue').pack(anchor='e', pady=5)
        ttk.Label(usd_frame, text=f"المصروفات: {expenses_usd:,.2f}", 
                 font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(usd_frame, text=f"الربح الصافي: {gross_profit_usd:,.2f}", 
                 font=('Arial', 14, 'bold'), 
                 foreground='green' if net_profit_usd >= 0 else 'red').pack(anchor='e', pady=10)
    
    def show_top_products_report(self, from_date, to_date):
        """تقرير أفضل المنتجات مبيعاً"""
        ttk.Label(self.report_frame, text=f"أفضل المنتجات مبيعاً من {from_date} إلى {to_date}", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        table_frame = ttk.LabelFrame(self.report_frame, text="المنتجات", padding=10)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ('product', 'quantity', 'total_syp', 'total_usd')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        tree.heading('product', text='المنتج')
        tree.heading('quantity', text='الكمية المباعة')
        tree.heading('total_syp', text='المبيعات (ل.س)')
        tree.heading('total_usd', text='المبيعات ($)')
        
        tree.pack(fill='both', expand=True)
        
        products = self.db.fetch_all("""
            SELECT si.product_name, SUM(si.quantity), SUM(si.subtotal_syp), SUM(si.subtotal_usd)
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            GROUP BY si.product_name
            ORDER BY SUM(si.quantity) DESC
            LIMIT 50
        """, (from_date, to_date))
        
        for product in products:
            tree.insert('', 'end', values=product)
    
    def show_suppliers_report(self):
        """تقرير الموردين والديون"""
        ttk.Label(self.report_frame, text="تقرير الموردين والديون", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        table_frame = ttk.LabelFrame(self.report_frame, text="الموردين", padding=10)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ('name', 'purchases', 'debt_syp', 'debt_usd', 'phone')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        tree.heading('name', text='اسم المورد')
        tree.heading('purchases', text='عدد المشتريات')
        tree.heading('debt_syp', text='الديون (ل.س)')
        tree.heading('debt_usd', text='الديون ($)')
        tree.heading('phone', text='الهاتف')
        
        tree.pack(fill='both', expand=True)
        
        suppliers = self.db.fetch_all("""
            SELECT s.name, COUNT(p.id), s.debt_syp, s.debt_usd, s.phone
            FROM suppliers s
            LEFT JOIN purchases p ON s.id = p.supplier_id
            GROUP BY s.id
            ORDER BY s.debt_syp DESC
        """)
        
        for supplier in suppliers:
            tree.insert('', 'end', values=supplier)
    
    def create_stat_box(self, parent, title, value, column):
        """إنشاء صندوق إحصائيات"""
        box = ttk.Frame(parent, relief='raised', borderwidth=2)
        box.grid(row=0, column=column, padx=10, pady=10, sticky='ew')
        parent.columnconfigure(column, weight=1)
        
        ttk.Label(box, text=title, font=('Arial', 11)).pack(pady=(10, 5))
        ttk.Label(box, text=value, font=('Arial', 16, 'bold')).pack(pady=(5, 10))
