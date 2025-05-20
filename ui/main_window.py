import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageEnhance
import database
from ui import register_window
from ui import film_selection_window  # Film seçim ekranını import ettik

current_user = {"username": None, "email": None}

def set_user(username, email):
    current_user["username"] = username
    current_user["email"] = email

def get_user():
    return current_user

def start_main_window():
    def login(event=None):  # Enter tuşu için event parametresi eklendi
        username = entry_username.get()
        password = entry_password.get()
        if database.check_user(username, password):
            user_info = database.get_user_info(username)
            email = user_info[3] if user_info else ""
            set_user(username, email)
            messagebox.showinfo("Başarılı", "Giriş başarılı!")
            root.destroy()
            film_selection_window.start_film_selection_window()
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre yanlış!")

    def register():
        root.destroy()
        register_window.start_register_screen()

    def exit_app():
        root.destroy()

    root = tk.Tk()
    root.title("Sinema Bilet Sistemi - Giriş")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.bind("<Return>", login)  # Enter tuşunu aktif ettik

    # Arka Plan Resmi ve Karartma
    image_path = r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos\giriş_ekranı.jpg"
    original_bg_image = Image.open(image_path)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    resized_bg_image = original_bg_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Brightness(resized_bg_image)
    darkened_image = enhancer.enhance(0.6)
    bg_image = ImageTk.PhotoImage(darkened_image)

    canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, anchor="nw", image=bg_image)
    canvas.bg_image = bg_image

    # Giriş Paneli
    panel_bg = "#1E3D59"
    panel = tk.Frame(root, bg=panel_bg, bd=10, relief="ridge")
    panel.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(panel, text="🎬 Giriş Yap", font=("Arial", 24, "bold"), bg=panel_bg, fg="white").pack(pady=20)

    tk.Label(panel, text="👤 Kullanıcı Adı", font=("Arial", 14), bg=panel_bg, fg="white").pack(pady=(10, 0))
    entry_username = tk.Entry(panel, font=("Arial", 14), width=30, bd=2, relief="groove")
    entry_username.pack(pady=5)

    tk.Label(panel, text="🔒 Şifre", font=("Arial", 14), bg=panel_bg, fg="white").pack(pady=(10, 0))
    entry_password = tk.Entry(panel, font=("Arial", 14), show="*", width=30, bd=2, relief="groove")
    entry_password.pack(pady=5)

    # Enter tuşu ile giriş için odaklanmayı kolaylaştır
    entry_password.bind("<Return>", login)
    entry_username.bind("<Return>", login)

    btn_style = {"font": ("Arial", 14, "bold"), "width": 20, "height": 2, "bd": 0}

    tk.Button(panel, text="✅ Giriş Yap", command=login, bg="#4CAF50", fg="white", **btn_style).pack(pady=10)
    tk.Button(panel, text="📝 Kayıt Ol", command=register, bg="#2196F3", fg="white", **btn_style).pack(pady=10)
    tk.Button(panel, text="❌ Uygulamadan Çık", command=exit_app, bg="#F44336", fg="white", **btn_style).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    start_main_window()
