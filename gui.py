import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from iris_engine import extract_iris_code
from iris_db import IrisDB

db = IrisDB()

# ─────────────────────────────
# FUNCTIONS
# ─────────────────────────────

def register():
    path = filedialog.askopenfilename()
    if not path:
        return

    name = reg_name.get().strip()
    if not name:
        messagebox.showerror("Hata", "İsim giriniz")
        return

    code = extract_iris_code(path)

    if code is None:
        messagebox.showerror("Hata", "İris çıkarılamadı")
        return

    db.add(name, code)
    messagebox.showinfo("Başarılı", f"{name} kaydedildi")


def identify():
    path = filedialog.askopenfilename()
    if not path:
        return

    code = extract_iris_code(path)
    name, score = db.identify(code)

    if name:
        result_var.set(f"✔ {name} bulundu | skor: {score:.3f}")
    else:
        result_var.set("✖ Eşleşme yok")


# ─────────────────────────────
# UI
# ─────────────────────────────

root = tk.Tk()
root.title("Iris Recognition System")
root.geometry("500x350")
root.configure(bg="#0f1116")

style = ttk.Style()
style.theme_use("default")

# Notebook (sekmeler)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# ─────────────────────────────
# TAB 1 - REGISTER
# ─────────────────────────────
tab1 = tk.Frame(notebook, bg="#0f1116")
notebook.add(tab1, text="Kayıt (Register)")

tk.Label(tab1, text="İsim Gir", fg="white", bg="#0f1116",
         font=("Arial", 12)).pack(pady=10)

reg_name = tk.Entry(tab1, font=("Arial", 12))
reg_name.pack(pady=5)

tk.Button(tab1,
          text="📂 Görsel Seç ve Kaydet",
          command=register,
          bg="#1f6feb",
          fg="white",
          font=("Arial", 11)).pack(pady=20)

# ─────────────────────────────
# TAB 2 - IDENTIFY
# ─────────────────────────────
tab2 = tk.Frame(notebook, bg="#0f1116")
notebook.add(tab2, text="Tanıma (Identify)")

tk.Button(tab2,
          text="📂 Görsel Seç ve Tanı",
          command=identify,
          bg="#238636",
          fg="white",
          font=("Arial", 11)).pack(pady=20)

result_var = tk.StringVar()
tk.Label(tab2,
         textvariable=result_var,
         fg="white",
         bg="#0f1116",
         font=("Arial", 12, "bold")).pack(pady=10)

# ─────────────────────────────
# TAB 3 - INFO (sunumluk)
# ─────────────────────────────
tab3 = tk.Frame(notebook, bg="#0f1116")
notebook.add(tab3, text="Bilgi")

info_text = """
IRIS RECOGNITION SYSTEM

• Kayıt: Göz görüntüsünden iris kodu çıkarılır
• Tanıma: Hamming distance ile karşılaştırma yapılır
• Kullanılan yöntem: Daugman tabanlı iris kodlama

Adımlar:
1. Görsel seç
2. Iris feature çıkarılır
3. Veritabanına kaydedilir
4. Yeni görüntü ile karşılaştırılır
"""

tk.Label(tab3,
         text=info_text,
         fg="white",
         bg="#0f1116",
         justify="left",
         font=("Consolas", 10)).pack(padx=10, pady=10)

root.mainloop()