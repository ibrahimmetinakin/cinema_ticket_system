import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from ui import seat_selection_window

def start_day_time_selection_window(selected_film, selected_theater):
    selected_time = [None]

    def select_time(selected_btn, time):
        selected_time[0] = time
        for btn in time_buttons:
            btn.config(bg="#2196F3")
        selected_btn.config(bg="#4CAF50")

    def proceed():
        if not selected_time[0]:
            messagebox.showwarning("Uyarı", "Lütfen bir saat seçiniz.")
            return
        selected_date = cal.get_date()
        root.destroy()
        seat_selection_window.start_seat_selection_window(
            film_title=selected_film,
            theater_name=selected_theater,
            selected_date=selected_date,
            selected_time=selected_time[0]
        )

    def go_back():
        root.destroy()
        from ui import movie_theater_selection
        movie_theater_selection.start_movie_theater_selection_window(selected_film)

    def update_times(event=None):
        selected_date_obj = datetime.strptime(cal.get_date(), "%m/%d/%y")
        weekday = selected_date_obj.weekday()
        times = ["14:00", "17:00", "19:00"] if weekday < 5 else ["14:00", "16:00", "18:00", "21:00"]

        for btn in time_buttons:
            btn.pack_forget()
        time_buttons.clear()

        now = datetime.now()

        for time_str in times:
            hour, minute = map(int, time_str.split(":"))
            selected_datetime = selected_date_obj.replace(hour=hour, minute=minute)

            btn_state = "normal"
            if selected_date_obj.date() == now.date():
                if selected_datetime - now < timedelta(hours=1):
                    btn_state = "disabled"

            btn = tk.Button(times_frame, text=time_str,
                            command=lambda b=time_str: select_time(btn_map[b], b),
                            bg="#2196F3", fg="white", font=("Arial", 16, "bold"),
                            width=10, height=2, relief="raised", bd=3, state=btn_state)
            btn.pack(side="left", padx=15, pady=20)
            btn_map[time_str] = btn
            time_buttons.append(btn)

    root = tk.Tk()
    root.title("Tarih ve Saat Seçimi")
    root.attributes("-fullscreen", True)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    bg_path = r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\arka_plan.jpg"
    bg_image = Image.open(bg_path)
    resized_bg = bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(resized_bg)

    canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)
    canvas.bg_image = bg_photo

    time_buttons = []
    btn_map = {}

    title = tk.Label(root, text="Tarih Seçiniz:", font=("Arial", 28, "bold"), bg="#FEE715", fg="black")
    canvas.create_window(screen_width // 2, 80, window=title)

    cal = Calendar(root, selectmode="day", year=datetime.now().year,
                   month=datetime.now().month, day=datetime.now().day, mindate=datetime.now())
    canvas.create_window(screen_width // 2, 300, window=cal)
    cal.bind("<<CalendarSelected>>", update_times)

    times_frame = tk.Frame(root, bg="#FEE715")
    canvas.create_window(screen_width // 2, 500, window=times_frame)

    update_times()

    btn_continue = tk.Button(root, text="Devam Et", command=proceed,
                             bg="#4CAF50", fg="white", font=("Arial", 18, "bold"), width=20, height=2)
    canvas.create_window(screen_width // 2, screen_height - 150, window=btn_continue)

    btn_back = tk.Button(root, text="↩️ Geri Dön", command=go_back,
                         bg="#2196F3", fg="white", font=("Arial", 16), width=15, height=2)
    canvas.create_window(screen_width // 2, screen_height - 80, window=btn_back)

    root.mainloop()
