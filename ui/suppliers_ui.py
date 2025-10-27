import tkinter as tk
from tkinter import ttk, messagebox

class SuppliersUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.setup_ui()
        self.load_suppliers()
        
    def setup_ui(self):
        """إعداد واجهة إدارة الموردين"""
        # العنوان
        title = ttk.Label(
            self.parent,
            text="إدارة الموردين",
            font=('Arial', 20, 'bold')
        )
        title.pack(pady=20)
        
        # إطار النموذج
        form_frame = ttk.LabelFrame(self.parent, text="إضافة/تعديل مورد", padding=20)
        form_frame.pack(fill='x', padx=20, pady=10)
        
        # اسم المورد
        ttk.Label(form_frame, text="اسم المورد:", font=('Arial', 11)).grid(row=0, column=1, padx=10, pady=10, sticky='e')
        self.name_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.name_entry.grid(row=0, column=0, padx=10, pady=10)
        
        # رقم الهاتف
        ttk.Label(form_frame, text="رقم الهاتف:", font=('Arial', 11)).grid(row=1, column=1, padx=10, pady=10, sticky='e')
        self.phone_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.phone_entry.grid(row=1, column=0, padx=10, pady=10)
        
        # العنوان
        ttk.Label(form_frame, text="العنوان:", font=('Arial', 11)).grid(row=2, column=1, padx=10, pady=10, sticky='e')
        self.address_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.address_entry.grid(row=2, column=0, padx=10, pady=10)
        
        # الديون بالليرة
        ttk.Label(form_frame, text="الديون (ل.س):", font=('Arial', 11)).grid(row=3, column=1, padx=10, pady=10, sticky='e')
        self.debt_syp_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.debt_syp_entry.insert(0, '0')
        self.debt_syp_entry.grid(row=3, column=0, padx=10, pady=10)
        
        # الديون بالدولار
        ttk.Label(form_frame, text="الديون ($):", font=('Arial', 11)).grid(row=4, column=1, padx=10, pady=10, sticky='e')
        self.debt_usd_entry = ttk.Entry(form_frame, font=('Arial', 11), width=30)
        self.debt_usd_entry.insert(0, '0')
        self.debt_usd_entry.grid(row=4, column=0, padx=10, pady=10)
        
        # ملاحظات
        ttk.Label(form_frame, text="ملاحظات:", font=('Arial', 11)).grid(row=5, column=1, padx=10, pady=10, sticky='ne')
        self.notes_text = tk.Text(form_frame, font=('Arial', 11), width=30, height=3)
        self.notes_text.grid(row=5, column=0, padx=10, pady=10)
        
        # الأزرار
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            buttons_frame,
            text="إضافة",
            command=self.add_supplier,
            style='success.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="تحديث",
            command=self.update_supplier,
            style='info.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="حذف",
            command=self.delete_supplier,
            style='danger.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            buttons_frame,
            text="مسح الحقول",
            command=self.clear_fields,
            style='secondary.TButton'
        ).pack(side='right', padx=5)
        
        # جدول الموردين
        table_frame = ttk.LabelFrame(self.parent, text="قائمة الموردين", padding=10)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # إنشاء الجدول
        columns = ('id', 'name', 'phone', 'address', 'debt_syp', 'debt_usd')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # تعريف الأعمدة
        self.tree.heading('id', text='الرقم')
        self.tree.heading('name', text='اسم المورد')
        self.tree.heading('phone', text='الهاتف')
        self.tree.heading('address', text='العنوان')
        self.tree.heading('debt_syp', text='الديون (ل.س)')
        self.tree.heading('debt_usd', text='الديون ($)')
        
        # عرض الأعمدة
        self.tree.column('id', width=60, anchor='center')
        self.tree.column('name', width=200, anchor='center')
        self.tree.column('phone', width=150, anchor='center')
        self.tree.column('address', width=250, anchor='center')
        self.tree.column('debt_syp', width=120, anchor='center')
        self.tree.column('debt_usd', width=120, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='right', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        # ربط حدث النقر
        self.tree.bind('<ButtonRelease-1>', self.on_select)
        
    def load_suppliers(self):
        """تحميل الموردين"""
        # مسح الجدول
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # جلب البيانات
        suppliers = self.db.fetch_all("SELECT id, name, phone, address, debt_syp, debt_usd FROM suppliers ORDER BY id DESC")
        
        # إضافة البيانات للجدول
        for supplier in suppliers:
            self.tree.insert('', 'end', values=supplier)
    
    def add_supplier(self):
        """إضافة مورد جديد"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()
        notes = self.notes_text.get('1.0', 'end-1c').strip()
        
        try:
            debt_syp = float(self.debt_syp_entry.get() or 0)
            debt_usd = float(self.debt_usd_entry.get() or 0)
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة للديون")
            return
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المورد")
            return
        
        # إضافة للقاعدة
        if self.db.execute_query(
            "INSERT INTO suppliers (name, phone, address, notes, debt_syp, debt_usd) VALUES (?, ?, ?, ?, ?, ?)",
            (name, phone, address, notes, debt_syp, debt_usd)
        ):
            messagebox.showinfo("نجاح", "تمت إضافة المورد بنجاح")
            self.clear_fields()
            self.load_suppliers()
        else:
            messagebox.showerror("خطأ", "فشل في إضافة المورد")
    
    def update_supplier(self):
        """تحديث مورد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار مورد للتحديث")
            return
        
        supplier_id = self.tree.item(selected[0])['values'][0]
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip()
        notes = self.notes_text.get('1.0', 'end-1c').strip()
        
        try:
            debt_syp = float(self.debt_syp_entry.get() or 0)
            debt_usd = float(self.debt_usd_entry.get() or 0)
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة للديون")
            return
        
        if not name:
            messagebox.showerror("خطأ", "يرجى إدخال اسم المورد")
            return
        
        # تحديث في القاعدة
        if self.db.execute_query(
            "UPDATE suppliers SET name = ?, phone = ?, address = ?, notes = ?, debt_syp = ?, debt_usd = ? WHERE id = ?",
            (name, phone, address, notes, debt_syp, debt_usd, supplier_id)
        ):
            messagebox.showinfo("نجاح", "تم تحديث المورد بنجاح")
            self.clear_fields()
            self.load_suppliers()
        else:
            messagebox.showerror("خطأ", "فشل في تحديث المورد")
    
    def delete_supplier(self):
        """حذف مورد"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("خطأ", "يرجى اختيار مورد للحذف")
            return
        
        supplier_id = self.tree.item(selected[0])['values'][0]
        
        # تأكيد الحذف
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا المورد؟"):
            if self.db.execute_query("DELETE FROM suppliers WHERE id = ?", (supplier_id,)):
                messagebox.showinfo("نجاح", "تم حذف المورد بنجاح")
                self.clear_fields()
                self.load_suppliers()
            else:
                messagebox.showerror("خطأ", "فشل في حذف المورد")
    
    def on_select(self, event):
        """عند اختيار مورد من الجدول"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            
            # جلب جميع البيانات
            supplier = self.db.fetch_one("SELECT * FROM suppliers WHERE id = ?", (values[0],))
            if supplier:
                self.name_entry.delete(0, 'end')
                self.name_entry.insert(0, supplier[1])
                
                self.phone_entry.delete(0, 'end')
                self.phone_entry.insert(0, supplier[2] if supplier[2] else '')
                
                self.address_entry.delete(0, 'end')
                self.address_entry.insert(0, supplier[3] if supplier[3] else '')
                
                self.notes_text.delete('1.0', 'end')
                self.notes_text.insert('1.0', supplier[4] if supplier[4] else '')
                
                self.debt_syp_entry.delete(0, 'end')
                self.debt_syp_entry.insert(0, str(supplier[5]))
                
                self.debt_usd_entry.delete(0, 'end')
                self.debt_usd_entry.insert(0, str(supplier[6]))
    
    def clear_fields(self):
        """مسح الحقول"""
        self.name_entry.delete(0, 'end')
        self.phone_entry.delete(0, 'end')
        self.address_entry.delete(0, 'end')
        self.notes_text.delete('1.0', 'end')
        self.debt_syp_entry.delete(0, 'end')
        self.debt_syp_entry.insert(0, '0')
        self.debt_usd_entry.delete(0, 'end')
        self.debt_usd_entry.insert(0, '0')
        # إلغاء التحديد
        for item in self.tree.selection():
            self.tree.selection_remove(item)
