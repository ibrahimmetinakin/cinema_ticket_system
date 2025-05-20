import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from ui import day_time_selection_window
from ui import film_selection_window

def start_movie_theater_selection_window(selected_film):
    def select_theater(theater_name):
        messagebox.showinfo("Salon Seçildi", 
            f"Film: {selected_film}\nSalon: {theater_name}\nGün ve saat seçimine yönlendiriliyorsunuz.")
        root.destroy()
        day_time_selection_window.start_day_time_selection_window(selected_film, theater_name)

    def go_back():
        root.destroy()
        film_selection_window.start_film_selection_window()

    def exit_app():
        root.destroy()

    def exit_fullscreen(event=None):
        root.attributes("-fullscreen", False)

    root = tk.Tk()
    root.title("Salon Seçim Ekranı")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", exit_fullscreen)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Arka Plan Resmi
    bg_path = r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\arka_plan.jpg"
    original_bg_image = Image.open(bg_path)
    resized_bg_image = original_bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(resized_bg_image)

    canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0, bg="black")
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=bg_image)
    canvas.bg_image = bg_image

    image_paths = [
        r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\sinema-1.png",
        r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\sinema-2.jpg",
        r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\sinema-3.jpg"
    ]
    theaters = ["CINEWEST Sinemaları", "Cinetime Özdilek Kocaeli", "İzmit Symbol AVM Cinemarine"]

    theater_infos = [
        "📍 Adres: Salim Dervişoğlu Cad. Ncity AVM No:82/85 İzmit / Kocaeli\n"
        "📞 Telefon: +90 262 323 11 41 / 0 262 371 19 26\n",

        "📍 Adres: İzmit Adapazarı Yolu 9.km Özdilek Kocaeli AVM Uzunçiftlik / İzmit\n"
        "📞 Telefon: +90 0 262 371 19 26",

        "📍 Adres: Symbol AVM D-100 Karayolu No:34 Yahya Kaptan Mevkii / Kocaeli\n"
        "📞 Telefon: +90 262 502 07 74"
    ]

    image_objs = []
    for path in image_paths:
        try:
            img = Image.open(path).resize((400, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            image_objs.append(photo)
        except:
            image_objs.append(None)

    title = tk.Label(root, text=f"{selected_film} için sinema seçin:", 
                     font=("Arial", 28, "bold"), bg="#000000", fg="white")
    canvas.create_window(screen_width // 2, 80, window=title)

    card_frame = tk.Frame(root, bg="#A69F87")
    canvas.create_window(screen_width // 2, 400, window=card_frame)

    for idx, theater in enumerate(theaters):
        # 📌 Kartlara Gölge ve Çerçeve Eklendi
        card = tk.Frame(card_frame, bg="white", bd=5, relief="ridge")
        card.pack(side="left", padx=50, pady=20)

        if image_objs[idx]:
            img_label = tk.Label(card, image=image_objs[idx], bg="white")
            img_label.image = image_objs[idx]
            img_label.pack(pady=10)
        else:
            tk.Label(card, text="Resim Yok", bg="white", font=("Arial", 12, "italic")).pack(pady=10)

        tk.Button(card, text=theater, 
                   command=lambda t=theater: select_theater(t),
                   bg="#4CAF50", fg="black", font=("Arial", 16, "bold"), width=30, height=2).pack(pady=10)

        # 📌 Salon Bilgisi Ekleniyor
        info_label = tk.Label(card, text=theater_infos[idx], font=("Arial", 10), 
                              bg="white", justify="left", anchor="w", wraplength=380)
        info_label.pack(padx=10, pady=5)

    control_frame = tk.Frame(root, bg="#000000")
    canvas.create_window(screen_width // 2, screen_height - 100, window=control_frame)

    tk.Button(control_frame, text="↩️ Geri Dön", command=go_back,
               bg="#2196F3", fg="white", font=("Arial", 16, "bold"), width=15, height=2).pack(side="left", padx=30)

    tk.Button(control_frame, text="❌ Çıkış", command=exit_app, 
               bg="#F44336", fg="white", font=("Arial", 16, "bold"), width=15, height=2).pack(side="right", padx=30)

    root.mainloop()
