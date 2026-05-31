# ui/tab_slot.py

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from manager import Manager


class SlotTab(ctk.CTkFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        self.manager = Manager()
        self.slot_combos = {}
        self.setup_ui()

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill=tk.X, pady=(10, 20))

        ctk.CTkLabel(
            header_frame,
            text="ロボットの物理スロット(1番〜9番)に搭載するシーケンスを選択してください。",
            font=("Helvetica", 18),
        ).pack(side=tk.LEFT, pady=5)

        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side=tk.RIGHT, padx=2)
        ctk.CTkButton(
            btn_frame,
            text="設定を保存",
            font=("Helvetica", 16, "bold"),
            height=35,
            command=self.save_slot_config,
        ).pack(fill=tk.X, pady=4)
        ctk.CTkButton(
            btn_frame,
            text="ロボット用CSV出力",
            font=("Helvetica", 16, "bold"),
            fg_color="#28a745",
            hover_color="#218838",
            height=35,
            command=self.trigger_csv_export,
        ).pack(fill=tk.X, pady=4)

        self.export_status_label = ctk.CTkLabel(
            header_frame, text="", text_color="green", font=("Helvetica", 16, "bold")
        )
        self.export_status_label.pack(side=tk.RIGHT, padx=10)

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        ctk.CTkLabel(
            form_frame,
            text="スロット割り当て設定(テンキー)",
            font=("Helvetica", 18, "bold"),
        ).pack(anchor="w", padx=15, pady=(15, 10))

        for slot_idx in range(1, 10):
            row = ctk.CTkFrame(form_frame, fg_color="transparent")
            row.pack(fill=tk.X, pady=6)
            ctk.CTkLabel(
                row,
                text=f"Slot {slot_idx} :",
                font=("Helvetica", 18),
                width=120,
                anchor="e",
            ).pack(side=tk.LEFT, padx=(0, 15))

            combo = ctk.CTkComboBox(
                row,
                state="readonly",
                width=360,
                font=("Helvetica", 18),
                dropdown_font=("Helvetica", 18),
                command=lambda e, s=slot_idx: self.on_slot_combo_changed(s),
            )
            combo.pack(side=tk.LEFT)
            self.slot_combos[slot_idx] = combo

        ctk.CTkLabel(
            form_frame,
            text="ここのスペースはなんですか？",
            font=("Helvetica", 14),
            text_color="gray",
        ).pack(side=tk.BOTTOM, anchor="e", padx=15, pady=5)
        self.refresh_comboboxes()

    def refresh_comboboxes(self):
        sequence_names = ["None"] + list(self.manager.sequences.keys())
        for slot_idx, combo in self.slot_combos.items():
            combo.configure(values=sequence_names)
            assigned = self.manager.export_slots.get(slot_idx)
            combo.set(
                str(assigned.name)
                if assigned and assigned.name in self.manager.sequences
                else "None"
            )

    def on_slot_combo_changed(self, slot_idx):
        selected_name = self.slot_combos[slot_idx].get()
        self.manager.export_slots[slot_idx] = (
            None if selected_name == "None" else self.manager.sequences[selected_name]
        )
        self.manager.has_changes = True

    def save_slot_config(self):
        self.manager.save_all()
        self.export_status_label.configure(text="✔ 設定を保存しました")
        self.after(2000, lambda: self.export_status_label.configure(text=""))

    def trigger_csv_export(self):
        try:
            self.manager.export_csv()
            self.manager.save_all()
            self.export_status_label.configure(text="✔ CSVを出力しました")
            self.after(2000, lambda: self.export_status_label.configure(text=""))
        except Exception as e:
            messagebox.showerror(
                "出力エラー", f"CSVの書き込みに失敗しました:\n{str(e)}"
            )
