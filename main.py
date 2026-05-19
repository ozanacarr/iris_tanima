import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from iris_db import IrisDB
from iris_engine import extract_iris_code

db = IrisDB()


class IrisApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Iris Tanıma ve Yönetim Sistemi")
        self.root.geometry("800x550")
        self.root.configure(bg="#F4F6F9")  # Açık gri modern arka plan

        # Modern Tema Tasarımı (Stiller)
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Notebook (Sekme) Tasarımı
        self.style.configure(
            "TNotebook", background="#F4F6F9", borderwidth=0
        )
        self.style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 11, "bold"),
            padding=[20, 8],
            background="#E0E6ED",
            foreground="#4A5568",
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#4A90E2")],
            foreground=[("selected", "white")],
        )

        # Kart/Gövde Tasarımı
        self.style.configure("TFrame", background="#FFFFFF")

        # Giriş Alanı Tasarımı
        self.style.configure(
            "TEntry", font=("Segoe UI", 11), padding=6, borderwidth=1
        )

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        # Tabs (Modern Kart Yapısı İçinde)
        self.tab_register = ttk.Frame(self.notebook, style="TFrame")
        self.tab_identify = ttk.Frame(self.notebook, style="TFrame")
        self.tab_users = ttk.Frame(self.notebook, style="TFrame")

        self.notebook.add(self.tab_register, text=" 📥 Kayıt Ol ")
        self.notebook.add(self.tab_identify, text=" 🔍 İris Tanıma ")
        self.notebook.add(self.tab_users, text=" 👥 Kullanıcı Yönetimi ")

        self.build_register()
        self.build_identify()
        self.build_users()

    # ───────────────────────── REGISTER ─────────────────────────
    def build_register(self):
        frame = self.tab_register

        # Merkezleme için içerik container'ı
        center_frame = tk.Frame(frame, bg="#FFFFFF")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            center_frame,
            text="Yeni İris Kaydı",
            font=("Segoe UI", 18, "bold"),
            fg="#2D3748",
            bg="#FFFFFF",
        ).pack(pady=15)

        tk.Label(
            center_frame,
            text="Kullanıcı Adı",
            font=("Segoe UI", 11),
            fg="#718096",
            bg="#FFFFFF",
        ).pack(anchor="w", padx=5)

        # Standart Entry yerine daha şık görünüm
        self.name_entry = tk.Entry(
            center_frame,
            font=("Segoe UI", 12),
            bg="#F7FAFC",
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightcolor="#4A90E2",
        )
        self.name_entry.pack(fill="x", ipady=6, pady=5)

        # Modern Renkli Buton
        register_btn = tk.Button(
            center_frame,
            text="Göz Görseli Seç ve Kaydet",
            font=("Segoe UI", 11, "bold"),
            bg="#2ECC71",
            fg="white",
            activebackground="#27AE60",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.register,
        )
        register_btn.pack(fill="x", ipady=8, pady=20)

    def register(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Hata", "Lütfen geçerli bir isim girin.")
            return

        code = extract_iris_code(path)
        db.add(name, code)

        messagebox.showinfo("Başarılı", f"{name} sisteme başarıyla kaydedildi.")
        self.name_entry.delete(0, tk.END)  # İşlem sonrası temizlik
        self.refresh_users()

    # ───────────────────────── IDENTIFY ─────────────────────────
    def build_identify(self):
        frame = self.tab_identify

        center_frame = tk.Frame(frame, bg="#FFFFFF")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            center_frame,
            text="Sistemdeki İrisleri Tara",
            font=("Segoe UI", 18, "bold"),
            fg="#2D3748",
            bg="#FFFFFF",
        ).pack(pady=10)

        tk.Label(
            center_frame,
            text="Doğrulama yapmak için bir göz görseli yükleyin.",
            font=("Segoe UI", 11),
            fg="#718096",
            bg="#FFFFFF",
        ).pack(pady=5)

        identify_btn = tk.Button(
            center_frame,
            text="📁 Görsel Seç ve Tanı",
            font=("Segoe UI", 12, "bold"),
            bg="#4A90E2",
            fg="white",
            activebackground="#357ABD",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.identify,
        )
        identify_btn.pack(ipadx=20, ipady=10, pady=25)

        # Sonuç Paneli (Görsel bir kart şeklinde)
        self.result_card = tk.Frame(
            center_frame, bg="#F7FAFC", bd=1, relief="solid", padx=20, pady=15
        )
        self.result_card.pack(fill="x")

        self.result = tk.Label(
            self.result_card,
            text="Sonuç bekleniyor...",
            font=("Segoe UI", 12, "italic"),
            fg="#A0AEC0",
            bg="#F7FAFC",
        )
        self.result.pack()

    def identify(self):
        path = filedialog.askopenfilename()
        if not path:
            return

        code = extract_iris_code(path)
        name, score = db.identify(code)

        if name:
            self.result.config(
                text=f"Eşleşme Başarılı!\nKullanıcı: {name}\nSkor: {score:.3f}",
                font=("Segoe UI", 12, "bold"),
                fg="#27AE60",
            )
        else:
            self.result.config(
                text="Eşleşme Bulunamadı!\nSistemde kayıtlı olmayan iris.",
                font=("Segoe UI", 12, "bold"),
                fg="#E74C3C",
            )

    # ───────────────────────── USERS ─────────────────────────
    def build_users(self):
        frame = self.tab_users

        # Sol taraf Listbox, Sağ taraf Butonlar olacak şekilde grid yapısı
        frame.columnconfigure(0, weight=4)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(0, weight=1)

        # Liste Alanı arka planı ve tasarımı
        list_container = tk.Frame(frame, bg="#FFFFFF", padx=15, pady=15)
        list_container.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            list_container,
            text="Kayıtlı Kullanıcı Listesi",
            font=("Segoe UI", 12, "bold"),
            fg="#2D3748",
            bg="#FFFFFF",
        ).pack(anchor="w", pady=5)

        # Modern Listbox
        self.listbox = tk.Listbox(
            list_container,
            font=("Segoe UI", 11),
            bg="#F7FAFC",
            fg="#2D3748",
            selectbackground="#4A90E2",
            selectforeground="white",
            borderwidth=1,
            relief="solid",
            highlightthickness=0,
            activestyle="none",
        )
        self.listbox.pack(fill="both", expand=True)

        # Sağ Buton Paneli
        btn_frame = tk.Frame(frame, bg="#F4F6F9", padx=15, pady=20)
        btn_frame.grid(row=0, column=1, sticky="nsew")

        # Buton Stilleri ortak fonksiyonu
        def create_action_btn(parent, text, color, hover_color, command):
            return tk.Button(
                parent,
                text=text,
                font=("Segoe UI", 10, "bold"),
                bg=color,
                fg="white",
                activebackground=hover_color,
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                command=command,
            )

        create_action_btn(
            btn_frame, "🔄 Yenile", "#34495E", "#2C3E50", self.refresh_users
        ).pack(fill="x", ipady=8, pady=5)
        create_action_btn(
            btn_frame, "✏️ İsim Değiştir", "#F39C12", "#D35400", self.rename_user
        ).pack(fill="x", ipady=8, pady=5)
        create_action_btn(
            btn_frame, "❌ Kullanıcıyı Sil", "#E74C3C", "#C0392B", self.delete_user
        ).pack(fill="x", ipady=8, pady=5)

        self.refresh_users()

    def refresh_users(self):
        self.listbox.delete(0, tk.END)
        for u in db.list_users():
            self.listbox.insert(tk.END, u)

    def delete_user(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning(
                "Seçim Yapılmadı", "Lütfen silinecek kullanıcıyı seçin."
            )
            return
        name = self.listbox.get(sel[0])

        if messagebox.askyesno(
            "Onay", f"{name} isimli kullanıcıyı silmek istediğinize emin misiniz?"
        ):
            db.delete_user(name)
            self.refresh_users()

    def rename_user(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning(
                "Seçim Yapılmadı", "Lütfen ismi değiştirilecek kullanıcıyı seçin."
            )
            return

        old_name = self.listbox.get(sel[0])

        # Modern Toplevel Pencere Tasarımı
        new_window = tk.Toplevel(self.root)
        new_window.title("İsim Düzenle")
        new_window.geometry("350x180")
        new_window.configure(bg="#FFFFFF")
        new_window.resizable(False, False)

        # Alt pencereyi ana pencereye sabitleme (Modal yapma)
        new_window.transient(self.root)
        new_window.grab_set()

        tk.Label(
            new_window,
            text=f"'{old_name}' için yeni isim:",
            font=("Segoe UI", 11, "bold"),
            fg="#2D3748",
            bg="#FFFFFF",
        ).pack(pady=15)

        entry = tk.Entry(
            new_window,
            font=("Segoe UI", 11),
            bg="#F7FAFC",
            relief="solid",
            bd=1,
        )
        entry.pack(fill="x", padx=30, ipady=4, pady=5)
        entry.insert(0, old_name)
        entry.focus_set()

        def apply():
            new_name = entry.get().strip()
            if not new_name:
                return

            records = db._data.get(old_name, None)
            if records is None:
                return

            db.delete_user(old_name)
            db._data[new_name] = records
            db._save()

            self.refresh_users()
            new_window.destroy()

        tk.Button(
            new_window,
            text="Güncelle",
            font=("Segoe UI", 10, "bold"),
            bg="#2ECC71",
            fg="white",
            relief="flat",
            command=apply,
        ).pack(pady=15, ipadx=15, ipady=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = IrisApp(root)
    root.mainloop()