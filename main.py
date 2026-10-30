import json
import random
import string
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

DATA_FILE = Path("passwords.json")

BG_COLOR = "#1e1e2e"        
FG_COLOR = "#cdd6f4"        
FRAME_BG = "#313244"        
ACCENT_COLOR = "#89b4fa"    
BTN_TEXT = "#11111b"        
RED_COLOR = "#f38ba8"       
GREEN_COLOR = "#a6e3a1"     


class PasswordManagerApp:

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Менеджер паролей (Вариант 28)")
        self.root.geometry("750x700")  
        self.root.minsize(650, 600)
        self.root.configure(bg=BG_COLOR)

        self.passwords = self.load_data()
        self.visible_passwords = set() 
        
        self.create_styles()
        self.create_widgets()
        self.refresh_table()

    def create_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TLabelframe", background=FRAME_BG, foreground=FG_COLOR, bordercolor=ACCENT_COLOR)
        style.configure("TLabelframe.Label", background=FRAME_BG, foreground=ACCENT_COLOR, font=("Segoe UI", 10, "bold"))

        style.configure("Treeview", background=FRAME_BG, foreground=FG_COLOR, fieldbackground=FRAME_BG, bordercolor=BG_COLOR, rowheight=30)
        style.configure("Treeview.Heading", background=ACCENT_COLOR, foreground=BTN_TEXT, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT_COLOR)], foreground=[("selected", BTN_TEXT)])

    def create_widgets(self) -> None:
        frame_add = tk.LabelFrame(self.root, text=" Добавить новый пароль ", padx=15, pady=15, bg=FRAME_BG, fg=FG_COLOR, font=("Segoe UI", 11, "bold"))
        frame_add.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_add, text="Сайт:", bg=FRAME_BG, fg=FG_COLOR, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_site = tk.Entry(frame_add, width=35, bg="#181825", fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat", font=("Segoe UI", 10))
        self.entry_site.grid(row=0, column=1, padx=10, pady=5, ipady=4)

        tk.Label(frame_add, text="Логин:", bg=FRAME_BG, fg=FG_COLOR, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_login = tk.Entry(frame_add, width=35, bg="#181825", fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat", font=("Segoe UI", 10))
        self.entry_login.grid(row=1, column=1, padx=10, pady=5, ipady=4)

        tk.Label(frame_add, text="Пароль:", bg=FRAME_BG, fg=FG_COLOR, font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_password = tk.Entry(frame_add, width=35, show="*", bg="#181825", fg=FG_COLOR, insertbackground=FG_COLOR, relief="flat", font=("Segoe UI", 10))
        self.entry_password.grid(row=2, column=1, padx=10, pady=5, ipady=4)

        self.show_password = False
        self.btn_eye = tk.Button(frame_add, text="👁", bg=FRAME_BG, fg=ACCENT_COLOR, activebackground=FRAME_BG, relief="flat", command=self.toggle_password, cursor="hand2", font=("Segoe UI", 12))
        self.btn_eye.grid(row=2, column=2, padx=5)

        btn_generate = tk.Button(frame_add, text="⚡ Сгенерировать", bg=ACCENT_COLOR, fg=BTN_TEXT, activebackground="#b4befe", relief="flat", font=("Segoe UI", 10, "bold"), command=self.generate_password, cursor="hand2")
        btn_generate.grid(row=0, column=2, rowspan=2, padx=10, pady=5, ipadx=10, ipady=5)

        btn_save = tk.Button(frame_add, text="💾 Сохранить пароль", bg=GREEN_COLOR, fg=BTN_TEXT, activebackground="#94e2d5", relief="flat", font=("Segoe UI", 11, "bold"), command=self.save_password, cursor="hand2")
        btn_save.grid(row=3, column=0, columnspan=3, pady=15, ipadx=20, ipady=5)

        frame_list = tk.LabelFrame(self.root, text=" Сохраненные пароли (кликните на 👁, чтобы показать) ", padx=15, pady=15, bg=FRAME_BG, fg=FG_COLOR, font=("Segoe UI", 11, "bold"))
        frame_list.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(frame_list, columns=("site", "login", "password", "show"), show="headings")
        self.tree.heading("site", text="Сайт")
        self.tree.heading("login", text="Логин")
        self.tree.heading("password", text="Пароль")
        self.tree.heading("show", text="👁")
        
        self.tree.column("site", width=180)
        self.tree.column("login", width=180)
        self.tree.column("password", width=180)
        self.tree.column("show", width=50, anchor="center") 
        
        self.tree.pack(fill="both", expand=True, pady=5)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)

        btn_delete = tk.Button(frame_list, text="🗑 Удалить выбранный", bg=RED_COLOR, fg=BTN_TEXT, activebackground="#f2cdcd", relief="flat", font=("Segoe UI", 10, "bold"), command=self.delete_password, cursor="hand2")
        btn_delete.pack(side="bottom", pady=10, ipadx=10, ipady=3)

    def on_tree_click(self, event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#4": # Колонка "show"
                item_id = self.tree.identify_row(event.y)
                if item_id:
                    index = self.tree.index(item_id)
                    self.toggle_table_password(index)
                    self.refresh_table()

    def toggle_table_password(self, index: int) -> None:
        if index in self.visible_passwords:
            self.visible_passwords.remove(index)
        else:
            self.visible_passwords.add(index)

    def toggle_password(self) -> None:
        if self.show_password:
            self.entry_password.config(show="*")
            self.btn_eye.config(fg=ACCENT_COLOR)
        else:
            self.entry_password.config(show="")
            self.btn_eye.config(fg=RED_COLOR)
        self.show_password = not self.show_password

    def generate_password(self) -> None:
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(random.choice(chars) for _ in range(12))
        self.entry_password.delete(0, tk.END)
        self.entry_password.insert(0, password)
        self.entry_password.config(show="")
        self.show_password = True
        self.btn_eye.config(fg=RED_COLOR)

    def save_password(self) -> None:
        site = self.entry_site.get().strip()
        login = self.entry_login.get().strip()
        password = self.entry_password.get().strip()

        if not site or not login or not password:
            messagebox.showwarning("Ошибка ввода", "Все поля должны быть заполнены!")
            return

        self.passwords.append({"site": site, "login": login, "password": password})
        self.save_data()
        self.refresh_table()
        
        self.entry_site.delete(0, tk.END)
        self.entry_login.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_password.config(show="*")
        self.show_password = False
        self.btn_eye.config(fg=ACCENT_COLOR)
        
        messagebox.showinfo("Успех", f"Пароль для {site} успешно сохранен!")

    def delete_password(self) -> None:
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Сначала выберите пароль в таблице!")
            return

        item_id = selected_item[0]
        index = self.tree.index(item_id)
        
        confirm = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот пароль?")
        if confirm:
            del self.passwords[index]
            self.visible_passwords = {i-1 if i > index else i for i in self.visible_passwords if i != index}
            self.save_data()
            self.refresh_table()

    def refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for i, pwd in enumerate(self.passwords):
            if i in self.visible_passwords:
                display_pwd = pwd["password"]
                eye_icon = "🔒"
            else:
                display_pwd = "********"
                eye_icon = "👁"
                
            self.tree.insert("", tk.END, values=(pwd["site"], pwd["login"], display_pwd, eye_icon))

    def load_data(self) -> list:
        if not DATA_FILE.exists():
            return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Ошибка файла", f"Не удалось прочитать файл: {e}")
            return []

    def save_data(self) -> None:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.passwords, f, ensure_ascii=False, indent=4)
        except OSError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл: {e}")


def main() -> None:
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()