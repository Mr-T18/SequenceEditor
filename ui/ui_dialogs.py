# ui/ui_dialogs.py

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk


class SequenceEditDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, current_name=""):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.result = None

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        lbl_frame = ctk.CTkFrame(container, fg_color="transparent")
        lbl_frame.pack(fill=tk.X, pady=15)

        ctk.CTkLabel(
            lbl_frame,
            text="シーケンス名:",
            width=120,
            anchor="e",
            font=("Helvetica", 18),
        ).pack(side=tk.LEFT, padx=(0, 10))
        self.name_entry = ctk.CTkEntry(lbl_frame, font=("Helvetica", 18), width=260)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.name_entry.insert(0, current_name)

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=(15, 0))

        ctk.CTkButton(
            btn_frame,
            text="キャンセル",
            font=("Helvetica", 16),
            fg_color="gray",
            hover_color="darkgray",
            command=self.destroy,
        ).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(
            btn_frame,
            text="確定",
            font=("Helvetica", 16, "bold"),
            command=self.on_confirm,
        ).pack(side=tk.RIGHT, padx=5)

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)

    def on_confirm(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror(
                "エラー", "シーケンス名を入力してください。", parent=self
            )
            return
        self.result = name
        self.destroy()
