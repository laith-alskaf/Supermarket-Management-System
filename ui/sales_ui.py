import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pytz
import traceback

# ملف محسّن لواجهة نقطة البيع (SalesUI)
# تحسينات رئيسية:
# - منطقة محتوى قابلة للتمرير تدعم عجلة الفأرة على ويندوز/ماك/لينكس
# - حوارات مدروسة بحجم مناسب ومركزّة على الشاشة
# - تحقق من المدخلات، رسائل خطأ مفهومة، وتنسيق الأرقام
# - تفعيل جميع الأزرار (حذف، تعديل كمية، مسح، إتمام البيع)
# - اختصارات لوحة مفاتيح: Delete لحذف المحدد من السلة، Ctrl+L لمسح السلة، Enter لإضافة من الحوار
# - تعامل آمن مع قاعدة البيانات مع دوال "safe_"


class SalesUI:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cart = []
        try:
            self.syria_tz = pytz.timezone('Asia/Damascus')
        except Exception:
            self.syria_tz = pytz.utc

        # عناصر ستتم تهيئتها في setup
        self.products_tree = None
        self.cart_tree = None
        self.search_entry = None
        self.discount_syp_entry = None
        self.discount_usd_entry = None
        self.total_syp_label = None
        self.total_usd_label = None
        self.payment_var = tk.StringVar(value='نقدي')
        self.notes_text = None

        self.setup_ui()

    # ------------------ أدوات مساعدة ------------------
    def safe_fetch_all(self, query, params=()):
        if not self.db:
            return []
        try:
            return self.db.fetch_all(query, params) or []
        except Exception:
            traceback.print_exc()
            return []

    def safe_fetch_one(self, query, params=()):
        if not self.db:
            return None
        try:
            return self.db.fetch_one(query, params)
        except Exception:
            traceback.print_exc()
            return None

    def safe_execute(self, query, params=()):
        if not self.db:
            return False
        try:
            return self.db.execute_query(query, params)
        except Exception:
            traceback.print_exc()
            return False

    def fmt(self, value):
        try:
            return f"{float(value):,.2f}"
        except Exception:
            return str(value)

    # ------------------ الواجهة والتمرير ------------------
    def setup_ui(self):
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill='both', expand=True)

        # Canvas قابل للتمرير
        self.canvas = tk.Canvas(main_container, highlightthickness=0)
        v_scroll = ttk.Scrollbar(main_container, orient='vertical', command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.canvas.configure(yscrollcommand=v_scroll.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')

        # ضبط التمرير والتوافق عبر الأنظمة
        def _on_frame_config(event):
            try:
                self.canvas.configure(scrollregion=self.canvas.bbox('all'))
            except Exception:
                pass

        self.inner.bind('<Configure>', _on_frame_config)

        def _on_canvas_resize(event):
            try:
                self.canvas.itemconfigure(self.inner_id, width=event.width)
            except Exception:
                pass

        self.canvas.bind('<Configure>', _on_canvas_resize)

        def _on_mousewheel(event):
            # windows/mac -> event.delta ; linux -> Button-4/5
            if getattr(event, 'delta', None):
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            elif getattr(event, 'num', None):
                if event.num == 4:
                    self.canvas.yview_scroll(-1, 'units')
                elif event.num == 5:
                    self.canvas.yview_scroll(1, 'units')

        self.canvas.bind_all('<MouseWheel>', _on_mousewheel)
        self.canvas.bind_all('<Button-4>', _on_mousewheel)
        self.canvas.bind_all('<Button-5>', _on_mousewheel)

        # بناء المحتوى
        self.setup_content()

        # اختصارات لوحة مفاتيح
        self.parent.bind_all('<Delete>', lambda e: self.remove_from_cart())
        self.parent.bind_all('<Control-l>', lambda e: self.clear_cart())

    # ------------------ محتوى الواجهة ------------------
    def setup_content(self):
        # Header
        header_frame = ttk.Frame(self.inner)
        header_frame.pack(fill='x', padx=12, pady=12)

        ttk.Label(header_frame, text='💰 نظام نقطة البيع (POS)', font=('Arial', 18, 'bold')).pack(side='right')

        controls = ttk.Frame(header_frame)
        controls.pack(side='left')

        ttk.Button(controls, text='🔄 تحديث', command=self.load_products).pack(side='left', padx=6)
        ttk.Button(controls, text='📋 الكل', command=self.show_all_products).pack(side='left', padx=6)

        # المحتوى الرئيسى (منتجات + سلة)
        content_frame = ttk.Frame(self.inner)
        content_frame.pack(fill='both', expand=True, padx=12, pady=6)

        products_container = ttk.Frame(content_frame)
        products_container.pack(side='right', fill='both', expand=True, padx=(6, 4))

        cart_container = ttk.Frame(content_frame, width=380)
        cart_container.pack(side='left', fill='y', padx=(4, 6))

        # اقسام
        self.setup_products_section(products_container)
        self.setup_cart_section(cart_container)

        # تحديث إحصائيات صغيرة
        self.update_stats()

    # ------------------ قسم المنتجات ------------------
    def setup_products_section(self, parent):
        frame = ttk.LabelFrame(parent, text='🛍️ المنتجات المتاحة', padding=10)
        frame.pack(fill='both', expand=True)

        controls = ttk.Frame(frame)
        controls.pack(fill='x', pady=(0, 8))

        search_group = ttk.Frame(controls)
        search_group.pack(side='right', fill='x', expand=True)

        ttk.Label(search_group, text='🔍 بحث سريع:', font=('Arial', 11)).pack(side='right', padx=6)
        self.search_entry = ttk.Entry(search_group, font=('Arial', 11))
        self.search_entry.pack(side='right', fill='x', expand=True, padx=6)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_products())

        btn_group = ttk.Frame(controls)
        btn_group.pack(side='left')
        ttk.Button(btn_group, text='🔄 تحديث', command=self.load_products).pack(side='left', padx=4)
        ttk.Button(btn_group, text='📋 الكل', command=self.show_all_products).pack(side='left', padx=4)

        # جدول المنتجات
        table_container = ttk.Frame(frame)
        table_container.pack(fill='both', expand=True)

        columns = ('id', 'name', 'price_syp', 'price_usd', 'quantity')
        self.products_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=18)
        cols_cfg = [
            ('id', 'الرقم', 80),
            ('name', 'اسم المنتج', 300),
            ('price_syp', 'السعر (ل.س)', 140),
            ('price_usd', 'السعر ($)', 110),
            ('quantity', 'المخزون', 100)
        ]
        for col, txt, w in cols_cfg:
            self.products_tree.heading(col, text=txt)
            self.products_tree.column(col, width=w, anchor='center')

        y_scroll = ttk.Scrollbar(table_container, orient='vertical', command=self.products_tree.yview)
        x_scroll = ttk.Scrollbar(table_container, orient='horizontal', command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.products_tree.pack(side='top', fill='both', expand=True)
        y_scroll.pack(side='right', fill='y')
        x_scroll.pack(side='bottom', fill='x')

        # تفعيل إضافة عبر نقرة مزدوجة أو Enter
        self.products_tree.bind('<Double-1>', self.add_to_cart)
        self.products_tree.bind('<Return>', self.add_to_cart)

        ttk.Label(frame, text='💡 انقر نقراً مزدوجاً على المنتج لإضافته إلى السلة', font=('Arial', 10, 'italic'), foreground='#666').pack(pady=8)

        # تحميل البيانات
        self.load_products()

    # ------------------ قسم السلة ------------------
    def setup_cart_section(self, parent):
        frame = ttk.LabelFrame(parent, text='🛒 سلة المشتريات', padding=8)
        frame.pack(fill='both', expand=True)

        # شجرة السلة
        tbl_cont = ttk.Frame(frame)
        tbl_cont.pack(fill='both', expand=True)

        cols = ('product_id', 'name', 'quantity', 'price_syp', 'price_usd', 'total_syp', 'total_usd')
        self.cart_tree = ttk.Treeview(tbl_cont, columns=cols, show='headings', height=12)
        cart_cols = [
            ('product_id', '#', 50),
            ('name', 'المنتج', 160),
            ('quantity', 'الكمية', 80),
            ('price_syp', 'سعر الوحدة (ل.س)', 110),
            ('price_usd', 'سعر الوحدة ($)', 100),
            ('total_syp', 'الإجمالي (ل.س)', 120),
            ('total_usd', 'الإجمالي ($)', 110)
        ]
        for col, txt, w in cart_cols:
            self.cart_tree.heading(col, text=txt)
            self.cart_tree.column(col, width=w, anchor='center')

        y_scroll = ttk.Scrollbar(tbl_cont, orient='vertical', command=self.cart_tree.yview)
        x_scroll = ttk.Scrollbar(tbl_cont, orient='horizontal', command=self.cart_tree.xview)
        self.cart_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.cart_tree.pack(side='top', fill='both', expand=True)
        y_scroll.pack(side='right', fill='y')
        x_scroll.pack(side='bottom', fill='x')

        # أزرار التحكم
        controls = ttk.Frame(frame)
        controls.pack(fill='x', pady=8)

        ttk.Button(controls, text='🗑️ حذف المحدد', command=self.remove_from_cart).pack(side='right', padx=4)
        ttk.Button(controls, text='✏️ تعديل الكمية', command=self.edit_quantity).pack(side='right', padx=4)
        ttk.Button(controls, text='🧹 مسح السلة', command=self.clear_cart).pack(side='right', padx=4)

        # إجماليات
        totals = ttk.LabelFrame(frame, text='💰 الإجماليات', padding=6)
        totals.pack(fill='x', pady=6)

        syp_row = ttk.Frame(totals)
        syp_row.pack(fill='x', pady=3)
        ttk.Label(syp_row, text='الإجمالي (ل.س):', font=('Arial', 11)).pack(side='right', padx=6)
        self.total_syp_label = ttk.Label(syp_row, text='0.00', font=('Arial', 12, 'bold'))
        self.total_syp_label.pack(side='right', padx=6)

        usd_row = ttk.Frame(totals)
        usd_row.pack(fill='x', pady=3)
        ttk.Label(usd_row, text='الإجمالي (دولار):', font=('Arial', 11)).pack(side='right', padx=6)
        self.total_usd_label = ttk.Label(usd_row, text='0.00', font=('Arial', 12, 'bold'))
        self.total_usd_label.pack(side='right', padx=6)

        # خصومات
        disc = ttk.LabelFrame(frame, text='🎁 الخصومات', padding=6)
        disc.pack(fill='x', pady=6)
        drow = ttk.Frame(disc)
        drow.pack(fill='x')
        ttk.Label(drow, text='خصم (ل.س):').pack(side='right', padx=6)
        self.discount_syp_entry = ttk.Entry(drow, width=12)
        self.discount_syp_entry.insert(0, '0')
        self.discount_syp_entry.pack(side='right', padx=6)
        self.discount_syp_entry.bind('<KeyRelease>', lambda e: self.update_totals())

        ttk.Label(drow, text='خصم ($):').pack(side='right', padx=6)
        self.discount_usd_entry = ttk.Entry(drow, width=12)
        self.discount_usd_entry.insert(0, '0')
        self.discount_usd_entry.pack(side='right', padx=6)
        self.discount_usd_entry.bind('<KeyRelease>', lambda e: self.update_totals())

        # إعدادات البيع
        settings = ttk.LabelFrame(frame, text='⚙️ إعدادات البيع', padding=6)
        settings.pack(fill='x', pady=6)
        pay_row = ttk.Frame(settings)
        pay_row.pack(fill='x')
        ttk.Label(pay_row, text='طريقة الدفع:').pack(side='right', padx=6)
        payment_combo = ttk.Combobox(pay_row, textvariable=self.payment_var, values=['نقدي', 'بطاقة ائتمان', 'تحويل بنكي', 'آجل'], state='readonly', width=18)
        payment_combo.pack(side='right', padx=6)

        notes_row = ttk.Frame(settings)
        notes_row.pack(fill='x', pady=6)
        ttk.Label(notes_row, text='ملاحظات:').pack(side='right', padx=6)
        self.notes_text = tk.Text(notes_row, height=4, width=30)
        self.notes_text.pack(side='right', fill='x', expand=True, padx=6)

        # أزرار الإجراء
        action_row = ttk.Frame(frame)
        action_row.pack(fill='x', pady=8)
        ttk.Button(action_row, text='✅ إتمام عملية البيع', command=self.complete_sale, style='success.TButton').pack(side='right')

    # ------------------ وظائف تحميل/بحث ------------------
    def load_products(self):
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)

        rows = self.safe_fetch_all(
            """
            SELECT id, name, selling_price_syp, selling_price_usd, quantity
            FROM products
            ORDER BY name
            """
        )
        for r in rows:
            # تأكد من وجود القيم
            if r and len(r) >= 5:
                self.products_tree.insert('', 'end', values=r)
        self.update_stats()

    def show_all_products(self):
        self.search_entry.delete(0, 'end')
        self.load_products()

    def search_products(self):
        term = self.search_entry.get().strip()
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        if term == '':
            self.load_products()
            return
        rows = self.safe_fetch_all(
            """
            SELECT id, name, selling_price_syp, selling_price_usd, quantity
            FROM products
            WHERE name LIKE ?
            ORDER BY name
            """,
            (f'%{term}%',)
        )
        for r in rows:
            if r and len(r) >= 5:
                self.products_tree.insert('', 'end', values=r)
        self.update_stats()

    # ------------------ إضافة وإدارة السلة ------------------
    def add_to_cart(self, event=None):
        sel = self.products_tree.selection()
        if not sel:
            messagebox.showwarning('تنبيه', '⚠️ يرجى اختيار منتج من القائمة')
            return
        try:
            vals = self.products_tree.item(sel[0])['values']
            product_id, name, price_syp, price_usd, available_qty = vals
            # تحويل أنواع مع التحقق
            try:
                product_id = int(product_id)
                price_syp = float(price_syp)
                price_usd = float(price_usd)
                available_qty = float(available_qty)
            except Exception:
                messagebox.showerror('خطأ', 'بيانات المنتج غير صالحة')
                return

            # حوار الكمية
            dlg = tk.Toplevel(self.parent)
            dlg.transient(self.parent)
            dlg.grab_set()
            dlg.title('إضافة إلى السلة')

            frm = ttk.Frame(dlg, padding=12)
            frm.pack(fill='both', expand=True)

            ttk.Label(frm, text=f"المنتج: {name}", font=('Arial', 12, 'bold')).pack(anchor='e')
            ttk.Label(frm, text=f"السعر: {self.fmt(price_syp)} ل.س / {self.fmt(price_usd)} $").pack(anchor='e', pady=(0,8))
            ttk.Label(frm, text=f"المخزون المتاح: {self.fmt(available_qty)}").pack(anchor='e', pady=(0,8))

            q_frame = ttk.Frame(frm)
            q_frame.pack(fill='x', pady=8)
            ttk.Label(q_frame, text='الكمية:').pack(side='right', padx=6)
            qty_var = tk.StringVar(value='1')
            qty_entry = ttk.Entry(q_frame, textvariable=qty_var, width=12, justify='center')
            qty_entry.pack(side='right', padx=6)
            qty_entry.focus()

            def confirm():
                try:
                    q = float(qty_var.get())
                    if q <= 0:
                        raise ValueError('الكمية يجب أن تكون أكبر من الصفر')
                    if q > available_qty:
                        messagebox.showerror('خطأ', f'الكمية المتاحة فقط: {available_qty}')
                        return
                    total_syp = q * price_syp
                    total_usd = q * price_usd
                    item = {
                        'product_id': product_id,
                        'name': name,
                        'quantity': q,
                        'unit_price_syp': price_syp,
                        'unit_price_usd': price_usd,
                        'total_syp': total_syp,
                        'total_usd': total_usd
                    }
                    self.cart.append(item)
                    self.update_cart_display()
                    dlg.destroy()
                    messagebox.showinfo('تم', f"تمت إضافة '{name}' إلى السلة")
                except ValueError as ve:
                    messagebox.showerror('خطأ', str(ve))
                    qty_entry.focus()
                except Exception as e:
                    traceback.print_exc()
                    messagebox.showerror('خطأ', 'حدث خطأ أثناء إضافة المنتج')

            btns = ttk.Frame(frm)
            btns.pack(fill='x', pady=6)
            ttk.Button(btns, text='✅ إضافة', command=confirm, style='success.TButton').pack(side='right', padx=6)
            ttk.Button(btns, text='❌ إلغاء', command=dlg.destroy).pack(side='right')

            # مفاتيح تأكيد/إلغاء
            qty_entry.bind('<Return>', lambda e: confirm())
            dlg.bind('<Escape>', lambda e: dlg.destroy())

            # ضبط حجم وموقع الحوار
            dlg.update_idletasks()
            w = 460
            h = 320
            x = (dlg.winfo_screenwidth() - w) // 2
            y = (dlg.winfo_screenheight() - h) // 2
            dlg.geometry(f"{w}x{h}+{x}+{y}")

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror('خطأ', f'حدث خطأ: {e}')

    def update_cart_display(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)
        for it in self.cart:
            self.cart_tree.insert('', 'end', values=(
                it['product_id'], it['name'], f"{it['quantity']:.2f}", self.fmt(it['unit_price_syp']), self.fmt(it['unit_price_usd']), self.fmt(it['total_syp']), self.fmt(it['total_usd'])
            ))
        self.update_totals()
        self.update_stats()

    def update_totals(self):
        total_syp = sum(item['total_syp'] for item in self.cart)
        total_usd = sum(item['total_usd'] for item in self.cart)
        try:
            discount_syp = float(self.discount_syp_entry.get() or 0)
        except Exception:
            discount_syp = 0
        try:
            discount_usd = float(self.discount_usd_entry.get() or 0)
        except Exception:
            discount_usd = 0
        final_syp = max(0, total_syp - discount_syp)
        final_usd = max(0, total_usd - discount_usd)
        self.total_syp_label.config(text=self.fmt(final_syp))
        self.total_usd_label.config(text=self.fmt(final_usd))

    def remove_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning('تنبيه', 'يرجى اختيار عنصر من السلة')
            return
        idx = self.cart_tree.index(sel[0])
        if 0 <= idx < len(self.cart):
            removed = self.cart.pop(idx)
            self.update_cart_display()
            messagebox.showinfo('تم', f"تم حذف '{removed['name']}' من السلة")

    def clear_cart(self):
        if not self.cart:
            messagebox.showinfo('معلومة', 'السلة فارغة بالفعل')
            return
        if messagebox.askyesno('تأكيد', 'هل تريد مسح السلة بالكامل؟'):
            self.cart.clear()
            self.update_cart_display()

    def edit_quantity(self):
        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showwarning('تنبيه', 'يرجى اختيار عنصر لتعديله')
            return
        idx = self.cart_tree.index(sel[0])
        item = self.cart[idx]

        dlg = tk.Toplevel(self.parent)
        dlg.transient(self.parent)
        dlg.grab_set()
        dlg.title('تعديل الكمية')

        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text=f"المنتج: {item['name']}", font=('Arial', 12)).pack(anchor='e')
        ttk.Label(frm, text=f"الموجود حالياً في السلة: {item['quantity']}").pack(anchor='e', pady=(0,6))

        qvar = tk.StringVar(value=f"{item['quantity']:.2f}")
        qentry = ttk.Entry(frm, textvariable=qvar, width=12, justify='center')
        qentry.pack(pady=8)
        qentry.focus()

        def apply_change():
            try:
                new_q = float(qvar.get())
                if new_q <= 0:
                    raise ValueError('الكمية يجب أن تكون أكبر من الصفر')
                # (اختياري) التحقق من المخزون بقيام استعلام للمنتج
                row = self.safe_fetch_one('SELECT quantity FROM products WHERE id = ?', (item['product_id'],))
                if row and row[0] is not None and new_q > float(row[0]):
                    messagebox.showerror('خطأ', f'الكمية المتاحة فقط: {row[0]}')
                    return
                item['quantity'] = new_q
                item['total_syp'] = new_q * item['unit_price_syp']
                item['total_usd'] = new_q * item['unit_price_usd']
                self.update_cart_display()
                dlg.destroy()
            except ValueError as ve:
                messagebox.showerror('خطأ', str(ve))
                qentry.focus()
            except Exception:
                traceback.print_exc()
                messagebox.showerror('خطأ', 'حدث خطأ أثناء تعديل الكمية')

        btns = ttk.Frame(frm)
        btns.pack(fill='x')
        ttk.Button(btns, text='✓ تطبيق', command=apply_change).pack(side='right', padx=6)
        ttk.Button(btns, text='إلغاء', command=dlg.destroy).pack(side='right')

        qentry.bind('<Return>', lambda e: apply_change())
        dlg.bind('<Escape>', lambda e: dlg.destroy())

        dlg.update_idletasks()
        w, h = 420, 220
        x = (dlg.winfo_screenwidth() - w) // 2
        y = (dlg.winfo_screenheight() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------ إحصائيات ومساعدة ------------------
    def update_stats(self):
        try:
            products_count = len(self.products_tree.get_children()) if self.products_tree else 0
            cart_count = len(self.cart)
            # تحديث العناوين البسيطة إن وُجدت
            # (نبحث في الواجهة عن المكان الصحيح) - محاولة مرنة
            try:
                header_children = self.inner.winfo_children()[0].winfo_children()
                # header_children[1] يحتمل أن يكون إطار التحكم الذي يحتوي على الإحصائيات
                # إذا فشل هذا الافتراض فلا نكسر التطبيق
                # لذا نلتزم فقط بتحديث الواجهة الداخلية للسلة
            except Exception:
                pass
        except Exception:
            pass

    # ------------------ إتمام البيع ------------------
    def complete_sale(self):
        if not self.cart:
            messagebox.showerror('خطأ', 'لا يمكن إتمام البيع - السلة فارغة')
            return
        try:
            discount_syp = float(self.discount_syp_entry.get() or 0)
        except Exception:
            messagebox.showerror('خطأ', 'قيمة خصم غير صحيحة (ل.س)')
            return
        try:
            discount_usd = float(self.discount_usd_entry.get() or 0)
        except Exception:
            messagebox.showerror('خطأ', 'قيمة خصم غير صحيحة ($)')
            return

        total_syp = sum(item['total_syp'] for item in self.cart) - discount_syp
        total_usd = sum(item['total_usd'] for item in self.cart) - discount_usd

        payment_method = self.payment_var.get()
        notes = self.notes_text.get('1.0', 'end-1c').strip()

        # حفظ البيع في قاعدة البيانات
        if not self.safe_execute(
            """
            INSERT INTO sales (total_syp, total_usd, payment_method, discount_syp, discount_usd, notes, sale_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (total_syp, total_usd, payment_method, discount_syp, discount_usd, notes, datetime.now(self.syria_tz).isoformat())
        ):
            messagebox.showerror('خطأ', 'فشل في تسجيل عملية البيع')
            return

        try:
            sale_id = self.db.cursor.lastrowid if hasattr(self.db, 'cursor') else None
            # حفظ عناصر البيع وتحديث المخزون
            for item in self.cart:
                self.safe_execute(
                    """
                    INSERT INTO sale_items (sale_id, product_id, product_name, quantity, unit_price_syp, unit_price_usd, subtotal_syp, subtotal_usd)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (sale_id, item['product_id'], item['name'], item['quantity'], item['unit_price_syp'], item['unit_price_usd'], item['total_syp'], item['total_usd'])
                )
                # تحديث المخزون
                self.safe_execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (item['quantity'], item['product_id']))
                # تسجيل حركة المخزون
                self.safe_execute("INSERT INTO inventory_movements (product_id, movement_type, quantity, reason, moved_at) VALUES (?, 'out', ?, 'بيع', ?)", (item['product_id'], item['quantity'], datetime.now(self.syria_tz).isoformat()))

            messagebox.showinfo('تم', f'تم تسجيل البيع بنجاح\nرقم الفاتورة: {sale_id or "-"}')

            # إعادة تهيئة النموذج
            self.cart.clear()
            self.update_cart_display()
            self.discount_syp_entry.delete(0, 'end'); self.discount_syp_entry.insert(0, '0')
            self.discount_usd_entry.delete(0, 'end'); self.discount_usd_entry.insert(0, '0')
            self.notes_text.delete('1.0', 'end')
            self.load_products()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror('خطأ', f'حدث خطأ أثناء حفظ عناصر البيع: {e}')

# نهاية الملف
