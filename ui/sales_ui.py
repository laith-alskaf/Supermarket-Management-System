import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class SalesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cart = []
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة نقطة البيع"""
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
            text="نقطة البيع - POS",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # الإطار الرئيسي
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(fill='both', expand=True, padx=20)
        
        # الجانب الأيمن - اختيار المنتجات
        left_frame = ttk.LabelFrame(main_frame, text="اختيار المنتجات", padding=10)
        left_frame.pack(side='right', fill='both', expand=True, padx=(0, 10))
        
        # البحث
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill='x', pady=10)
        
        ttk.Label(search_frame, text="بحث:", font=('Arial', 11)).pack(side='right', padx=10)
        self.search_entry = ttk.Entry(search_frame, font=('Arial', 11), width=25)
        self.search_entry.pack(side='right', padx=10)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_products())
        
        # جدول المنتجات
        products_frame = ttk.Frame(left_frame)
        products_frame.pack(fill='both', expand=True)
        
        columns = ('id', 'name', 'price_syp', 'price_usd', 'quantity')
        self.products_tree = ttk.Treeview(products_frame, columns=columns, show='headings', height=15)
        
        self.products_tree.heading('id', text='الرقم')
        self.products_tree.heading('name', text='اسم المنتج')
        self.products_tree.heading('price_syp', text='السعر (ل.س)')
        self.products_tree.heading('price_usd', text='السعر ($)')
        self.products_tree.heading('quantity', text='المتوفر')
        
        self.products_tree.column('id', width=50, anchor='center')
        self.products_tree.column('name', width=200, anchor='center')
        self.products_tree.column('price_syp', width=100, anchor='center')
        self.products_tree.column('price_usd', width=100, anchor='center')
        self.products_tree.column('quantity', width=80, anchor='center')
        
        products_scrollbar = ttk.Scrollbar(products_frame, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=products_scrollbar.set)
        
        self.products_tree.pack(side='right', fill='both', expand=True)
        products_scrollbar.pack(side='left', fill='y')
        
        self.products_tree.bind('<Double-1>', self.add_to_cart)
        
        # الجانب الأيسر - سلة المشتريات
        right_frame = ttk.LabelFrame(main_frame, text="سلة المشتريات", padding=10)
        right_frame.pack(side='left', fill='both', expand=True)
        
        # جدول السلة
        cart_frame = ttk.Frame(right_frame)
        cart_frame.pack(fill='both', expand=True, pady=10)
        
        cart_columns = ('product_id', 'name', 'quantity', 'unit_price_syp', 'unit_price_usd', 'total_syp', 'total_usd')
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show='headings', height=12)
        
        self.cart_tree.heading('product_id', text='#')
        self.cart_tree.heading('name', text='المنتج')
        self.cart_tree.heading('quantity', text='الكمية')
        self.cart_tree.heading('unit_price_syp', text='سعر (ل.س)')
        self.cart_tree.heading('unit_price_usd', text='سعر ($)')
        self.cart_tree.heading('total_syp', text='المجموع (ل.س)')
        self.cart_tree.heading('total_usd', text='المجموع ($)')
        
        self.cart_tree.column('product_id', width=40, anchor='center')
        self.cart_tree.column('name', width=150, anchor='center')
        self.cart_tree.column('quantity', width=60, anchor='center')
        self.cart_tree.column('unit_price_syp', width=80, anchor='center')
        self.cart_tree.column('unit_price_usd', width=70, anchor='center')
        self.cart_tree.column('total_syp', width=100, anchor='center')
        self.cart_tree.column('total_usd', width=80, anchor='center')
        
        cart_scrollbar = ttk.Scrollbar(cart_frame, orient='vertical', command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_tree.pack(side='right', fill='both', expand=True)
        cart_scrollbar.pack(side='left', fill='y')
        
        # أزرار السلة
        cart_buttons = ttk.Frame(right_frame)
        cart_buttons.pack(fill='x', pady=10)
        
        ttk.Button(
            cart_buttons,
            text="حذف من السلة",
            command=self.remove_from_cart,
            style='danger.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            cart_buttons,
            text="مسح السلة",
            command=self.clear_cart,
            style='warning.TButton'
        ).pack(side='right', padx=5)
        
        # الإجماليات
        totals_frame = ttk.Frame(right_frame)
        totals_frame.pack(fill='x', pady=10)
        
        ttk.Label(totals_frame, text="الإجمالي (ل.س):", font=('Arial', 12, 'bold')).pack(side='right', padx=10)
        self.total_syp_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 14, 'bold'), foreground='green')
        self.total_syp_label.pack(side='right', padx=10)
        
        ttk.Label(totals_frame, text="الإجمالي ($):", font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        self.total_usd_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 14, 'bold'), foreground='blue')
        self.total_usd_label.pack(side='left', padx=10)
        
        # الخصم
        discount_frame = ttk.Frame(right_frame)
        discount_frame.pack(fill='x', pady=10)
        
        ttk.Label(discount_frame, text="خصم (ل.س):", font=('Arial', 11)).pack(side='right', padx=10)
        self.discount_syp_entry = ttk.Entry(discount_frame, font=('Arial', 11), width=10)
        self.discount_syp_entry.insert(0, '0')
        self.discount_syp_entry.pack(side='right', padx=10)
        self.discount_syp_entry.bind('<KeyRelease>', lambda e: self.update_totals())
        
        ttk.Label(discount_frame, text="خصم ($):", font=('Arial', 11)).pack(side='left', padx=10)
        self.discount_usd_entry = ttk.Entry(discount_frame, font=('Arial', 11), width=10)
        self.discount_usd_entry.insert(0, '0')
        self.discount_usd_entry.pack(side='left', padx=10)
        self.discount_usd_entry.bind('<KeyRelease>', lambda e: self.update_totals())
        
        # طريقة الدفع
        payment_frame = ttk.Frame(right_frame)
        payment_frame.pack(fill='x', pady=10)
        
        ttk.Label(payment_frame, text="طريقة الدفع:", font=('Arial', 11)).pack(side='right', padx=10)
        self.payment_var = tk.StringVar(value='نقدي')
        payment_combo = ttk.Combobox(payment_frame, textvariable=self.payment_var, 
                                      font=('Arial', 11), width=15, state='readonly')
        payment_combo['values'] = ['نقدي', 'بطاقة', 'آجل']
        payment_combo.pack(side='right', padx=10)
        
        # ملاحظات
        ttk.Label(right_frame, text="ملاحظات:", font=('Arial', 11)).pack(anchor='e', padx=10, pady=5)
        self.notes_text = tk.Text(right_frame, font=('Arial', 10), height=3)
        self.notes_text.pack(fill='x', padx=10, pady=5)
        
        # زر إتمام البيع
        ttk.Button(
            right_frame,
            text="✓ إتمام البيع",
            command=self.complete_sale,
            style='success.TButton'
        ).pack(fill='x', padx=10, pady=20)
        
        # تحميل المنتجات
        self.load_products()
        
        # عرض Canvas و Scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_products(self):
        """تحميل المنتجات"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        products = self.db.fetch_all(
            "SELECT id, name, selling_price_syp, selling_price_usd, quantity FROM products WHERE quantity > 0 ORDER BY name"
        )
        
        for product in products:
            self.products_tree.insert('', 'end', values=product)
    
    def search_products(self):
        """البحث عن منتجات"""
        search_term = self.search_entry.get().strip()
        
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        products = self.db.fetch_all(
            "SELECT id, name, selling_price_syp, selling_price_usd, quantity FROM products WHERE name LIKE ? AND quantity > 0 ORDER BY name",
            (f'%{search_term}%',)
        )
        
        for product in products:
            self.products_tree.insert('', 'end', values=product)
    
    def add_to_cart(self, event=None):
        """إضافة منتج للسلة"""
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار منتج")
            return
        
        values = self.products_tree.item(selected[0])['values']
        product_id, name, price_syp, price_usd, available_qty = values
        
        # إنشاء نافذة الحوار
        quantity_dialog = tk.Toplevel(self.parent)
        quantity_dialog.title("إدخال الكمية")
        quantity_dialog.resizable(False, False)
        quantity_dialog.transient(self.parent)
        quantity_dialog.grab_set()
        
        # الإطار الرئيسي مع padding
        container = ttk.Frame(quantity_dialog, padding=20)
        container.pack(fill='both', expand=True)
        
        # عنوان
        title_label = ttk.Label(
            container,
            text="إضافة منتج إلى السلة",
            font=('Arial', 14, 'bold'),
            foreground='#2c3e50'
        )
        title_label.pack(pady=(0, 15))
        
        # معلومات المنتج
        info_frame = ttk.LabelFrame(container, text="معلومات المنتج", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(
            info_frame,
            text=f"المنتج: {name}",
            font=('Arial', 11, 'bold')
        ).pack(anchor='e', pady=3)
        
        ttk.Label(
            info_frame,
            text=f"السعر: {price_syp:.2f} ل.س",
            font=('Arial', 10)
        ).pack(anchor='e', pady=3)
        
        ttk.Label(
            info_frame,
            text=f"الكمية المتوفرة: {available_qty}",
            font=('Arial', 10),
            foreground='#27ae60'
        ).pack(anchor='e', pady=3)
        
        # إدخال الكمية
        input_frame = ttk.LabelFrame(container, text="الكمية المطلوبة", padding=10)
        input_frame.pack(fill='x', pady=(0, 10))
        
        quantity_entry = ttk.Entry(
            input_frame,
            font=('Arial', 14),
            width=25,
            justify='center'
        )
        quantity_entry.pack(pady=5)
        quantity_entry.insert(0, '1')
        quantity_entry.focus()
        quantity_entry.select_range(0, tk.END)
        
        # دالة الإضافة
        def add_to_cart_action():
            try:
                qty_text = quantity_entry.get().strip()
                if not qty_text:
                    messagebox.showerror("خطأ", "الرجاء إدخال الكمية", parent=quantity_dialog)
                    quantity_entry.focus()
                    return
                
                qty = float(qty_text)
                
                if qty <= 0:
                    messagebox.showerror("خطأ", "الكمية يجب أن تكون أكبر من صفر", parent=quantity_dialog)
                    quantity_entry.focus()
                    quantity_entry.select_range(0, tk.END)
                    return
                
                if qty > available_qty:
                    messagebox.showerror("خطأ", f"الكمية المتوفرة فقط: {available_qty}", parent=quantity_dialog)
                    quantity_entry.focus()
                    quantity_entry.select_range(0, tk.END)
                    return
                
                # حساب الإجماليات
                total_syp = qty * price_syp
                total_usd = qty * price_usd
                
                # إضافة إلى السلة
                self.cart.append({
                    'product_id': product_id,
                    'name': name,
                    'quantity': qty,
                    'unit_price_syp': price_syp,
                    'unit_price_usd': price_usd,
                    'total_syp': total_syp,
                    'total_usd': total_usd
                })
                
                # تحديث العرض
                self.update_cart_display()
                
                # إغلاق النافذة
                quantity_dialog.destroy()
                
                # رسالة نجاح
                messagebox.showinfo("نجاح", f"تمت إضافة '{name}' إلى السلة بنجاح")
                
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال رقم صحيح", parent=quantity_dialog)
                quantity_entry.focus()
                quantity_entry.select_range(0, tk.END)
        
        # الأزرار
        button_frame = ttk.Frame(container)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # زر الإضافة
        add_button = ttk.Button(
            button_frame,
            text="✓ إضافة",
            command=add_to_cart_action,
            style='success.TButton',
            width=15
        )
        add_button.pack(side='right', padx=5)
        
        # زر الإلغاء
        cancel_button = ttk.Button(
            button_frame,
            text="✕ إلغاء",
            command=quantity_dialog.destroy,
            style='danger.TButton',
            width=15
        )
        cancel_button.pack(side='left', padx=5)
        
        # ربط المفاتيح
        quantity_entry.bind('<Return>', lambda e: add_to_cart_action())
        quantity_entry.bind('<KP_Enter>', lambda e: add_to_cart_action())
        quantity_dialog.bind('<Escape>', lambda e: quantity_dialog.destroy())
        
        # تحديد حجم النافذة بعد إضافة جميع العناصر
        quantity_dialog.update_idletasks()
        width = 450
        height = 350
        x = (quantity_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (quantity_dialog.winfo_screenheight() // 2) - (height // 2)
        quantity_dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def update_cart_display(self):
        """تحديث عرض السلة"""
        # مسح الجدول
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # إضافة العناصر
        for item in self.cart:
            self.cart_tree.insert('', 'end', values=(
                item['product_id'],
                item['name'],
                item['quantity'],
                f"{item['unit_price_syp']:.2f}",
                f"{item['unit_price_usd']:.2f}",
                f"{item['total_syp']:.2f}",
                f"{item['total_usd']:.2f}"
            ))
        
        self.update_totals()
    
    def update_totals(self):
        """تحديث الإجماليات"""
        total_syp = sum(item['total_syp'] for item in self.cart)
        total_usd = sum(item['total_usd'] for item in self.cart)
        
        try:
            discount_syp = float(self.discount_syp_entry.get() or 0)
            discount_usd = float(self.discount_usd_entry.get() or 0)
        except ValueError:
            discount_syp = 0
            discount_usd = 0
        
        final_syp = total_syp - discount_syp
        final_usd = total_usd - discount_usd
        
        self.total_syp_label.config(text=f"{final_syp:,.2f}")
        self.total_usd_label.config(text=f"{final_usd:,.2f}")
    
    def remove_from_cart(self):
        """حذف من السلة"""
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار عنصر للحذف")
            return
        
        index = self.cart_tree.index(selected[0])
        self.cart.pop(index)
        self.update_cart_display()
    
    def clear_cart(self):
        """مسح السلة"""
        if self.cart and messagebox.askyesno("تأكيد", "هل تريد مسح السلة؟"):
            self.cart = []
            self.update_cart_display()
    
    def complete_sale(self):
        """إتمام البيع"""
        if not self.cart:
            messagebox.showerror("خطأ", "السلة فارغة")
            return
        
        try:
            discount_syp = float(self.discount_syp_entry.get() or 0)
            discount_usd = float(self.discount_usd_entry.get() or 0)
        except ValueError:
            messagebox.showerror("خطأ", "خصم غير صحيح")
            return
        
        total_syp = sum(item['total_syp'] for item in self.cart) - discount_syp
        total_usd = sum(item['total_usd'] for item in self.cart) - discount_usd
        
        payment_method = self.payment_var.get()
        notes = self.notes_text.get('1.0', 'end-1c').strip()
        
        # حفظ البيع
        if self.db.execute_query(
            """INSERT INTO sales (total_syp, total_usd, payment_method, discount_syp, discount_usd, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (total_syp, total_usd, payment_method, discount_syp, discount_usd, notes)
        ):
            sale_id = self.db.cursor.lastrowid
            
            # حفظ عناصر البيع وتحديث المخزون
            for item in self.cart:
                self.db.execute_query(
                    """INSERT INTO sale_items 
                       (sale_id, product_id, product_name, quantity, unit_price_syp, unit_price_usd, subtotal_syp, subtotal_usd)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sale_id, item['product_id'], item['name'], item['quantity'],
                     item['unit_price_syp'], item['unit_price_usd'],
                     item['total_syp'], item['total_usd'])
                )
                
                # تحديث المخزون
                self.db.execute_query(
                    "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                    (item['quantity'], item['product_id'])
                )
                
                # تسجيل حركة المخزون
                self.db.execute_query(
                    """INSERT INTO inventory_movements (product_id, movement_type, quantity, reason)
                       VALUES (?, 'out', ?, 'بيع')""",
                    (item['product_id'], item['quantity'])
                )
            
            messagebox.showinfo("نجاح", f"تم تسجيل البيع بنجاح\nرقم الفاتورة: {sale_id}")
            
            # مسح السلة
            self.cart = []
            self.update_cart_display()
            self.discount_syp_entry.delete(0, 'end')
            self.discount_syp_entry.insert(0, '0')
            self.discount_usd_entry.delete(0, 'end')
            self.discount_usd_entry.insert(0, '0')
            self.notes_text.delete('1.0', 'end')
            self.load_products()
        else:
            messagebox.showerror("خطأ", "فشل في تسجيل البيع")
