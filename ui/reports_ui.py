import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pytz
import csv
import arabic_reshaper
from bidi.algorithm import get_display

class ReportsUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        # توقيت سوريا (GMT+3)
        self.syria_tz = pytz.timezone('Asia/Damascus')
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
        
        filter_frame.columnconfigure((0, 1, 2, 3), weight=1) # For responsiveness

        # نوع التقرير
        ttk.Label(filter_frame, text="نوع التقرير:", font=('Arial', 11)).grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.report_var = tk.StringVar(value='المبيعات')
        report_combo = ttk.Combobox(filter_frame, textvariable=self.report_var, 
                                     font=('Arial', 11), width=20, state='readonly', justify='right')
        report_combo['values'] = ['المبيعات', 'المشتريات', 'المصروفات', 'الأرباح', 'أفضل المنتجات', 'الموردين']
        report_combo.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        # الفترة
        ttk.Label(filter_frame, text="الفترة:", font=('Arial', 11)).grid(row=0, column=3, padx=10, pady=10, sticky='w')
        self.period_var = tk.StringVar(value='الشهر')
        period_combo = ttk.Combobox(filter_frame, textvariable=self.period_var, 
                                     font=('Arial', 11), width=15, state='readonly', justify='right')
        period_combo['values'] = ['اليوم', 'الأسبوع', 'الشهر', 'السنة', 'مخصص']
        period_combo.grid(row=0, column=2, padx=10, pady=10, sticky='ew')
        period_combo.bind('<<ComboboxSelected>>', self.toggle_date_entries)
        
        # التواريخ المخصصة
        date_frame = ttk.Frame(filter_frame)
        date_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky='e')
        
        ttk.Label(date_frame, text="إلى:", font=('Arial', 11)).pack(side='right', padx=5)
        self.to_date_entry = ttk.Entry(date_frame, font=('Arial', 11), width=15, state='disabled', justify='right')
        self.to_date_entry.pack(side='right', padx=10)

        ttk.Label(date_frame, text="من:", font=('Arial', 11)).pack(side='right', padx=5)
        self.from_date_entry = ttk.Entry(date_frame, font=('Arial', 11), width=15, state='disabled', justify='right')
        self.from_date_entry.pack(side='right', padx=10)
        
        # زر إنشاء التقرير
        # حاوية الأزرار
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=15)

        ttk.Button(
            button_frame,
            text="إنشاء التقرير",
            command=self.generate_report,
            style='primary.TButton'
        ).pack(side='right', padx=5)

        ttk.Button(
            button_frame,
            text="تصدير CSV",
            command=self.export_to_csv
        ).pack(side='left', padx=5)
        
        # إطار عرض التقرير
        self.report_frame = ttk.Frame(self.parent)
        self.report_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
    def toggle_date_entries(self, event=None):
        """تفعيل/تعطيل حقول التاريخ"""
        if self.period_var.get() == 'مخصص':
            self.from_date_entry.config(state='normal')
            self.to_date_entry.config(state='normal')
            self.from_date_entry.delete(0, 'end')
            syria_time = datetime.now(self.syria_tz)
            self.from_date_entry.insert(0, (syria_time - timedelta(days=30)).strftime('%Y-%m-%d'))
            self.to_date_entry.delete(0, 'end')
            self.to_date_entry.insert(0, syria_time.strftime('%Y-%m-%d'))
        else:
            self.from_date_entry.config(state='disabled')
            self.to_date_entry.config(state='disabled')
    
    def get_date_range(self):
        """الحصول على نطاق التاريخ"""
        period = self.period_var.get()
        syria_time = datetime.now(self.syria_tz)
        today = syria_time
        
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
    
    def export_to_csv(self):
        """تصدير بيانات التقرير الحالي إلى ملف CSV"""
        report_type = self.report_var.get()
        from_date, to_date = self.get_date_range()
        
        data = []
        header = []
        
        if report_type == 'المبيعات':
            header = ['ID', 'Total SYP', 'Total USD', 'Payment Method', 'Date']
            data = self.db.fetch_all("SELECT id, total_syp, total_usd, payment_method, sale_date FROM sales WHERE DATE(sale_date) BETWEEN ? AND ? ORDER BY id DESC", (from_date, to_date))
        elif report_type == 'المشتريات':
            header = ['ID', 'Supplier', 'Total SYP', 'Total USD', 'Date']
            data = self.db.fetch_all("SELECT p.id, COALESCE(s.name, 'N/A'), p.total_syp, p.total_usd, p.purchase_date FROM purchases p LEFT JOIN suppliers s ON p.supplier_id = s.id WHERE DATE(p.purchase_date) BETWEEN ? AND ? ORDER BY p.id DESC", (from_date, to_date))
        elif report_type == 'أفضل المنتجات':
            header = ['Product Name', 'Quantity Sold', 'Total Sales (SYP)', 'Total Sales (USD)']
            data = self.db.fetch_all("SELECT si.product_name, SUM(si.quantity), SUM(si.subtotal_syp), SUM(si.subtotal_usd) FROM sale_items si JOIN sales s ON si.sale_id = s.id WHERE DATE(s.sale_date) BETWEEN ? AND ? GROUP BY si.product_name ORDER BY SUM(si.quantity) DESC", (from_date, to_date))
        else:
            messagebox.showinfo("غير مدعوم", "التصدير غير مدعوم لهذا النوع من التقارير.")
            return

        if not data:
            messagebox.showinfo("لا توجد بيانات", "لا توجد بيانات لتصديرها.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                   filetypes=[("CSV files", "*.csv")],
                                                   initialfile=f"{report_type}_{from_date}_to_{to_date}.csv")
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerows(data)
                messagebox.showinfo("نجاح", f"تم تصدير البيانات بنجاح إلى:\n{file_path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء تصدير الملف:\n{e}")
    
    def show_sales_report(self, from_date, to_date):
        """تقرير المبيعات مع تحسينات بصرية"""
        # العنوان
        ttk.Label(self.report_frame, text=f"تقرير المبيعات من {from_date} إلى {to_date}", 
                  font=('Arial', 16, 'bold')).pack(pady=10)

        # جلب البيانات
        stats = self.db.fetch_one("""
            SELECT COUNT(*), SUM(total_syp), SUM(total_usd), SUM(discount_syp)
            FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?
        """, (from_date, to_date))

        if not stats or not stats[0]:
            ttk.Label(self.report_frame, text="لا توجد مبيعات في هذه الفترة", 
                      font=('Arial', 12)).pack(pady=50)
            return

        count, total_syp, total_usd, discount_syp = stats
        total_syp = total_syp or 0
        total_usd = total_usd or 0
        discount_syp = discount_syp or 0

        # إطار علوي للإحصائيات والمخطط
        top_frame = ttk.Frame(self.report_frame)
        top_frame.pack(fill='x', pady=5)

        # حاوية المخطط البياني
        chart_container = ttk.LabelFrame(top_frame, text="المبيعات اليومية (ل.س)", padding=10)
        chart_container.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # حاوية الإحصائيات
        stats_container = ttk.LabelFrame(top_frame, text="ملخص المبيعات", padding=15)
        stats_container.pack(side='left', fill='y')
        
        self.create_stat_label(stats_container, "عدد المبيعات:", f"{count}")
        self.create_stat_label(stats_container, "الإجمالي (ل.س):", f"{total_syp:,.2f}")
        self.create_stat_label(stats_container, "الإجمالي ($):", f"{total_usd:,.2f}")
        self.create_stat_label(stats_container, "الخصومات (ل.س):", f"{discount_syp:,.2f}")
        
        sales_by_day = self.db.fetch_all("""
            SELECT DATE(sale_date), SUM(total_syp)
            FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?
            GROUP BY DATE(sale_date) ORDER BY DATE(sale_date)
        """, (from_date, to_date))
        
        if sales_by_day:
            dates = [row[0] for row in sales_by_day]
            totals = [row[1] for row in sales_by_day]
            
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.bar(dates, totals, color='skyblue')
            ax.set_ylabel(get_display(arabic_reshaper.reshape('إجمالي المبيعات (ل.س)')))
            ax.set_xlabel(get_display(arabic_reshaper.reshape('التاريخ')))
            fig.autofmt_xdate()
            
            canvas = FigureCanvasTkAgg(fig, master=chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        # جدول تفاصيل المبيعات
        table_frame = ttk.LabelFrame(self.report_frame, text="تفاصيل المبيعات", padding=10)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ('id', 'total_syp', 'total_usd', 'payment', 'date')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            tree.heading(col, text={'id': 'رقم', 'total_syp': 'المبلغ (ل.س)', 'total_usd': 'المبلغ ($)', 
                                    'payment': 'طريقة الدفع', 'date': 'التاريخ'}[col])
            tree.column(col, width=100, anchor='center')

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)
        
        sales_data = self.db.fetch_all("""
            SELECT id, total_syp, total_usd, payment_method, sale_date
            FROM sales WHERE DATE(sale_date) BETWEEN ? AND ? ORDER BY id DESC
        """, (from_date, to_date))
        
        for sale in sales_data:
            tree.insert('', 'end', values=sale)
    
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
        """تقرير الأرباح مع تحسينات بصرية"""
        ttk.Label(self.report_frame, text=f"تقرير الأرباح والخسائر من {from_date} إلى {to_date}", 
                  font=('Arial', 16, 'bold')).pack(pady=10)

        # جلب البيانات
        sales_syp, sales_usd = self.db.fetch_one("SELECT SUM(total_syp), SUM(total_usd) FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?", (from_date, to_date)) or (0, 0)
        cogs_syp, cogs_usd = self.db.fetch_one("SELECT SUM(si.quantity * p.purchase_price_syp), SUM(si.quantity * p.purchase_price_usd) FROM sale_items si JOIN sales s ON si.sale_id = s.id JOIN products p ON si.product_id = p.id WHERE DATE(s.sale_date) BETWEEN ? AND ?", (from_date, to_date)) or (0, 0)
        expenses_syp, expenses_usd = self.db.fetch_one("SELECT SUM(amount_syp), SUM(amount_usd) FROM expenses WHERE DATE(expense_date) BETWEEN ? AND ?", (from_date, to_date)) or (0, 0)

        sales_syp, sales_usd = sales_syp or 0, sales_usd or 0
        cogs_syp, cogs_usd = cogs_syp or 0, cogs_usd or 0
        expenses_syp, expenses_usd = expenses_syp or 0, expenses_usd or 0

        net_profit_syp = sales_syp - cogs_syp - expenses_syp

        # الإطار الرئيسي
        main_frame = ttk.Frame(self.report_frame)
        main_frame.pack(fill='both', expand=True, pady=10)

        # حاوية المخطط
        chart_container = ttk.LabelFrame(main_frame, text="توزيع الإيرادات والتكاليف (ل.س)", padding=10)
        chart_container.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # حاوية الملخص
        summary_container = ttk.LabelFrame(main_frame, text="ملخص الأرباح (ل.س)", padding=15)
        summary_container.pack(side='left', fill='y')

        self.create_stat_label(summary_container, "إجمالي الإيرادات:", f"{sales_syp:,.2f}")
        self.create_stat_label(summary_container, "تكلفة البضاعة المباعة:", f"({cogs_syp:,.2f})")
        self.create_stat_label(summary_container, "المصروفات:", f"({expenses_syp:,.2f})")
        
        ttk.Separator(summary_container, orient='horizontal').pack(fill='x', pady=10)
        
        profit_color = 'green' if net_profit_syp >= 0 else 'red'
        profit_frame = ttk.Frame(summary_container)
        profit_frame.pack(fill='x', pady=5)
        ttk.Label(profit_frame, text="الربح الصافي:", font=('Arial', 12, 'bold')).pack(side='right')
        ttk.Label(profit_frame, text=f"{net_profit_syp:,.2f}", font=('Arial', 14, 'bold'), foreground=profit_color).pack(side='left')

        if sales_syp > 0:
            labels_ar = ['الربح الصافي', 'تكلفة البضاعة', 'المصروفات']
            sizes = [max(0, net_profit_syp), cogs_syp, expenses_syp]
            colors = ['lightgreen', 'coral', 'lightskyblue']
            
            # إزالة القيم الصفرية وتشكيل النصوص العربية
            non_zero_data = []
            for label, size, color in zip(labels_ar, sizes, colors):
                if size > 0:
                    reshaped_text = arabic_reshaper.reshape(label)
                    bidi_text = get_display(reshaped_text)
                    non_zero_data.append((bidi_text, size, color))

            if non_zero_data:
                labels, sizes, colors = zip(*non_zero_data)

                fig = Figure(figsize=(5, 5), dpi=100)
                ax = fig.add_subplot(111)
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
                ax.axis('equal')  # لضمان أن المخطط دائري
                
                canvas = FigureCanvasTkAgg(fig, master=chart_container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
        else:
            ttk.Label(chart_container, text="لا توجد إيرادات لعرض المخطط").pack(pady=50)
    
    def show_top_products_report(self, from_date, to_date):
        """تقرير أفضل المنتجات مبيعاً مع مخطط بياني"""
        ttk.Label(self.report_frame, text=f"أفضل المنتجات مبيعاً من {from_date} إلى {to_date}", 
                  font=('Arial', 16, 'bold')).pack(pady=10)

        products = self.db.fetch_all("""
            SELECT si.product_name, SUM(si.quantity), SUM(si.subtotal_syp), SUM(si.subtotal_usd)
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            GROUP BY si.product_name
            ORDER BY SUM(si.quantity) DESC
            LIMIT 50
        """, (from_date, to_date))

        if not products:
            ttk.Label(self.report_frame, text="لا توجد بيانات لعرضها", 
                      font=('Arial', 12)).pack(pady=50)
            return

        # إطار علوي للمخطط والجدول
        top_frame = ttk.Frame(self.report_frame)
        top_frame.pack(fill='both', expand=True, pady=5)

        # حاوية المخطط البياني (أفضل 10)
        chart_container = ttk.LabelFrame(top_frame, text="أفضل 10 منتجات (حسب الكمية)", padding=10)
        chart_container.pack(side='top', fill='x', pady=(0, 10))
        
        top_10_products = products[:10]
        
        # تشكيل أسماء المنتجات العربية
        product_names_ar = [p[0] for p in top_10_products]
        product_names = [get_display(arabic_reshaper.reshape(name)) for name in product_names_ar]
        quantities = [p[1] for p in top_10_products]

        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh(product_names, quantities, color='coral')
        ax.set_xlabel(get_display(arabic_reshaper.reshape('الكمية المباعة')))
        ax.invert_yaxis()  # لعرض المنتج الأعلى في الأعلى
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='x', expand=True)

        # جدول كل المنتجات
        table_frame = ttk.LabelFrame(top_frame, text="قائمة المنتجات", padding=10)
        table_frame.pack(fill='both', expand=True)
        
        columns = ('product', 'quantity', 'total_syp', 'total_usd')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        tree.heading('product', text='المنتج')
        tree.heading('quantity', text='الكمية المباعة')
        tree.heading('total_syp', text='المبيعات (ل.س)')
        tree.heading('total_usd', text='المبيعات ($)')
        
        tree.column('product', width=250)
        tree.column('quantity', anchor='center')
        tree.column('total_syp', anchor='center')
        tree.column('total_usd', anchor='center')

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)
        
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
    
    def create_stat_label(self, parent, title, value):
        """إنشاء ملصق عرض إحصائيات"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=4)
        ttk.Label(frame, text=title, font=('Arial', 11)).pack(side='right')
        ttk.Label(frame, text=value, font=('Arial', 12, 'bold')).pack(side='left')

    def create_stat_box(self, parent, title, value, column):
        """إنشاء صندوق إحصائيات"""
        box = ttk.Frame(parent, relief='raised', borderwidth=2)
        box.grid(row=0, column=column, padx=10, pady=10, sticky='ew')
        parent.columnconfigure(column, weight=1)
        
        ttk.Label(box, text=title, font=('Arial', 11)).pack(pady=(10, 5))
        ttk.Label(box, text=value, font=('Arial', 16, 'bold')).pack(pady=(5, 10))
