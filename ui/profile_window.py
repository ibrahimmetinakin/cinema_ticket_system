import tkinter as tk
from tkinter import Canvas, Scrollbar, Frame, messagebox
import database
from ui import film_selection_window
from ui import main_window  # Kullanıcı bilgisi için

def start_profile_window(username=None, email=None):
    if not username or not email:
        user = main_window.get_user()
        username = user["username"]
        email = user["email"]

    user_info = database.get_user_info(username)
    if not user_info:
        messagebox.showerror("Hata", "Kullanıcı bilgisi alınamadı!")
        return

    tickets = database.get_user_tickets(username)
    reservations = database.get_user_reservations(username)

    def go_back():
        root.destroy()
        film_selection_window.start_film_selection_window()

    def open_password_update_window():
        def update_password():
            old_pwd = entry_old.get()
            new_pwd = entry_new.get()
            new_pwd_repeat = entry_new_repeat.get()

            if not old_pwd or not new_pwd or not new_pwd_repeat:
                messagebox.showwarning("Uyarı", "Tüm alanları doldurmalısınız.")
                return

            if new_pwd != new_pwd_repeat:
                messagebox.showerror("Hata", "Yeni şifreler uyuşmuyor!")
                return

            if database.update_user_password(username, old_pwd, new_pwd):
                messagebox.showinfo("Başarılı", "Şifreniz güncellendi!")
                pwd_window.destroy()
            else:
                messagebox.showerror("Hata", "Eski şifreniz yanlış!")

        pwd_window = tk.Toplevel(root)
        pwd_window.title("Şifre Güncelle")
        pwd_window.geometry("400x300")
        pwd_window.config(bg="#A69F87")

        tk.Label(pwd_window, text="Eski Şifre", bg="#A69F87").pack(pady=5)
        entry_old = tk.Entry(pwd_window, show="*", width=30)
        entry_old.pack(pady=5)

        tk.Label(pwd_window, text="Yeni Şifre", bg="#A69F87").pack(pady=5)
        entry_new = tk.Entry(pwd_window, show="*", width=30)
        entry_new.pack(pady=5)

        tk.Label(pwd_window, text="Yeni Şifre Tekrar", bg="#A69F87").pack(pady=5)
        entry_new_repeat = tk.Entry(pwd_window, show="*", width=30)
        entry_new_repeat.pack(pady=5)

        tk.Button(pwd_window, text="Şifreyi Güncelle", command=update_password,
                  bg="#4CAF50", fg="white", width=20).pack(pady=20)

    def cancel_ticket(ticket):
        if messagebox.askyesno("Bilet İptali", "Bu bileti iptal etmek istiyor musunuz?"):
            film, salon, seat, date, time = ticket
            database.cancel_ticket(username, film, salon, seat, date, time)
            root.destroy()
            start_profile_window(username, email)

    def cancel_reservation(reservation):
        if messagebox.askyesno("Rezervasyon İptali", "Bu rezervasyonu iptal etmek istiyor musunuz?"):
            film, salon, seat, date, time = reservation
            database.cancel_reservation(username, film, salon, seat, date, time)
            root.destroy()
            start_profile_window(username, email)

    def open_payment_window(reservation):
        film, salon, seat, date, time = reservation
        pay_window = tk.Toplevel(root)
        pay_window.title("Ödeme Ekranı")
        pay_window.geometry("400x400")
        pay_window.config(bg="#2C2F48")
        pay_window.grab_set()

        tk.Label(pay_window, text="💳 Ödeme Bilgileri", font=("Arial", 18, "bold"), bg="#2C2F48", fg="white").pack(pady=15)
        tk.Label(pay_window, text="Kart Numarası:", bg="#2C2F48", fg="white").pack()
        entry_card = tk.Entry(pay_window)
        entry_card.pack(pady=5)

        tk.Label(pay_window, text="Son Kullanma (AA/YY):", bg="#2C2F48", fg="white").pack()
        entry_expiry = tk.Entry(pay_window)
        entry_expiry.pack(pady=5)

        tk.Label(pay_window, text="CVV:", bg="#2C2F48", fg="white").pack()
        entry_cvv = tk.Entry(pay_window, show="*")
        entry_cvv.pack(pady=5)

        def process_payment():
            card_number = entry_card.get()
            expiry_date = entry_expiry.get()
            cvv = entry_cvv.get()

            # 1️⃣ Kart Numarası Doğrulama
            if len(card_number) != 16 or not card_number.isdigit():
                messagebox.showwarning("Hatalı Kart", "Lütfen 16 haneli geçerli bir kart numarası girin!")
                return

            # 2️⃣ Son Kullanma Tarihi Doğrulama (Format: AA/YY)
            try:
                if len(expiry_date) != 5 or expiry_date[2] != '/':
                    raise ValueError
                month, year = expiry_date.split('/')
                month = int(month)
                year = int('20' + year)  # YY -> 20YY formatına çevir

                if not (1 <= month <= 12):
                    raise ValueError

                from datetime import datetime
                now = datetime.now()
                expiry = datetime(year, month, 1)

                if expiry < now.replace(day=1):
                    messagebox.showwarning("Tarih Hatası", "Kart son kullanma tarihi geçmiş!")
                    return

            except ValueError:
                messagebox.showwarning("Hatalı Tarih", "Lütfen AA/YY formatında geçerli bir tarih girin!")
                return

            # 3️⃣ CVV Doğrulama
            if len(cvv) != 3 or not cvv.isdigit():
                messagebox.showwarning("Hatalı CVV", "Lütfen 3 haneli geçerli bir CVV girin!")
                return

            # ✅ Tüm Kontroller Geçerse Satın Alma İşlemi
            result = database.save_ticket(username, film, salon, seat, date, time)
            if result:
                messagebox.showinfo("Ödeme Başarılı", "Bilet satın alındı ve ödeme tamamlandı!")
                pay_window.destroy()
                root.destroy()
                start_profile_window(username, email)
            else:
                messagebox.showerror("Hata", "Bu koltuk şu anda satın alınamaz!")
                pay_window.destroy()



        tk.Button(pay_window, text="💳 Ödemeyi Tamamla", command=process_payment,
                  bg="#4CAF50", fg="white", width=20).pack(pady=20)
        tk.Button(pay_window, text="❌ İptal", command=pay_window.destroy,
                  bg="#F44336", fg="white", width=20).pack(pady=10)

    root = tk.Tk()
    root.title("Profil Ekranı")
    root.attributes("-fullscreen", True)
    root.config(bg="#A69F87")
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    tk.Label(root, text=f"👤 Kullanıcı: {username}", font=("Arial", 24, "bold"), bg="#FEE715", fg="black").pack(pady=10)
    tk.Label(root, text=f"📧 E-posta: {email}", font=("Arial", 16), bg="#FEE715", fg="black").pack(pady=5)

    canvas = Canvas(root, bg="#A69F87", highlightthickness=0)
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame = Frame(canvas, bg="#A69F87")
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    if tickets:
        tk.Label(frame, text="🎟️ Satın Aldığınız Biletler", font=("Arial", 20, "bold"), bg="#FEE715", fg="black").pack(pady=20)
        for ticket in tickets:
            film, salon, seat, date, time = ticket
            ticket_frame = tk.Frame(frame, bg="white", bd=2, relief="groove")
            ticket_frame.pack(pady=10, padx=50, fill="x")

            info = f"🎬 {film} | 🏛️ {salon} | 💺 Koltuk: {seat} | 📅 {date} {time}"
            tk.Label(ticket_frame, text=info, font=("Arial", 14), bg="white", anchor="w").pack(padx=10, pady=10, fill="x")

            tk.Button(ticket_frame, text="❌ Bileti İptal Et", 
                       command=lambda t=ticket: cancel_ticket(t),
                       bg="#F44336", fg="white", width=20).pack(pady=5)
    else:
        tk.Label(frame, text="Satın alınmış bilet yok.", font=("Arial", 16), bg="#FEE715", fg="black").pack(pady=50)

    if reservations:
        tk.Label(frame, text="🕒 Rezervasyonlarınız", font=("Arial", 20, "bold"), bg="#FEE715", fg="black").pack(pady=20)
        for reservation in reservations:
            film, salon, seat, date, time = reservation
            res_frame = tk.Frame(frame, bg="white", bd=2, relief="groove")
            res_frame.pack(pady=10, padx=50, fill="x")

            info = f"🎬 {film} | 🏛️ {salon} | 💺 Koltuk: {seat} | 📅 {date} {time}"
            tk.Label(res_frame, text=info, font=("Arial", 14), bg="white", anchor="w").pack(padx=10, pady=10, fill="x")

            btn_frame_inner = tk.Frame(res_frame, bg="white")
            btn_frame_inner.pack(pady=5)

            tk.Button(btn_frame_inner, text="❌ Rezervasyonu İptal Et",
                       command=lambda r=reservation: cancel_reservation(r),
                       bg="#FFA500", fg="white", width=20).pack(side="left", padx=10)

            tk.Button(btn_frame_inner, text="💳 Satın Al",
                       command=lambda r=reservation: open_payment_window(r),
                       bg="#4CAF50", fg="white", width=20).pack(side="left", padx=10)
    else:
        tk.Label(frame, text="Aktif rezervasyon yok.", font=("Arial", 16), bg="#FEE715", fg="black").pack(pady=50)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    btn_frame = tk.Frame(root, bg="#A69F87")
    btn_frame.pack(pady=30)

    tk.Button(btn_frame, text="↩️ Geri Dön", command=go_back,
               bg="#2196F3", fg="white", width=15).pack(side="left", padx=20)

    tk.Button(btn_frame, text="⚙️ Hesap Ayarları", command=open_password_update_window,
               bg="#4CAF50", fg="white", width=15).pack(side="left", padx=20)

    root.mainloop()
