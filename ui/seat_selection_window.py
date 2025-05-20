import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import time
import database
from ui import main_window
from ui import day_time_selection_window
from ui import profile_window
from ui import payment_window

selected_seats = set()
reservation_time = 15 * 60  # 15 dakika

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def start_seat_selection_window(film_title, theater_name, selected_date, selected_time):
    user = main_window.get_user()
    username = user["username"]
    email = user["email"]

    def open_profile():
        root.destroy()
        profile_window.start_profile_window(username, email)

    def go_back():
        root.destroy()
        day_time_selection_window.start_day_time_selection_window(film_title, theater_name)

    def exit_program():
        if messagebox.askyesno("Çıkış", "Uygulamadan çıkmak istediğinize emin misiniz?"):
            root.destroy()

    def handle_seat_action(seat_id, button):
        action_window = tk.Toplevel(root)
        action_window.title(f"{seat_id} Koltuk İşlemleri")
        center_window(action_window, 350, 200)
        action_window.config(bg="#2C2F48")
        action_window.grab_set()
        action_window.focus_set()
        action_window.transient(root)

        def reserve():
            result = database.reserve_seat(username, film_title, theater_name, seat_id, selected_date, selected_time)
            if result:
                reserved_seats.add(seat_id)
                button.config(bg="#FFA500", state="disabled")
                start_reservation_countdown(seat_id, button)
            else:
                messagebox.showwarning("Uyarı", f"{seat_id} koltuğu şu anda rezerve edilemez.")
            action_window.destroy()

        def purchase():
            action_window.destroy()
            payment_window.start_payment_window(
                username, email, film_title, theater_name, seat_id, selected_date, selected_time, root, seat_buttons
            )

        tk.Label(action_window, text=f"{seat_id} Koltuğu Seç", font=("Arial", 18, "bold"),
                 bg="#2C2F48", fg="white").pack(pady=15)

        tk.Button(action_window, text="🕒 Rezerve Et (15 dk)", command=reserve,
                  bg="#FFA500", fg="white", font=("Arial", 14, "bold"), width=22, height=2).pack(pady=5)

        tk.Button(action_window, text="💳 Hemen Satın Al", command=purchase,
                  bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), width=22, height=2).pack(pady=5)

    def load_reserved_seats():
        return database.get_reserved_seats(film_title, theater_name, selected_date, selected_time)

    def start_reservation_countdown(seat_id, button):
        def countdown():
            remaining_time = reservation_time
            while remaining_time > 0:
                time.sleep(1)
                remaining_time -= 1
            reserved_seats.discard(seat_id)
            button.config(bg="#D3D3D3", state="normal")
        threading.Thread(target=countdown, daemon=True).start()

    root = tk.Tk()
    root.title("Koltuk Seçim Ekranı")
    root.state('zoomed')
    root.config(bg="#1E1E2F")

    # 📌 Ana Çerçeve ve Scroll
    main_canvas = tk.Canvas(root, bg="#1E1E2F", highlightthickness=0)
    main_scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
    main_canvas.configure(yscrollcommand=main_scrollbar.set)

    main_scrollbar.pack(side="right", fill="y")
    main_canvas.pack(side="left", fill="both", expand=True)

    main_frame = tk.Frame(main_canvas, bg="#1E1E2F")
    main_canvas.create_window((0, 0), window=main_frame, anchor="nw")

    def on_main_configure(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    main_frame.bind("<Configure>", on_main_configure)
    main_canvas.bind_all("<MouseWheel>", lambda e: main_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # 🎬 Başlık ve Kullanıcı Bilgisi
    tk.Label(main_frame, text=f"{film_title} - {theater_name}", font=("Arial", 24, "bold"),
             bg="#1E1E2F", fg="white").pack(pady=20)
    tk.Label(main_frame, text=f"Müşteri: {username} | E-posta: {email}",
             font=("Arial", 14), bg="#1E1E2F", fg="white").pack(pady=10)

    # 📢 Banner Görselleri Sağ Tarafa
    banner_frame = tk.Frame(main_frame, bg="#1E1E2F")
    banner_frame.pack(side="right", padx=200, pady=50)

    banner_paths = [
        r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\Screenshot_1.png",
        r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\Screenshot_2.png",
        r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\Screenshot_3.png"
    ]

    banner_images = []
    for path in banner_paths:
        if os.path.exists(path):
            img = Image.open(path).resize((160, 160))
            banner_images.append(ImageTk.PhotoImage(img))

    for banner_photo in banner_images:
        tk.Label(banner_frame, image=banner_photo, bg="#1E1E2F").pack(pady=15)

    # 🎟️ Koltuk Alanı
    seats_frame = tk.Frame(main_frame, bg="#1E1E2F")
    seats_frame.pack(pady=30)

    seat_icon_path = r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\cinema-seat.png"
    seat_photo = None
    if os.path.exists(seat_icon_path):
        seat_img = Image.open(seat_icon_path).resize((38, 38))
        seat_photo = ImageTk.PhotoImage(seat_img)

    rows = [chr(i) for i in range(65, 71)]
    cols = range(1, 19)

    seat_buttons = {}
    sold_seats, reserved_seats = load_reserved_seats()

    for j, col in enumerate(cols, start=1):
        tk.Label(seats_frame, text=str(col), font=("Arial", 12, "bold"),
                 bg="#1E1E2F", fg="red", width=4).grid(row=0, column=j, padx=5)

    for i, row in enumerate(rows, start=1):
        tk.Label(seats_frame, text=row, font=("Arial", 12, "bold"),
                 bg="#1E1E2F", fg="red", width=4).grid(row=i, column=0, padx=5)

        for j, col in enumerate(cols, start=1):
            seat_id = f"{row}{col}"
            btn_params = {
                "bg": "#D3D3D3",
                "bd": 0,
                "relief": "flat",
                "width": 45,
                "height": 45
            }

            if seat_photo:
                btn_params["image"] = seat_photo
                btn_params["compound"] = "center"
                btn_params["text"] = ""

            btn = tk.Button(seats_frame, **btn_params,
                            command=lambda b=seat_id: handle_seat_action(b, seat_buttons[b]))

            if seat_id in sold_seats:
                btn.config(bg="#FF0000", state="disabled")
            elif seat_id in reserved_seats:
                btn.config(bg="#FFA500", state="disabled")

            btn.grid(row=i, column=j, padx=5, pady=5)
            seat_buttons[seat_id] = btn

    # 🎨 Renk Anlamları Paneli
    info_frame = tk.Frame(main_frame, bg="#1E1E2F")
    info_frame.pack(pady=10)

    legend_items = [
        ("#FF0000", "Satılmış Koltuk"),
        ("#FFA500", "Rezerve Koltuk (15 dk süresi var)"),
        ("#D3D3D3", "Boş Koltuk (Seçilebilir)"),
    ]

    for color, text in legend_items:
        item_frame = tk.Frame(info_frame, bg="#1E1E2F")
        item_frame.pack(pady=3)
        tk.Label(item_frame, bg=color, width=4, height=2).pack(side="left", padx=10)
        tk.Label(item_frame, text=text, font=("Arial", 12), bg="#1E1E2F", fg="white").pack(side="left")

    # 🎛️ Alt Butonlar
    btn_frame = tk.Frame(main_frame, bg="#1E1E2F")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="↩️ Geri Dön", command=go_back,
               bg="#2196F3", fg="white", font=("Arial", 14, "bold"),
               width=15, height=2).pack(side="left", padx=20)

    tk.Button(btn_frame, text="👤 Profilim", command=open_profile,
               bg="#4CAF50", fg="white", font=("Arial", 14, "bold"),
               width=15, height=2).pack(side="left", padx=20)

    tk.Button(btn_frame, text="❌ Çıkış", command=exit_program,
               bg="#FF0000", fg="white", font=("Arial", 14, "bold"),
               width=15, height=2).pack(side="right", padx=20)

    root.mainloop()
