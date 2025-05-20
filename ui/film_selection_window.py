import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas, Frame
from PIL import Image, ImageTk
import os
import subprocess
import sys
import database  # Veritabanı bağlantısı
from ui import movie_theater_selection
from ui import profile_window  # Profil penceresi eklendi

# 📂 Görsel klasör yolu
image_folder = r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos"
films = database.get_all_films()  # 🎬 Veritabanından film listesi al


def buy_ticket(film_name):
    messagebox.showinfo("Bilet Al", f"{film_name} filmi için bilet alma ekranına yönlendiriliyorsunuz.")
    root.destroy()
    movie_theater_selection.start_movie_theater_selection_window(film_name)

def profile_access():
    root.destroy()
    profile_window.start_profile_window()

def exit_app():
    root.destroy()

def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)

def clear_search_placeholder(event):
    if search_entry.get() == "Film Ara...":
        search_entry.delete(0, tk.END)
        search_entry.config(fg="black")

def restore_search_placeholder(event):
    if not search_entry.get():
        search_entry.insert(0, "Film Ara...")
        search_entry.config(fg="gray")

def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def play_trailer(trailer_path):
    print(f"Gelen Fragman Path: {trailer_path}")  # Debug için ekledik

    if trailer_path:
        trailer_path = os.path.normpath(trailer_path)

        if os.path.isfile(trailer_path):
            try:
                os.startfile(trailer_path)
            except AttributeError:
                subprocess.call(['open', trailer_path])  
            except Exception as e:
                messagebox.showerror("Hata", f"Fragman açılamadı: {e}")
        else:
            messagebox.showinfo("Bilgi", f"Fragman dosyası bulunamadı:\n{trailer_path}")
    else:
        messagebox.showinfo("Bilgi", "Bu filme ait fragman bulunamadı.")

def render_films(filtered_films):
    for widget in frame.winfo_children():
        widget.destroy()

    columns = 5
    for idx, (film_name, image_file, trailer_path) in enumerate(filtered_films):
        row = idx // columns
        col = idx % columns

        film_frame = tk.Frame(frame, bg="white", bd=2, relief="raised")
        film_frame.grid(row=row, column=col, padx=15, pady=20)

        image_path = os.path.join(image_folder, image_file)
        if os.path.exists(image_path):
            img = Image.open(image_path).resize((200, 300))
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(film_frame, image=photo)
            img_label.image = photo
            img_label.pack()
        else:
            img_label = tk.Label(film_frame, text="Resim Yok", width=25, height=15, bg="gray")
            img_label.pack()

        name_label = tk.Label(film_frame, text=film_name, font=("Arial", 12), wraplength=180, bg="white")
        name_label.pack(pady=5)

        btn_buy = tk.Button(film_frame, text="Bilet Al", command=lambda f=film_name: buy_ticket(f),
                            bg="#2196F3", fg="white", width=15, height=2)
        btn_buy.pack(pady=5)

        # Fragman butonu kontrolü (Path varsa aktif, yoksa pasif)
        trailer_button_state = "normal" if trailer_path and os.path.isfile(os.path.normpath(trailer_path)) else "disabled"
        btn_trailer = tk.Button(
            film_frame,
            text="Fragmanı İzle",
            command=lambda p=trailer_path: play_trailer(p),
            bg="#FF5722",
            fg="white",
            width=15,
            height=2,
            state=trailer_button_state
        )
        btn_trailer.pack(pady=5)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))


def search_films(event=None):
    keyword = search_var.get().lower()
    filtered = [film for film in films if keyword in film[0].lower()]
    render_films(filtered)

def start_film_selection_window():
    global root, search_entry, frame, canvas, search_var

    root = tk.Tk()
    root.title("Film Seçim Ekranı")
    root.attributes("-fullscreen", True)
    root.config(bg="#A69F87")
    root.bind("<Escape>", exit_fullscreen)

    header = tk.Frame(root, bg="#A69F87")
    header.pack(fill="x", pady=10)

    label_title = tk.Label(header, text="Hoşgeldin, İşte Vizyondaki Filmler!", font=("Arial", 24, "bold"),
                           bg="#A69F87", fg="black")
    label_title.pack(side="left", padx=20)

    search_var = tk.StringVar()
    search_entry = tk.Entry(header, textvariable=search_var, font=("Arial", 14), width=30, fg="gray")
    search_entry.pack(side="left", padx=10)
    search_entry.insert(0, "Film Ara...")
    search_entry.bind("<FocusIn>", clear_search_placeholder)
    search_entry.bind("<FocusOut>", restore_search_placeholder)
    search_entry.bind("<KeyRelease>", search_films)

    btn_profile = tk.Button(header, text="Profilim", command=profile_access, bg="#4CAF50", fg="white",
                            width=15, height=2)
    btn_profile.pack(side="right", padx=10)

    btn_exit = tk.Button(header, text="Çıkış", command=exit_app, bg="#F44336", fg="white", width=15, height=2)
    btn_exit.pack(side="right", padx=10)

    canvas = Canvas(root, bg="#A69F87", highlightthickness=0)
    scrollbar_y = Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar_x = Scrollbar(root, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    frame = Frame(canvas, bg="#A69F87")
    canvas.create_window((0, 0), window=frame, anchor="nw")

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")

    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    render_films(films)

    root.mainloop()
