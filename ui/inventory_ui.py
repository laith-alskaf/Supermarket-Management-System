import tkinter as tk
from tkinter import ttk, messagebox

class InventoryUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        self.load_inventory()
        
    def setup_ui(self):
        """إعداد واجهة المخزون"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="إدارة المخزون",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار الفلاتر
        filter_frame = ttk.Frame(self.parent)
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(filter_frame, text="عرض:", font=('Arial', 11)).pack(side='right', padx=10)
        self.filter_var = tk.StringVar(value='all')
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                     font=('Arial', 11), width=20, state='readonly')
        filter_combo['values'] = ['الكل', 'قريب من النفاد', 'نفذ من المخزون']
        filter_combo.pack(side='right', padx=10)
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_inventory())
        
        ttk.Label(filter_frame, text="بحث:", font=('Arial', 11)).pack(side='left', padx=10)
        self.search_entry = ttk.Entry(filter_frame, font=('Arial', 11), width=25)
        self.search_entry.pack(side='left', padx=10)
        self.search_entry.bind('<KeyRelease>', lambda e: self.load_inventory())
        
        # جدول المخزون
        table_frame = ttk.LabelFrame(self.parent, text="المخزون الحالي", padding=10)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # إنشاء الجدول
        columns = ('id', 'name', 'category', 'quantity', 'min_quantity', 'unit', 'status')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # تعريف الأعمدة
        self.tree.heading('id', text='الرقم')
        self.tree.heading('name', text='اسم المنتج')
        self.tree.heading('category', text='الفئة')
        self.tree.heading('quantity', text='الكمية')
        self.tree.heading('min_quantity', text='الحد الأدنى')
        self.tree.heading('unit', text='الوحدة')
        self.tree.heading('status', text='الحالة')
        
        # عرض الأعمدة
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('name', width=200, anchor='center')
        self.tree.column('category', width=150, anchor='center')
        self.tree.column('quantity', width=100, anchor='center')
        self.tree.column('min_quantity', width=100, anchor='center')
        self.tree.column('unit', width=80, anchor='center')
        self.tree.column('status', width=120, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='right', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # تلوين الصفوف
        self.tree.tag_configure('low', background='#ffcccc')
        self.tree.tag_configure('out', background='#ff9999')
        self.tree.tag_configure('normal', background='#ccffcc')
        
        # النقر المزدوج لتعديل الكمية
        self.tree.bind('<Double-1>', self.adjust_quantity)
        
        # إحصائيات
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="", font=('Arial', 12, 'bold'))
        self.stats_label.pack(side='right', padx=20)
        
    def load_inventory(self):
        """تحميل المخزون"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # الفلتر
        filter_type = self.filter_var.get()
        search_term = self.search_entry.get().strip()
        
        # بناء الاستعلام
        query = """
            SELECT p.id, p.name, 
                   COALESCE(c.name, 'بدون فئة'), 
                   p.quantity, p.min_quantity, p.unit
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        """
        params = []
        
        if search_term:
            query += " AND p.name LIKE ?"
            params.append(f'%{search_term}%')
        
        if filter_type == 'قريب من النفاد':
            query += " AND p.quantity <= p.min_quantity AND p.quantity > 0"
        elif filter_type == 'نفذ من المخزون':
            query += " AND p.quantity = 0"
        
        query += " ORDER BY p.quantity ASC"
        
        # جلب البيانات
        products = self.db.fetch_all(query, tuple(params) if params else None)
        
        low_stock = 0
        out_of_stock = 0
        normal = 0
        
        # إضافة البيانات للجدول
        for product in products:
            product_id, name, category, quantity, min_quantity, unit = product
            
            # تحديد الحالة
            if quantity == 0:
                status = '⚠️ نفذ'
                tag = 'out'
                out_of_stock += 1
            elif quantity <= min_quantity:
                status = '⚠️ قريب من النفاد'
                tag = 'low'
                low_stock += 1
            else:
                status = '✓ متوفر'
                tag = 'normal'
                normal += 1
            
            self.tree.insert('', 'end', 
                           values=(product_id, name, category, quantity, min_quantity, unit, status),
                           tags=(tag,))
        
        # تحديث الإحصائيات
        self.stats_label.config(
            text=f"المجموع: {len(products)} | متوفر: {normal} | قريب من النفاد: {low_stock} | نفذ: {out_of_stock}"
        )
    
    def adjust_quantity(self, event):
        """تعديل كمية المنتج"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        product_id, name, category, current_qty = values[0], values[1], values[2], values[3]
        
        # نافذة التعديل
        dialog = tk.Toplevel(self.parent)
        dialog.title("تعديل الكمية")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"المنتج: {name}", font=('Arial', 12, 'bold')).pack(pady=10)
        ttk.Label(dialog, text=f"الكمية الحالية: {current_qty}", font=('Arial', 11)).pack(pady=10)
        
        # نوع العملية
        ttk.Label(dialog, text="نوع العملية:", font=('Arial', 11)).pack(pady=5)
        operation_var = tk.StringVar(value='add')
        ttk.Radiobutton(dialog, text="إضافة", variable=operation_var, value='add').pack()
        ttk.Radiobutton(dialog, text="سحب", variable=operation_var, value='remove').pack()
        
        # الكمية
        ttk.Label(dialog, text="الكمية:", font=('Arial', 11)).pack(pady=10)
        quantity_entry = ttk.Entry(dialog, font=('Arial', 11), width=15)
        quantity_entry.pack(pady=5)
        quantity_entry.focus()
        
        # السبب
        ttk.Label(dialog, text="السبب:", font=('Arial', 11)).pack(pady=10)
        reason_entry = ttk.Entry(dialog, font=('Arial', 11), width=30)
        reason_entry.pack(pady=5)
        
        def save():
            try:
                quantity = float(quantity_entry.get())
                if quantity <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("خطأ", "يرجى إدخال كمية صحيحة")
                return
            
            operation = operation_var.get()
            reason = reason_entry.get().strip() or 'تعديل يدوي'
            
            if operation == 'add':
                # إضافة
                if self.db.execute_query(
                    "UPDATE products SET quantity = quantity + ? WHERE id = ?",
                    (quantity, product_id)
                ):
                    self.db.execute_query(
                        """INSERT INTO inventory_movements (product_id, movement_type, quantity, reason)
                           VALUES (?, 'in', ?, ?)""",
                        (product_id, quantity, reason)
                    )
                    messagebox.showinfo("نجاح", "تم إضافة الكمية بنجاح")
                    dialog.destroy()
                    self.load_inventory()
            else:
                # سحب
                if quantity > current_qty:
                    messagebox.showerror("خطأ", "الكمية المطلوبة أكبر من المتوفر")
                    return
                
                if self.db.execute_query(
                    "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                    (quantity, product_id)
                ):
                    self.db.execute_query(
                        """INSERT INTO inventory_movements (product_id, movement_type, quantity, reason)
                           VALUES (?, 'out', ?, ?)""",
                        (product_id, quantity, reason)
                    )
                    messagebox.showinfo("نجاح", "تم سحب الكمية بنجاح")
                    dialog.destroy()
                    self.load_inventory()
        
        ttk.Button(
            dialog,
            text="حفظ",
            command=save,
            style='success.TButton'
        ).pack(pady=20)
