import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import database
from ui import main_window  # Doğru import!

def start_register_screen():
    def change_image():
        global img_index, after_id
        image_path = os.path.join(image_folder, images[img_index])
        img = Image.open(image_path)
        img = img.resize((screen_width // 2, screen_height))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo

        img_index = (img_index + 1) % len(images)
        after_id = root.after(3000, change_image)  # after_id kaydediliyor

    def register():
        email = entry_email.get()
        username = entry_username.get()
        password = entry_password.get()
        password_repeat = entry_password_repeat.get()

        if email == placeholders["email"]: email = ""
        if username == placeholders["username"]: username = ""
        if password == placeholders["password"]: password = ""
        if password_repeat == placeholders["password_repeat"]: password_repeat = ""

        if not email or not username or not password or not password_repeat:
            messagebox.showerror("Hata", "Tüm alanları doldurmalısınız.")
            return

        if password != password_repeat:
            messagebox.showerror("Hata", "Şifreler uyuşmuyor!")
            return

        if database.create_user(username, password, email):
            messagebox.showinfo("Başarılı", "Kayıt başarılı! Giriş ekranına yönlendiriliyorsunuz.")
            on_close()
            main_window.start_main_window()
        else:
            messagebox.showerror("Hata", "Bu kullanıcı adı veya e-posta zaten kayıtlı.")

    def on_close():
        global after_id
        if after_id:
            root.after_cancel(after_id)
        root.destroy()

    def exit_app():
        on_close()

    def back_to_login():
        on_close()
        main_window.start_main_window()

    # Placeholder Fonksiyonları
    def add_placeholder(entry, text, is_password=False):
        entry.insert(0, text)
        entry.config(fg="gray", show="")
        entry.placeholder = (text, is_password)

    def clear_placeholder(event):
        entry = event.widget
        text, is_password = getattr(entry, 'placeholder', ("", False))
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg="black")
            if is_password:
                entry.config(show="•")

    def restore_placeholder(event):
        entry = event.widget
        if not entry.get():
            text, is_password = getattr(entry, 'placeholder', ("", False))
            add_placeholder(entry, text, is_password)

    # Buton Hover Efekti
    def on_enter(event):
        event.widget.config(bg="#555555")

    def on_leave(event):
        color_map = {
            "Kayıt Ol": "#4CAF50",
            "Uygulamadan Çık": "#F44336",
            "Giriş Ekranına Dön": "#2196F3"
        }
        event.widget.config(bg=color_map.get(event.widget.cget("text"), "#003F88"))

    # Ana Pencere
    root = tk.Tk()
    root.title("Kayıt Ol")
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.config(bg="#FEE715")

    # Pencere Kapanışını Yakala
    root.protocol("WM_DELETE_WINDOW", on_close)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    image_folder = r"C:\Users\metin\OneDrive\Desktop\cinema_ticket_system\photos"
    images = ["kayıt-1.jpg", "kayıt-2.1.png", "kayıt-3.1.png"]

    global img_index, after_id
    img_index = 0
    after_id = None

    image_label = tk.Label(root)
    image_label.place(x=0, y=0, width=screen_width // 2, height=screen_height)
    change_image()

    form_frame = tk.Frame(root, bg="#003F88")
    form_frame.place(x=screen_width // 2, y=0, width=screen_width // 2, height=screen_height)

    tk.Label(form_frame, text="Kayıt Ol", font=("Arial", 32), bg="#003F88", fg="white").pack(pady=40)

    placeholders = {
        "email": "E-posta adresinizi girin",
        "username": "Kullanıcı adınızı girin",
        "password": "Şifrenizi girin",
        "password_repeat": "Şifrenizi tekrar girin"
    }

    entry_email = tk.Entry(form_frame, font=("Arial", 16), width=30)
    add_placeholder(entry_email, placeholders["email"])
    entry_email.bind("<FocusIn>", clear_placeholder)
    entry_email.bind("<FocusOut>", restore_placeholder)
    entry_email.pack(pady=10)

    entry_username = tk.Entry(form_frame, font=("Arial", 16), width=30)
    add_placeholder(entry_username, placeholders["username"])
    entry_username.bind("<FocusIn>", clear_placeholder)
    entry_username.bind("<FocusOut>", restore_placeholder)
    entry_username.pack(pady=10)

    entry_password = tk.Entry(form_frame, font=("Arial", 16), width=30)
    add_placeholder(entry_password, placeholders["password"], is_password=True)
    entry_password.bind("<FocusIn>", clear_placeholder)
    entry_password.bind("<FocusOut>", restore_placeholder)
    entry_password.pack(pady=10)

    entry_password_repeat = tk.Entry(form_frame, font=("Arial", 16), width=30)
    add_placeholder(entry_password_repeat, placeholders["password_repeat"], is_password=True)
    entry_password_repeat.bind("<FocusIn>", clear_placeholder)
    entry_password_repeat.bind("<FocusOut>", restore_placeholder)
    entry_password_repeat.pack(pady=10)

    buttons = [
        ("Kayıt Ol", register, "#4CAF50"),
        ("Uygulamadan Çık", exit_app, "#F44336"),
        ("Giriş Ekranına Dön", back_to_login, "#2196F3")
    ]

    for text, command, color in buttons:
        btn = tk.Button(form_frame, text=text, command=command, bg=color, fg="white", width=20, height=2, font=("Arial", 12))
        btn.pack(pady=10)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    root.mainloop()
