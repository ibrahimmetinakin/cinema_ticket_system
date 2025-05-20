import tkinter as tk
from tkinter import messagebox
import database
from datetime import datetime

def start_payment_window(username, email, film_title, theater_name, seat_id, selected_date, selected_time, parent_window, seat_buttons):
    payment_window = tk.Toplevel(parent_window)
    payment_window.title("Ödeme Ekranı")
    payment_window.geometry("400x400")
    payment_window.config(bg="#2C2F48")
    payment_window.grab_set()
    payment_window.focus_set()

    def center_window():
        screen_width = payment_window.winfo_screenwidth()
        screen_height = payment_window.winfo_screenheight()
        x = int((screen_width / 2) - (400 / 2))
        y = int((screen_height / 2) - (400 / 2))
        payment_window.geometry(f"400x400+{x}+{y}")

    center_window()

    tk.Label(payment_window, text="💳 Ödeme Bilgileri", font=("Arial", 18, "bold"), bg="#2C2F48", fg="white").pack(pady=15)

    tk.Label(payment_window, text="Kart Numarası:", bg="#2C2F48", fg="white").pack()
    entry_card = tk.Entry(payment_window, font=("Arial", 12))
    entry_card.pack(pady=5)

    def format_card_number(event):
        value = entry_card.get().replace(" ", "")
        formatted = ' '.join(value[i:i+4] for i in range(0, len(value), 4))
        entry_card.delete(0, tk.END)
        entry_card.insert(0, formatted)

    entry_card.bind("<KeyRelease>", format_card_number)

    tk.Label(payment_window, text="Son Kullanma Tarihi (AA/YY):", bg="#2C2F48", fg="white").pack()
    entry_expiry = tk.Entry(payment_window, font=("Arial", 12))
    entry_expiry.pack(pady=5)

    tk.Label(payment_window, text="CVV:", bg="#2C2F48", fg="white").pack()
    entry_cvv = tk.Entry(payment_window, font=("Arial", 12), show="*")
    entry_cvv.pack(pady=5)

    def process_payment():
        card_number = entry_card.get().replace(" ", "")
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
            year = int('20' + year)

            if not (1 <= month <= 12):
                raise ValueError

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

        # ✅ Ödeme ve Satın Alma İşlemi
        result = database.save_ticket(username, film_title, theater_name, seat_id, selected_date, selected_time)
        if result:
            messagebox.showinfo("Ödeme Başarılı", "Bilet satın alındı ve ödeme tamamlandı!")
            if seat_id in seat_buttons:
                seat_buttons[seat_id].config(bg="#F44336", state="disabled")
            payment_window.destroy()
        else:
            messagebox.showwarning("Hata", f"{seat_id} koltuğu şu anda satın alınamaz.")
            payment_window.destroy()

    tk.Button(payment_window, text="💳 Ödemeyi Tamamla", command=process_payment,
              bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), width=20).pack(pady=20)

    tk.Button(payment_window, text="❌ İptal", command=payment_window.destroy,
              bg="#F44336", fg="white", font=("Arial", 14, "bold"), width=20).pack(pady=10)
