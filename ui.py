# 📦 Gerekli modüller
import tkinter as tk
from tkinter import filedialog, messagebox
from pdf2image import convert_from_path
from PIL import ImageTk, Image
import PyPDF2
import io
import os

from config import POPPLER_PATH, RESAMPLE_MODE
from utils import parse_page_input, get_unique_filename

# 🔄 Açık önizleme pencerelerini takip etmek için liste
open_previews = []

# 🧹 Tüm açık önizleme pencerelerini kapatır
def close_all_previews():
    global open_previews
    for win in open_previews:
        try:
            win.destroy()
        except:
            pass
    open_previews.clear()

# ⚡ Hızlı önizleme: sadece geçerli sayfayı yükler
def preview_pdf_lazy(parent, input_path=None):
    if not input_path:
        input_path = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
        if not input_path:
            return

    try:
        with open(input_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            total_pages = len(reader.pages)

        win = tk.Toplevel(parent)
        win.title("📖 Hızlı Önizleme")
        win.geometry("600x800")
        win.configure(bg="#ffffff")
        open_previews.append(win)

        img_label = tk.Label(win, bg="#ffffff")
        img_label.pack(pady=10)

        page_num_var = tk.StringVar()
        tk.Label(win, textvariable=page_num_var, bg="#ffffff", font=("Segoe UI", 10)).pack()

        current_index = [0]

        def show_page(index):
            try:
                images = convert_from_path(
                    input_path,
                    dpi=100,
                    first_page=index + 1,
                    last_page=index + 1,
                    poppler_path=POPPLER_PATH
                )
                img = images[0].resize((500, 700), RESAMPLE_MODE)
                tk_img = ImageTk.PhotoImage(img)
                img_label.config(image=tk_img)
                img_label.image = tk_img
                page_num_var.set(f"Sayfa {index + 1} / {total_pages}")
            except Exception as e:
                messagebox.showerror("Hata", f"Sayfa yüklenemedi: {e}")

        def next_page():
            if current_index[0] < total_pages - 1:
                current_index[0] += 1
                show_page(current_index[0])

        def prev_page():
            if current_index[0] > 0:
                current_index[0] -= 1
                show_page(current_index[0])

        nav = tk.Frame(win, bg="#ffffff")
        nav.pack(pady=10)
        tk.Button(nav, text="⬅️ Geri", command=prev_page).pack(side="left", padx=10)
        tk.Button(nav, text="İleri ➡️", command=next_page).pack(side="right", padx=10)

        show_page(current_index[0])
    except Exception as e:
        messagebox.showerror("Hata", f"Önizleme başlatılamadı: {e}")

# 📤 Belirli sayfaları çıkararak yeni PDF oluşturur
def extract_pages(parent):
    close_all_previews()
    input_path = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
    if not input_path:
        return

    preview_pdf_lazy(parent, input_path)

    try:
        with open(input_path, "rb") as infile:
            reader = PyPDF2.PdfReader(infile)
            total_pages = len(reader.pages)
            page_clones = []
            for i in range(total_pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[i])
                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0)
                clone_reader = PyPDF2.PdfReader(buffer)
                page_clones.append(clone_reader.pages[0])
    except Exception as e:
        messagebox.showerror("Hata", f"PDF okunamadı: {e}")
        return

    win = tk.Toplevel(parent)
    win.title("📤 Sayfa Seçimi")
    win.configure(bg="#ffffff")
    win.geometry("400x200")
    x = parent.winfo_x() + parent.winfo_width() + 20
    y = parent.winfo_y()
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text=f"Toplam Sayfa: {total_pages}", bg="#ffffff").pack(pady=(10, 5))
    tk.Label(win, text="Sayfa Numaraları (örn: 2,4,7-9):", bg="#ffffff").pack()
    entry = tk.Entry(win, width=40)
    entry.pack(pady=5)

    def on_confirm():
        selected_pages = parse_page_input(entry.get().strip(), total_pages)
        if not selected_pages:
            messagebox.showerror("Hatalı Giriş", "Geçerli sayfa numarası girilmedi.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not output_path:
            return

        try:
            writer = PyPDF2.PdfWriter()
            for p in selected_pages:
                writer.add_page(page_clones[p - 1])
            output_path = get_unique_filename(output_path)
            with open(output_path, "wb") as outfile:
                writer.write(outfile)
            messagebox.showinfo("Başarılı", f"{output_path} oluşturuldu.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Sayfalar çıkarılamadı: {e}")

    tk.Button(win, text="✅ Sayfaları Çıkar", command=on_confirm, bg="#4CAF50", fg="white").pack(pady=10)

# 🗑️ Belirli sayfaları silerek yeni PDF oluşturur
def delete_pages(parent):
    close_all_previews()
    input_path = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
    if not input_path:
        return

    preview_pdf_lazy(parent, input_path)

    try:
        with open(input_path, "rb") as infile:
            reader = PyPDF2.PdfReader(infile)
            total_pages = len(reader.pages)
            page_clones = []
            for i in range(total_pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[i])
                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0)
                clone_reader = PyPDF2.PdfReader(buffer)
                page_clones.append(clone_reader.pages[0])
    except Exception as e:
        messagebox.showerror("Hata", f"PDF okunamadı: {e}")
        return

    win = tk.Toplevel(parent)
    win.title("🗑️ Sayfa Sil")
    win.configure(bg="#ffffff")
    win.geometry("400x200")
    x = parent.winfo_x() + parent.winfo_width() + 20
    y = parent.winfo_y()
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text=f"Toplam Sayfa: {total_pages}", bg="#ffffff").pack(pady=(10, 5))
    tk.Label(win, text="Silinecek Sayfalar (örn: 1,3,5-6):", bg="#ffffff").pack()
    entry = tk.Entry(win, width=40)
    entry.pack(pady=5)

    def on_confirm():
        to_delete = parse_page_input(entry.get().strip(), total_pages)
        if not to_delete:
            messagebox.showerror("Hatalı Giriş", "Geçerli sayfa numarası girilmedi.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not output_path:
            return

        try:
            writer = PyPDF2.PdfWriter()
            for i in range(total_pages):
                if (i + 1) not in to_delete:
                    writer.add_page(page_clones[i])
            output_path = get_unique_filename(output_path)
            with open(output_path, "wb") as out:
                writer.write(out)
            messagebox.showinfo("Başarılı", f"{len(to_delete)} sayfa silindi.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Sayfa silme başarısız: {e}")

    tk.Button(win, text="✅ Sayfaları Sil", command=on_confirm, bg="#E91E63", fg="white").pack(pady=10)

def split_pdf(parent):
    close_all_previews()
    input_path = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
    if not input_path:
        return

    preview_pdf_lazy(parent, input_path)

    try:
        with open(input_path, "rb") as infile:
            reader = PyPDF2.PdfReader(infile)
            total_pages = len(reader.pages)
            page_clones = []
            for i in range(total_pages):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[i])
                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0)
                clone_reader = PyPDF2.PdfReader(buffer)
                page_clones.append(clone_reader.pages[0])
    except Exception as e:
        messagebox.showerror("Hata", f"PDF okunamadı: {e}")
        return

    win = tk.Toplevel(parent)
    win.title("✂️ PDF Böl")
    win.configure(bg="#ffffff")
    win.geometry("400x200")
    x = parent.winfo_x() + parent.winfo_width() + 20
    y = parent.winfo_y()
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text=f"Toplam Sayfa: {total_pages}", bg="#ffffff").pack(pady=(10, 5))
    tk.Label(win, text="Kaç sayfada bir bölünsün?", bg="#ffffff").pack()
    entry = tk.Entry(win, width=10)
    entry.pack(pady=5)

    def on_confirm():
        try:
            chunk_size = int(entry.get())
            if chunk_size < 1:
                raise ValueError
        except:
            messagebox.showerror("Hatalı Giriş", "Geçerli bir sayı girin.")
            return

        output_dir = filedialog.askdirectory(title="Parçaları Kaydet")
        if not output_dir:
            return

        try:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            for i in range(0, total_pages, chunk_size):
                writer = PyPDF2.PdfWriter()
                for j in range(i, min(i + chunk_size, total_pages)):
                    writer.add_page(page_clones[j])
                part_num = (i // chunk_size) + 1
                raw_path = os.path.join(output_dir, f"{base_name}_parca_{part_num}.pdf")
                output_path = get_unique_filename(raw_path)
                with open(output_path, "wb") as out:
                    writer.write(out)
            messagebox.showinfo("Başarılı", f"{total_pages} sayfa {chunk_size}'lik parçalara ayrıldı.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Bölme işlemi başarısız: {e}")

    tk.Button(win, text="✅ PDF'yi Böl", command=on_confirm, bg="#FF5722", fg="white").pack(pady=10)

def merge_pdfs(parent):
    close_all_previews()
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF Dosyaları", "*.pdf")])
    if not file_paths:
        return

    win = tk.Toplevel(parent)
    win.title("📚 PDF Birleştir – Sıralama")
    win.geometry("500x400")
    win.configure(bg="#ffffff")
    x = parent.winfo_x() + parent.winfo_width() + 20
    y = parent.winfo_y()
    win.geometry(f"+{x}+{y}")

    tk.Label(win, text="Seçilen Dosyalar (↑ ↓ ile sıralayın):", bg="#ffffff", font=("Segoe UI", 10, "bold")).pack(pady=(10, 5))

    listbox = tk.Listbox(win, selectmode=tk.SINGLE, width=60, height=10)
    for path in file_paths:
        listbox.insert(tk.END, path)
    listbox.pack(pady=5)

    def move_up():
        idx = listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        item = listbox.get(i)
        listbox.delete(i)
        listbox.insert(i - 1, item)
        listbox.select_set(i - 1)

    def move_down():
        idx = listbox.curselection()
        if not idx or idx[0] == listbox.size() - 1:
            return
        i = idx[0]
        item = listbox.get(i)
        listbox.delete(i)
        listbox.insert(i + 1, item)
        listbox.select_set(i + 1)

    def on_merge():
        ordered_paths = list(listbox.get(0, tk.END))
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not output_path:
            return

        try:
            writer = PyPDF2.PdfWriter()
            for path in ordered_paths:
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        writer.add_page(page)
            output_path = get_unique_filename(output_path)
            with open(output_path, "wb") as out:
                writer.write(out)
            messagebox.showinfo("Başarılı", f"{len(ordered_paths)} dosya birleştirildi.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Birleştirme başarısız: {e}")

    nav = tk.Frame(win, bg="#ffffff")
    nav.pack(pady=5)
    tk.Button(nav, text="⬆️ Yukarı", command=move_up, width=10).pack(side="left", padx=10)
    tk.Button(nav, text="⬇️ Aşağı", command=move_down, width=10).pack(side="left", padx=10)

    tk.Button(win, text="✅ PDF'leri Birleştir", command=on_merge, bg="#9C27B0", fg="white", width=30).pack(pady=15)

def preview_pdf(parent):
    input_path = filedialog.askopenfilename(filetypes=[("PDF Dosyaları", "*.pdf")])
    if not input_path:
        return

    try:
        pages = convert_from_path(input_path, dpi=100, poppler_path=POPPLER_PATH)
        if not pages:
            messagebox.showerror("Hata", "PDF sayfaları okunamadı.")
            return

        win = tk.Toplevel(parent)
        win.title("📖 Yavaş Önizleme")
        win.geometry("600x800")
        win.configure(bg="#ffffff")
        open_previews.append(win)

        img_label = tk.Label(win, bg="#ffffff")
        img_label.pack(pady=10)

        page_num_var = tk.StringVar()
        tk.Label(win, textvariable=page_num_var, bg="#ffffff", font=("Segoe UI", 10)).pack()

        current_index = [0]

        def show_page(index):
            img = pages[index].resize((500, 700), RESAMPLE_MODE)
            tk_img = ImageTk.PhotoImage(img)
            img_label.config(image=tk_img)
            img_label.image = tk_img
            page_num_var.set(f"Sayfa {index + 1} / {len(pages)}")

        def next_page():
            if current_index[0] < len(pages) - 1:
                current_index[0] += 1
                show_page(current_index[0])

        def prev_page():
            if current_index[0] > 0:
                current_index[0] -= 1
                show_page(current_index[0])

        nav = tk.Frame(win, bg="#ffffff")
        nav.pack(pady=10)
        tk.Button(nav, text="⬅️ Geri", command=prev_page).pack(side="left", padx=10)
        tk.Button(nav, text="İleri ➡️", command=next_page).pack(side="right", padx=10)

        show_page(current_index[0])

    except Exception as e:
        messagebox.showerror("Hata", f"Önizleme başarısız: {e}")

def show_help_window(parent):
    help_win = tk.Toplevel(parent)
    help_win.title("📖 RedRiverPDF Yardım Rehberi")
    help_win.geometry("650x750")
    help_win.configure(bg="#ffffff")

    text = tk.Text(help_win, wrap="word", font=("Segoe UI", 10), bg="#ffffff")
    text.pack(expand=True, fill="both", padx=10, pady=10)

    help_content = """
📖 RedRiverPDF Tool – Kullanım Rehberi

Bu uygulama, PDF dosyaları üzerinde temel düzenleme işlemlerini kolayca yapmanızı sağlar.
Aşağıda her aracın ne işe yaradığı ve nasıl kullanılacağı adım adım açıklanmıştır:

────────────────────────────────────────────
📤 Sayfa Çıkar
────────────────────────────────────────────
Belirli sayfaları seçerek yeni bir PDF oluşturur.

1. “📤 Sayfaları Çıkar” butonuna tıklayın.
2. PDF dosyasını seçin → hızlı önizleme otomatik açılır.
3. Açılan pencerede çıkarmak istediğiniz sayfa numaralarını girin.
4. Yeni dosya adını belirleyin ve kaydedin.

Örnek girişler:
- 5 → sadece 5. sayfa
- 2,4,6-8 → 2, 4, 6, 7, 8. sayfalar

────────────────────────────────────────────
🗑️ Sayfa Sil
────────────────────────────────────────────
İstenmeyen sayfaları PDF’den çıkarır.

1. “🗑️ Sayfa Sil” butonuna tıklayın.
2. PDF dosyasını seçin → hızlı önizleme otomatik açılır.
3. Silmek istediğiniz sayfa numaralarını girin.
4. Yeni dosya adını belirleyin ve kaydedin.

────────────────────────────────────────────
✂️ PDF Böl
────────────────────────────────────────────
PDF’yi belirli aralıklarla parçalara ayırır.

1. “✂️ PDF Böl” butonuna tıklayın.
2. PDF dosyasını seçin → hızlı önizleme otomatik açılır.
3. Kaç sayfada bir bölmek istediğinizi yazın (örneğin 3).
4. Parçaların kaydedileceği klasörü seçin.

Not: Aynı isimde dosya varsa otomatik olarak (1), (2) gibi numaralar eklenir.

────────────────────────────────────────────
📚 PDF Birleştir
────────────────────────────────────────────
Birden fazla PDF dosyasını seçip sıralayarak birleştirir.

1. “📚 PDF Birleştir” butonuna tıklayın.
2. Ctrl tuşuna basarak birden fazla PDF seçin.
3. Açılan listede dosyaları yukarı/aşağı taşıyarak sıralayın.
4. “✅ PDF’leri Birleştir” butonuna tıklayın ve yeni dosyayı kaydedin.

Not: Dosyalar, listede göründüğü sıraya göre birleştirilir.

────────────────────────────────────────────
🔍 Önizleme Seçenekleri
────────────────────────────────────────────
🐢 Yavaş Önizleme:
- Tüm sayfaları baştan yükler.
- Geçişler hızlıdır.

⚡ Hızlı Önizleme:
- Sadece o anki sayfayı yükler.
- Açılış hızlıdır, geçişlerde yeniden yükleme olur.

────────────────────────────────────────────
🧹 Önizlemeleri Kapat
────────────────────────────────────────────
Açık kalan tüm önizleme pencerelerini tek tıklamayla kapatır.
Yeni bir işlem başlarken eski önizlemeler otomatik olarak da kapanır.

────────────────────────────────────────────
📌 Sayfa Numarası Girişi Formatı
────────────────────────────────────────────
- Tek sayfa: 5
- Aralık: 3-7 → 3, 4, 5, 6, 7
- Karışık: 1,4,6-8 → 1, 4, 6, 7, 8

Sayfa numaraları 1’den başlar. Geçersiz girişlerde uygulama sizi uyarır.

────────────────────────────────────────────
💡 Ek Bilgiler
────────────────────────────────────────────
- Her işlem yeni bir dosya oluşturur. Orijinal dosyanız değişmez.
- Aynı isimde dosya varsa otomatik olarak numaralandırılır.
- İşlem pencereleri ana pencerenin sağına açılır.
- Hatalı girişlerde uygulama sizi uyarır ve işlem iptal edilir.
"""
    text.insert("1.0", help_content)
    text.config(state="disabled")

def create_main_window():
    app = tk.Tk()
    app.title("🧰 RedRiverPDF v2")
    app.geometry("400x600")
    app.configure(bg="#ECEFF1")

    tk.Label(app, text="RedRiverPDF v2", font=("Segoe UI", 16, "bold"), bg="#ECEFF1").pack(pady=(20, 10))

    tk.Button(app, text="📤 Sayfaları Çıkar", command=lambda: extract_pages(app), bg="#4CAF50", fg="white", width=30).pack(pady=5)
    tk.Button(app, text="🗑️ Sayfa Sil", command=lambda: delete_pages(app), bg="#E91E63", fg="white", width=30).pack(pady=5)
    tk.Button(app, text="✂️ PDF'yi Böl", command=lambda: split_pdf(app), bg="#FF5722", fg="white", width=30).pack(pady=5)
    tk.Button(app, text="📚 PDF'leri Birleştir", command=lambda: merge_pdfs(app), bg="#9C27B0", fg="white", width=30).pack(pady=5)

    tk.Label(app, text="Önizleme", font=("Segoe UI", 12, "bold"), bg="#ECEFF1").pack(pady=(20, 5))
    tk.Button(app, text="🐢 Yavaş Önizleme", command=lambda: preview_pdf(app), bg="#607D8B", fg="white", width=30).pack(pady=2)
    tk.Button(app, text="⚡ Hızlı Önizleme", command=lambda: preview_pdf_lazy(app), bg="#03A9F4", fg="white", width=30).pack(pady=2)

    tk.Button(app, text="🧹 Önizlemeleri Kapat", command=close_all_previews, bg="#B0BEC5", fg="black", width=30).pack(pady=(5, 20))
    tk.Button(app, text="📖 Yardım", command=lambda: show_help_window(app), bg="#FFC107", fg="black", width=30).pack()

    return app
