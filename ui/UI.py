# ui/UI.py

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from manager import Manager
from ui.tab_motor import MotorTab
from ui.tab_sequence import SequenceTab
from ui.tab_slot import SlotTab


class UnsavedChangesDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("保存していない変更")
        self.result = "cancel"
        self.transient(parent)
        self.grab_set()
        self.geometry("460x180")
        self.resizable(False, False)

        label = ctk.CTkLabel(
            self,
            text="変更が保存されていません。\n終了する前に変更を保存しますか？",
            font=("Helvetica", 16),
            justify=tk.CENTER,
        )
        label.pack(pady=25)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill=tk.X, padx=20, side=tk.BOTTOM, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="保存して終了",
            font=("Helvetica", 14, "bold"),
            command=self.on_save,
        ).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ctk.CTkButton(
            btn_frame,
            text="保存せずに終了",
            font=("Helvetica", 14, "bold"),
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=self.on_discard,
        ).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ctk.CTkButton(
            btn_frame,
            text="キャンセル",
            font=("Helvetica", 14),
            fg_color="gray",
            hover_color="darkgray",
            command=self.on_cancel,
        ).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window(self)

    def on_save(self):
        self.result = "save"
        self.destroy()

    def on_discard(self):
        self.result = "discard"
        self.destroy()

    def on_cancel(self):
        self.result = "cancel"
        self.destroy()


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ロボットシーケンス制御データ管理システム")
        self.geometry("1280x880")
        self.manager = Manager()
        self.protocol("WM_DELETE_WINDOW", self.on_close_request)
        self.option_add("*TCombobox*Listbox.font", ("Helvetica", 18))

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.tab_view._segmented_button.configure(font=("Helvetica", 18, "bold"))

        self.tab_view.add(" モータ登録設定 ")
        self.tab_view.add(" シーケンス作成・編集 ")
        self.tab_view.add(" 搭載スロット設定 ")

        self.tab1 = MotorTab(self.tab_view.tab(" モータ登録設定 "), main_window=self)
        self.tab1.pack(fill=tk.BOTH, expand=True)
        self.tab2 = SequenceTab(
            self.tab_view.tab(" シーケンス作成・編集 "), main_window=self
        )
        self.tab2.pack(fill=tk.BOTH, expand=True)
        self.tab3 = SlotTab(self.tab_view.tab(" 搭載スロット設定 "), main_window=self)
        self.tab3.pack(fill=tk.BOTH, expand=True)

        self.after(10, lambda: self.state("zoomed"))

    def notify_motor_changed(self):
        self.tab2.refresh_left_list()
        self.tab2.refresh_right_timeline()

    def notify_sequence_changed(self):
        self.tab3.refresh_comboboxes()

    def on_close_request(self):
        if self.manager.has_changes:
            dialog = UnsavedChangesDialog(self)
            if dialog.result == "save":
                try:
                    self.manager.save_all()
                    self.destroy()
                except Exception as e:
                    messagebox.showerror(
                        "保存エラー", f"保存中にエラーが発生しました:\n{e}"
                    )
            elif dialog.result == "discard":
                self.destroy()
            elif dialog.result == "cancel":
                return
        else:
            self.destroy()
