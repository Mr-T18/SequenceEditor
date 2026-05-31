# ui/tab_motor.py

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from manager import Manager
from motor import Motor


class MotorTab(ctk.CTkFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        self.manager = Manager()
        self.selected_motor_name = None
        self.setup_ui()

    def setup_ui(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkButton(
            toolbar,
            text="選択中のモータを削除",
            font=("Helvetica", 16, "bold"),
            fg_color="#d9534f",
            hover_color="#c9302c",
            height=38,
            command=self.delete_motor,
        ).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(
            toolbar,
            text="設定を保存",
            font=("Helvetica", 16, "bold"),
            height=38,
            command=self.save_motor_pool,
        ).pack(side=tk.RIGHT, padx=2)
        self.save_status_label = ctk.CTkLabel(
            toolbar, text="", text_color="green", font=("Helvetica", 16, "bold")
        )
        self.save_status_label.pack(side=tk.RIGHT, padx=10)

        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.motor_listbox = tk.Listbox(
            list_frame,
            font=("MS Gothic", 18),
            background="#ffffff",
            selectbackground="#b3d8ff",
            selectforeground="#000000",
            bd=1,
            highlightthickness=0,
        )
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.motor_listbox.yview)
        self.motor_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.motor_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.motor_listbox.bind("<<ListboxSelect>>", self.on_motor_select)

        bg_panel_color = "#f0f0f0"
        editor_pane = ctk.CTkFrame(self, fg_color=bg_panel_color)
        editor_pane.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=15)
        ctk.CTkLabel(
            editor_pane, text="モータの情報入力・編集", font=("Helvetica", 16, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))

        inputs_frame = ctk.CTkFrame(editor_pane, fg_color=bg_panel_color)
        inputs_frame.pack(fill=tk.X, padx=15, pady=5)

        ctk.CTkLabel(
            inputs_frame,
            text="モータ名:",
            font=("Helvetica", 18),
            width=120,
            anchor="e",
        ).pack(side=tk.LEFT, padx=5)
        self.name_entry = ctk.CTkEntry(inputs_frame, font=("Helvetica", 18), width=300)
        self.name_entry.pack(side=tk.LEFT, padx=10)

        ctk.CTkLabel(
            inputs_frame, text="CAN ID:", font=("Helvetica", 18), width=120, anchor="e"
        ).pack(side=tk.LEFT, padx=5)
        self.can_id_spin = tk.Spinbox(
            inputs_frame,
            from_=1,
            to=254,
            increment=1,
            width=8,
            font=("Helvetica", 18),
            justify=tk.CENTER,
        )
        self.can_id_spin.delete(0, tk.END)
        self.can_id_spin.insert(0, "1")
        self.can_id_spin.pack(side=tk.LEFT, padx=10, ipady=3)

        btn_frame = ctk.CTkFrame(editor_pane, fg_color=bg_panel_color)
        btn_frame.pack(fill=tk.X, padx=15, pady=(5, 15))

        ctk.CTkButton(
            btn_frame,
            text="入力欄をクリア",
            font=("Helvetica", 16),
            fg_color="gray",
            hover_color="darkgray",
            height=40,
            command=self.clear_inputs,
        ).pack(side=tk.LEFT, padx=5)
        self.btn_update = ctk.CTkButton(
            btn_frame,
            text="選択中を更新 (改名連動)",
            font=("Helvetica", 16, "bold"),
            height=40,
            command=self.update_motor,
            state="disabled",
        )
        self.btn_update.pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(
            btn_frame,
            text="新規モータ登録",
            font=("Helvetica", 16, "bold"),
            height=40,
            command=self.register_motor,
        ).pack(side=tk.RIGHT, padx=5)

        self.refresh_motor_list()

    def refresh_motor_list(self):
        import unicodedata

        self.motor_listbox.delete(0, tk.END)

        def pad_text(text, target_len):
            current_width = sum(
                2 if unicodedata.east_asian_width(c) in "FWA" else 1 for c in text
            )
            return text + " " * max(0, target_len - current_width)

        for m in self.manager.motors.values():
            self.motor_listbox.insert(
                tk.END, f"モータ名: {pad_text(m.name, 24)} | CAN ID: {m.canID:<4}"
            )
        self.clear_inputs()

    def on_motor_select(self, event):
        sel = self.motor_listbox.curselection()
        if not sel:
            return
        m_name = (
            self.motor_listbox.get(sel[0])
            .split("|")[0]
            .replace("モータ名:", "")
            .strip()
        )
        m_obj = self.manager.motors[m_name]
        self.selected_motor_name = m_name
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, m_obj.name)
        self.can_id_spin.delete(0, tk.END)
        self.can_id_spin.insert(0, str(m_obj.canID))
        self.btn_update.configure(state="normal")

    def clear_inputs(self):
        self.selected_motor_name = None
        self.name_entry.delete(0, tk.END)
        self.can_id_spin.delete(0, tk.END)
        self.can_id_spin.insert(0, "1")
        self.btn_update.configure(state="disabled")
        self.motor_listbox.selection_clear(0, tk.END)

    def register_motor(self):
        name = self.name_entry.get().strip()
        if not name or name in self.manager.motors:
            return
        try:
            can_id = int(self.can_id_spin.get())
        except ValueError:
            return
        if not (1 <= can_id <= 254):
            return
        self.manager.motors[name] = Motor(name, can_id)
        self.manager.has_changes = True
        self.refresh_motor_list()
        self.main_window.notify_motor_changed()

    def update_motor(self):
        if not self.selected_motor_name:
            return
        name = self.name_entry.get().strip()
        if not name or (
            name != self.selected_motor_name and name in self.manager.motors
        ):
            return
        try:
            can_id = int(self.can_id_spin.get())
        except ValueError:
            return
        if not (1 <= can_id <= 254):
            return
        new_motor = Motor(name, can_id)
        self.manager.update_motor(self.selected_motor_name, new_motor)
        self.manager.has_changes = True
        self.refresh_motor_list()
        self.main_window.notify_motor_changed()

    def delete_motor(self):
        sel = self.motor_listbox.curselection()
        if not sel:
            return
        m_name = (
            self.motor_listbox.get(sel[0])
            .split("|")[0]
            .replace("モータ名:", "")
            .strip()
        )
        if self.manager.is_motor_used(m_name):
            return
        if messagebox.askyesno("削除確認", f"モータ '{m_name}' を削除しますか？"):
            del self.manager.motors[m_name]
            self.manager.has_changes = True
            self.refresh_motor_list()
            self.main_window.notify_motor_changed()

    def save_motor_pool(self):
        self.manager.save_all()
        self.save_status_label.configure(text="✔ 設定を保存しました")
        self.after(2000, lambda: self.save_status_label.configure(text=""))
