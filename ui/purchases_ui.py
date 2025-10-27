import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class PurchasesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cart = []
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة إدارة المشتريات"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="إدارة المشتريات",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار الإضافة
        ttk.Button(
            self.parent,
            text="+ إضافة مشتريات جديدة",
            command=self.show_purchase_dialog,
            style='success.TButton'
        ).pack(pady=10)
        
        # جدول المشتريات
        table_frame = ttk.LabelFrame(self.parent, text="سجل المشتريات", padding=10)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('id', 'supplier', 'total_syp', 'total_usd', 'payment', 'date')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        self.tree.heading('id', text='رقم')
        self.tree.heading('supplier', text='المورد')
        self.tree.heading('total_syp', text='المجموع (ل.س)')
        self.tree.heading('total_usd', text='المجموع ($)')
        self.tree.heading('payment', text='طريقة الدفع')
        self.tree.heading('date', text='التاريخ')
        
        self.tree.column('id', width=80, anchor='center')
        self.tree.column('supplier', width=200, anchor='center')
        self.tree.column('total_syp', width=150, anchor='center')
        self.tree.column('total_usd', width=150, anchor='center')
        self.tree.column('payment', width=120, anchor='center')
        self.tree.column('date', width=200, anchor='center')
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='right', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        self.tree.bind('<Double-1>', self.show_purchase_details)
        
        self.load_purchases()
    
    def load_purchases(self):
        """تحميل المشتريات"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        purchases = self.db.fetch_all("""
            SELECT p.id, COALESCE(s.name, 'بدون مورد'), 
                   p.total_syp, p.total_usd, p.payment_method, p.purchase_date
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            ORDER BY p.id DESC
        """)
        
        for purchase in purchases:
            self.tree.insert('', 'end', values=purchase)
    
    def show_purchase_dialog(self):
        """عرض نافذة إضافة مشتريات"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("إضافة مشتريات جديدة")
        dialog.geometry("1000x700")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        self.cart = []
        
        # إطار المعلومات الأساسية
        info_frame = ttk.LabelFrame(dialog, text="معلومات المشتريات", padding=10)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        # المورد
        ttk.Label(info_frame, text="المورد:", font=('Arial', 11)).grid(row=0, column=1, padx=10, pady=10, sticky='e')
        supplier_var = tk.StringVar()
        supplier_combo = ttk.Combobox(info_frame, textvariable=supplier_var, font=('Arial', 11), width=25, state='readonly')
        
        suppliers = self.db.fetch_all("SELECT id, name FROM suppliers")
        supplier_dict = {sup[1]: sup[0] for sup in suppliers}
        supplier_combo['values'] = list(supplier_dict.keys())
        supplier_combo.grid(row=0, column=0, padx=10, pady=10)
        
        # إطار المنتجات
        products_frame = ttk.LabelFrame(dialog, text="إضافة منتجات", padding=10)
        products_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # اختيار المنتج
        select_frame = ttk.Frame(products_frame)
        select_frame.pack(fill='x', pady=10)
        
        ttk.Label(select_frame, text="المنتج:", font=('Arial', 11)).pack(side='right', padx=10)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(select_frame, textvariable=product_var, font=('Arial', 11), width=25)
        
        products = self.db.fetch_all("SELECT id, name, purchase_price_syp, purchase_price_usd FROM products")
        product_dict = {f"{p[1]}": {'id': p[0], 'price_syp': p[2], 'price_usd': p[3]} for p in products}
        product_combo['values'] = list(product_dict.keys())
        product_combo.pack(side='right', padx=10)
        
        ttk.Label(select_frame, text="الكمية:", font=('Arial', 11)).pack(side='right', padx=10)
        quantity_entry = ttk.Entry(select_frame, font=('Arial', 11), width=10)
        quantity_entry.pack(side='right', padx=10)
        
        def add_product():
            product_name = product_var.get()
            if not product_name or product_name not in product_dict:
                messagebox.showerror("خطأ", "يرجى اختيار منتج")
                return
            
            try:
                quantity = float(quantity_entry.get())
                if quantity <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("خطأ", "يرجى إدخال كمية صحيحة")
                return
            
            product_info = product_dict[product_name]
            total_syp = quantity * product_info['price_syp']
            total_usd = quantity * product_info['price_usd']
            
            self.cart.append({
                'product_id': product_info['id'],
                'name': product_name,
                'quantity': quantity,
                'unit_price_syp': product_info['price_syp'],
                'unit_price_usd': product_info['price_usd'],
                'total_syp': total_syp,
                'total_usd': total_usd
            })
            
            update_cart()
            product_var.set('')
            quantity_entry.delete(0, 'end')
        
        ttk.Button(
            select_frame,
            text="إضافة",
            command=add_product,
            style='success.TButton'
        ).pack(side='left', padx=10)
        
        # جدول المنتجات
        cart_columns = ('name', 'quantity', 'price_syp', 'price_usd', 'total_syp', 'total_usd')
        cart_tree = ttk.Treeview(products_frame, columns=cart_columns, show='headings', height=10)
        
        cart_tree.heading('name', text='المنتج')
        cart_tree.heading('quantity', text='الكمية')
        cart_tree.heading('price_syp', text='سعر (ل.س)')
        cart_tree.heading('price_usd', text='سعر ($)')
        cart_tree.heading('total_syp', text='مجموع (ل.س)')
        cart_tree.heading('total_usd', text='مجموع ($)')
        
        cart_tree.pack(fill='both', expand=True)
        
        def update_cart():
            for item in cart_tree.get_children():
                cart_tree.delete(item)
            
            for item in self.cart:
                cart_tree.insert('', 'end', values=(
                    item['name'], item['quantity'],
                    f"{item['unit_price_syp']:.2f}", f"{item['unit_price_usd']:.2f}",
                    f"{item['total_syp']:.2f}", f"{item['total_usd']:.2f}"
                ))
            
            total_syp = sum(item['total_syp'] for item in self.cart)
            total_usd = sum(item['total_usd'] for item in self.cart)
            total_syp_label.config(text=f"{total_syp:,.2f}")
            total_usd_label.config(text=f"{total_usd:,.2f}")
        
        # الإجماليات
        totals_frame = ttk.Frame(products_frame)
        totals_frame.pack(fill='x', pady=10)
        
        ttk.Label(totals_frame, text="الإجمالي (ل.س):", font=('Arial', 12, 'bold')).pack(side='right', padx=10)
        total_syp_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 14, 'bold'))
        total_syp_label.pack(side='right', padx=10)
        
        ttk.Label(totals_frame, text="الإجمالي ($):", font=('Arial', 12, 'bold')).pack(side='left', padx=10)
        total_usd_label = ttk.Label(totals_frame, text="0.00", font=('Arial', 14, 'bold'))
        total_usd_label.pack(side='left', padx=10)
        
        # إطار الدفع
        payment_frame = ttk.LabelFrame(dialog, text="معلومات الدفع", padding=10)
        payment_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(payment_frame, text="طريقة الدفع:", font=('Arial', 11)).grid(row=0, column=1, padx=10, pady=10, sticky='e')
        payment_var = tk.StringVar(value='نقدي')
        ttk.Combobox(payment_frame, textvariable=payment_var, font=('Arial', 11), width=20, state='readonly',
                     values=['نقدي', 'بطاقة', 'آجل', 'شيك']).grid(row=0, column=0, padx=10, pady=10)
        
        ttk.Label(payment_frame, text="المبلغ المدفوع (ل.س):", font=('Arial', 11)).grid(row=1, column=1, padx=10, pady=10, sticky='e')
        paid_syp_entry = ttk.Entry(payment_frame, font=('Arial', 11), width=20)
        paid_syp_entry.insert(0, '0')
        paid_syp_entry.grid(row=1, column=0, padx=10, pady=10)
        
        ttk.Label(payment_frame, text="المبلغ المدفوع ($):", font=('Arial', 11)).grid(row=2, column=1, padx=10, pady=10, sticky='e')
        paid_usd_entry = ttk.Entry(payment_frame, font=('Arial', 11), width=20)
        paid_usd_entry.insert(0, '0')
        paid_usd_entry.grid(row=2, column=0, padx=10, pady=10)
        
        # ملاحظات
        ttk.Label(payment_frame, text="ملاحظات:", font=('Arial', 11)).grid(row=3, column=1, padx=10, pady=10, sticky='ne')
        notes_text = tk.Text(payment_frame, font=('Arial', 11), width=20, height=3)
        notes_text.grid(row=3, column=0, padx=10, pady=10)
        
        # زر الحفظ
        def save_purchase():
            if not self.cart:
                messagebox.showerror("خطأ", "يرجى إضافة منتجات")
                return
            
            supplier_name = supplier_var.get()
            supplier_id = supplier_dict.get(supplier_name) if supplier_name else None
            
            try:
                paid_syp = float(paid_syp_entry.get() or 0)
                paid_usd = float(paid_usd_entry.get() or 0)
            except:
                messagebox.showerror("خطأ", "مبلغ غير صحيح")
                return
            
            total_syp = sum(item['total_syp'] for item in self.cart)
            total_usd = sum(item['total_usd'] for item in self.cart)
            payment_method = payment_var.get()
            notes = notes_text.get('1.0', 'end-1c').strip()
            
            # حفظ المشتريات
            if self.db.execute_query(
                """INSERT INTO purchases 
                   (supplier_id, total_syp, total_usd, payment_method, paid_amount_syp, paid_amount_usd, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (supplier_id, total_syp, total_usd, payment_method, paid_syp, paid_usd, notes)
            ):
                purchase_id = self.db.cursor.lastrowid
                
                # حفظ العناصر وتحديث المخزون
                for item in self.cart:
                    self.db.execute_query(
                        """INSERT INTO purchase_items 
                           (purchase_id, product_id, product_name, quantity, unit_price_syp, unit_price_usd, subtotal_syp, subtotal_usd)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (purchase_id, item['product_id'], item['name'], item['quantity'],
                         item['unit_price_syp'], item['unit_price_usd'],
                         item['total_syp'], item['total_usd'])
                    )
                    
                    # تحديث المخزون
                    self.db.execute_query(
                        "UPDATE products SET quantity = quantity + ? WHERE id = ?",
                        (item['quantity'], item['product_id'])
                    )
                    
                    # حركة المخزون
                    self.db.execute_query(
                        """INSERT INTO inventory_movements (product_id, movement_type, quantity, reason)
                           VALUES (?, 'in', ?, 'شراء')""",
                        (item['product_id'], item['quantity'])
                    )
                
                # تحديث ديون المورد
                if supplier_id:
                    remaining_syp = total_syp - paid_syp
                    remaining_usd = total_usd - paid_usd
                    if remaining_syp > 0 or remaining_usd > 0:
                        self.db.execute_query(
                            "UPDATE suppliers SET debt_syp = debt_syp + ?, debt_usd = debt_usd + ? WHERE id = ?",
                            (remaining_syp, remaining_usd, supplier_id)
                        )
                
                messagebox.showinfo("نجاح", f"تم تسجيل المشتريات بنجاح\nرقم: {purchase_id}")
                dialog.destroy()
                self.load_purchases()
            else:
                messagebox.showerror("خطأ", "فشل في حفظ المشتريات")
        
        ttk.Button(
            dialog,
            text="✓ حفظ المشتريات",
            command=save_purchase,
            style='success.TButton'
        ).pack(fill='x', padx=20, pady=20)
    
    def show_purchase_details(self, event):
        """عرض تفاصيل مشتريات"""
        selected = self.tree.selection()
        if not selected:
            return
        
        purchase_id = self.tree.item(selected[0])['values'][0]
        
        # نافذة التفاصيل
        details = tk.Toplevel(self.parent)
        details.title(f"تفاصيل المشتريات #{purchase_id}")
        details.geometry("800x600")
        
        # معلومات المشتريات
        purchase = self.db.fetch_one("SELECT * FROM purchases WHERE id = ?", (purchase_id,))
        
        info_frame = ttk.LabelFrame(details, text="معلومات عامة", padding=10)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(info_frame, text=f"رقم المشتريات: {purchase[0]}", font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(info_frame, text=f"التاريخ: {purchase[8]}", font=('Arial', 12)).pack(anchor='e', pady=5)
        ttk.Label(info_frame, text=f"طريقة الدفع: {purchase[4]}", font=('Arial', 12)).pack(anchor='e', pady=5)
        
        # العناصر
        items_frame = ttk.LabelFrame(details, text="المنتجات", padding=10)
        items_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('name', 'quantity', 'price_syp', 'price_usd', 'total_syp', 'total_usd')
        items_tree = ttk.Treeview(items_frame, columns=columns, show='headings')
        
        items_tree.heading('name', text='المنتج')
        items_tree.heading('quantity', text='الكمية')
        items_tree.heading('price_syp', text='سعر (ل.س)')
        items_tree.heading('price_usd', text='سعر ($)')
        items_tree.heading('total_syp', text='مجموع (ل.س)')
        items_tree.heading('total_usd', text='مجموع ($)')
        
        items_tree.pack(fill='both', expand=True)
        
        items = self.db.fetch_all(
            "SELECT product_name, quantity, unit_price_syp, unit_price_usd, subtotal_syp, subtotal_usd FROM purchase_items WHERE purchase_id = ?",
            (purchase_id,)
        )
        
        for item in items:
            items_tree.insert('', 'end', values=item)
        
        # الإجمالي
        total_frame = ttk.Frame(details)
        total_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(total_frame, text=f"الإجمالي (ل.س): {purchase[2]:,.2f}", 
                 font=('Arial', 14, 'bold')).pack(side='right', padx=10)
        ttk.Label(total_frame, text=f"الإجمالي ($): {purchase[3]:,.2f}", 
                 font=('Arial', 14, 'bold')).pack(side='left', padx=10)
