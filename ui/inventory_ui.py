import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pytz

class InventoryUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        # توقيت سوريا (GMT+3)
        self.syria_tz = pytz.timezone('Asia/Damascus')
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
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # الإطار الرئيسي مع padding
        container = ttk.Frame(dialog, padding=25)
        container.pack(fill='both', expand=True)
        
        # عنوان
        ttk.Label(
            container,
            text="تعديل كمية المنتج",
            font=('Arial', 16, 'bold'),
            foreground='#2c3e50',
            anchor='center'
        ).pack(pady=(0, 20))
        
        # معلومات المنتج
        info_frame = ttk.LabelFrame(container, text="معلومات المنتج", padding=15)
        info_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            info_frame,
            text=f"المنتج: {name}",
            font=('Arial', 12, 'bold'),
            anchor='e'
        ).pack(fill='x', pady=5)
        
        ttk.Label(
            info_frame,
            text=f"الفئة: {category}",
            font=('Arial', 11),
            anchor='e'
        ).pack(fill='x', pady=5)
        
        ttk.Label(
            info_frame,
            text=f"الكمية الحالية: {current_qty}",
            font=('Arial', 11),
            foreground='#27ae60',
            anchor='e'
        ).pack(fill='x', pady=5)
        
        # نوع العملية
        operation_frame = ttk.LabelFrame(container, text="نوع العملية", padding=15)
        operation_frame.pack(fill='x', pady=(0, 15))
        
        operation_var = tk.StringVar(value='add')
        
        ttk.Radiobutton(
            operation_frame,
            text="إضافة كمية",
            variable=operation_var,
            value='add'
        ).pack(anchor='e', pady=5)
        
        ttk.Radiobutton(
            operation_frame,
            text="سحب كمية",
            variable=operation_var,
            value='remove'
        ).pack(anchor='e', pady=5)
        
        # الكمية
        quantity_frame = ttk.LabelFrame(container, text="الكمية", padding=15)
        quantity_frame.pack(fill='x', pady=(0, 15))
        
        quantity_entry = ttk.Entry(
            quantity_frame,
            font=('Arial', 14),
            width=20,
            justify='center'
        )
        quantity_entry.pack(pady=5)
        quantity_entry.focus()
        
        # السبب
        reason_frame = ttk.LabelFrame(container, text="السبب (اختياري)", padding=15)
        reason_frame.pack(fill='x', pady=(0, 15))
        
        reason_entry = ttk.Entry(
            reason_frame,
            font=('Arial', 11),
            width=30
        )
        reason_entry.pack(pady=5)
        
        def save():
            try:
                qty_text = quantity_entry.get().strip()
                if not qty_text:
                    messagebox.showerror("خطأ", "يرجى إدخال الكمية", parent=dialog)
                    quantity_entry.focus()
                    return
                
                quantity = float(qty_text)
                if quantity <= 0:
                    messagebox.showerror("خطأ", "يرجى إدخال كمية أكبر من صفر", parent=dialog)
                    quantity_entry.focus()
                    return
            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال كمية صحيحة", parent=dialog)
                quantity_entry.focus()
                return
            
            operation = operation_var.get()
            reason = reason_entry.get().strip() or 'تعديل يدوي'
            
            # الحصول على التاريخ والوقت الحالي بتوقيت سوريا
            syria_time = datetime.now(self.syria_tz)
            movement_date = syria_time.strftime('%Y-%m-%d %H:%M:%S')
            
            if operation == 'add':
                # إضافة
                if self.db.execute_query(
                    "UPDATE products SET quantity = quantity + ?, updated_at = ? WHERE id = ?",
                    (quantity, movement_date, product_id)
                ):
                    self.db.execute_query(
                        """INSERT INTO inventory_movements (product_id, movement_type, quantity, reason, movement_date)
                           VALUES (?, 'in', ?, ?, ?)""",
                        (product_id, quantity, reason, movement_date)
                    )
                    messagebox.showinfo("نجاح", f"تم إضافة الكمية بنجاح\nالكمية الجديدة: {current_qty + quantity}", parent=dialog)
                    dialog.destroy()
                    self.load_inventory()
                else:
                    messagebox.showerror("خطأ", "فشل في إضافة الكمية", parent=dialog)
            else:
                # سحب
                if quantity > current_qty:
                    messagebox.showerror("خطأ", f"الكمية المطلوبة ({quantity}) أكبر من المتوفر ({current_qty})", parent=dialog)
                    quantity_entry.focus()
                    quantity_entry.select_range(0, tk.END)
                    return
                
                if self.db.execute_query(
                    "UPDATE products SET quantity = quantity - ?, updated_at = ? WHERE id = ?",
                    (quantity, movement_date, product_id)
                ):
                    self.db.execute_query(
                        """INSERT INTO inventory_movements (product_id, movement_type, quantity, reason, movement_date)
                           VALUES (?, 'out', ?, ?, ?)""",
                        (product_id, quantity, reason, movement_date)
                    )
                    messagebox.showinfo("نجاح", f"تم سحب الكمية بنجاح\nالكمية الجديدة: {current_qty - quantity}", parent=dialog)
                    dialog.destroy()
                    self.load_inventory()
                else:
                    messagebox.showerror("خطأ", "فشل في سحب الكمية", parent=dialog)
        
        # الأزرار
        button_frame = ttk.Frame(container)
        button_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(
            button_frame,
            text="✓ حفظ",
            command=save,
            style='success.TButton',
            width=18
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="✕ إلغاء",
            command=dialog.destroy,
            style='danger.TButton',
            width=18
        ).pack(side='left', padx=5)
        
        # ربط المفاتيح
        quantity_entry.bind('<Return>', lambda e: save())
        quantity_entry.bind('<KP_Enter>', lambda e: save())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        
        # تحديد حجم النافذة
        dialog.update_idletasks()
        width = 600
        height = 650
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
