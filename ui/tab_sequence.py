# ui/tab_sequence.py

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from manager import Manager
from sequence import Sequence, SequenceStep


class SequenceTab(ctk.CTkFrame):
    def __init__(self, parent, main_window):
        super().__init__(parent, fg_color="transparent")
        self.main_window = main_window
        self.manager = Manager()
        self.timeline_mapping = []
        self.is_updating_widgets = False
        self.setup_ui()

    def setup_ui(self):
        # 1. 上部ツールバー
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(top_bar, text="編集対象:", font=("Helvetica", 18)).pack(
            side=tk.LEFT, padx=5
        )
        self.seq_combobox = ctk.CTkComboBox(
            top_bar,
            state="readonly",
            width=240,
            font=("Helvetica", 18),
            dropdown_font=("Helvetica", 18),
            command=lambda e: self.refresh_right_timeline(),
        )
        self.seq_combobox.pack(side=tk.LEFT, padx=5)

        ctk.CTkButton(
            top_bar,
            text="新規登録",
            font=("Helvetica", 16, "bold"),
            command=self.create_sequence,
        ).pack(side=tk.LEFT, padx=4)
        ctk.CTkButton(
            top_bar,
            text="名前変更",
            font=("Helvetica", 16, "bold"),
            command=self.rename_sequence,
        ).pack(side=tk.LEFT, padx=4)
        ctk.CTkButton(
            top_bar,
            text="シーケンス削除",
            font=("Helvetica", 16, "bold"),
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=self.delete_sequence,
        ).pack(side=tk.LEFT, padx=4)

        ctk.CTkButton(
            top_bar,
            text="設定を保存",
            font=("Helvetica", 16, "bold"),
            command=self.save_sequence_pool,
        ).pack(side=tk.RIGHT, padx=2)
        self.save_status_label = ctk.CTkLabel(
            top_bar, text="", text_color="green", font=("Helvetica", 16, "bold")
        )
        self.save_status_label.pack(side=tk.RIGHT, padx=10)

        # 2. 中央ペイン領域（左右分割）
        pane_frame = ctk.CTkFrame(self, fg_color="transparent")
        pane_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        left_pane = ctk.CTkFrame(pane_frame, width=280)
        left_pane.pack_propagate(False)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        ctk.CTkLabel(
            left_pane, text="モータ一覧（選択して追加）", font=("Helvetica", 16, "bold")
        ).pack(anchor="w", padx=5, pady=(5, 0))
        self.motor_listbox = tk.Listbox(
            left_pane,
            font=("Helvetica", 18),
            background="#ffffff",
            selectbackground="#b3d8ff",
            selectforeground="#000000",
            bd=1,
            highlightthickness=0,
            exportselection=False,
        )
        self.motor_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        mid_pane = ctk.CTkFrame(pane_frame, fg_color="transparent")
        mid_pane.pack(side=tk.LEFT, fill=tk.Y, padx=15)

        mid_btn_container = ctk.CTkFrame(mid_pane, fg_color="transparent")
        mid_btn_container.pack(expand=True)

        self.add_new_step_btn = ctk.CTkButton(
            mid_btn_container,
            text="新規ステップ\nとして追加 ➔",
            font=("Helvetica", 15, "bold"),
            width=140,
            height=50,
            command=self.add_as_new_step,
        )
        self.add_new_step_btn.pack(pady=10)

        self.add_parallel_btn = ctk.CTkButton(
            mid_btn_container,
            text="選択ステップに\n同時駆動を追加 ➔",
            font=("Helvetica", 15, "bold"),
            width=140,
            height=50,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.add_as_parallel_motor,
        )
        self.add_parallel_btn.pack(pady=10)

        right_pane = ctk.CTkFrame(pane_frame)
        right_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ctk.CTkLabel(
            right_pane,
            text="現在のシーケンス (最大10ステップ)",
            font=("Helvetica", 16, "bold"),
        ).pack(anchor="w", padx=5, pady=(5, 0))
        tl_main_frame = ctk.CTkFrame(right_pane, fg_color="transparent")
        tl_main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.timeline_listbox = tk.Listbox(
            tl_main_frame,
            font=("MS Gothic", 16),
            background="#ffffff",
            selectbackground="#b3d8ff",
            selectforeground="#000000",
            bd=1,
            highlightthickness=0,
            exportselection=False,
        )
        self.timeline_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.timeline_listbox.bind("<<ListboxSelect>>", self.on_timeline_select)

        control_btn_frame = ctk.CTkFrame(right_pane, fg_color="transparent")
        control_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        ctk.CTkButton(
            control_btn_frame,
            text="▲ 上へ",
            font=("Helvetica", 16),
            command=self.move_step_up,
        ).pack(fill=tk.X, pady=4)
        ctk.CTkButton(
            control_btn_frame,
            text="▼ 下へ",
            font=("Helvetica", 16),
            command=self.move_step_down,
        ).pack(fill=tk.X, pady=4)

        self.delete_btn = ctk.CTkButton(
            control_btn_frame,
            text="削除",
            font=("Helvetica", 16),
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=self.delete_step,
        )
        self.delete_btn.pack(fill=tk.X, pady=(25, 4))

        # 3. 画面下部インライン編集領域（元の4列構造を維持し、幅を最適化）
        bg_panel_color = "#f0f0f0"
        editor_pane = ctk.CTkFrame(self, fg_color=bg_panel_color)
        editor_pane.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=15)

        # タイトルラベル（「ステップ編集」に統一していただいた部分）
        ctk.CTkLabel(
            editor_pane,
            text="ステップ編集",
            font=("Helvetica", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(15, 2), pady=(10, 5))

        self.edit_step_name_label = ctk.CTkLabel(
            editor_pane,
            text="",
            font=("Helvetica", 16, "bold"),
            text_color="#1f77b4",
        )
        self.edit_step_name_label.grid(
            row=0, column=1, columnspan=3, sticky="w", padx=(0, 15), pady=(10, 5)
        )

        # 元のシンプルな2カラム引き伸ばし設定を維持
        editor_pane.columnconfigure(1, weight=1)
        editor_pane.columnconfigure(3, weight=1)

        # 動作方向 (dir)
        ctk.CTkLabel(
            editor_pane,
            text="動作方向 (dir):",
            font=("Helvetica", 18),
            width=140,
            anchor="w",
        ).grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")

        self.edit_dir_combo = ctk.CTkComboBox(
            editor_pane,
            values=["1: CW (上 / 前)", "2: CCW (下 / 後ろ)"],
            state="readonly",
            width=320,  # ★下のタイムアウト枠（スライダー200＋スピンボックス＋単位）の総幅と目視でピッタリ揃えるための調整
            font=("Helvetica", 18),
            dropdown_font=("Helvetica", 18),
            command=lambda e: self.write_widgets_to_data(),
        )
        self.edit_dir_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # 出力比率 (duty)
        ctk.CTkLabel(
            editor_pane,
            text="出力比率 (duty):",
            font=("Helvetica", 18),
            width=140,
            anchor="w",
        ).grid(row=1, column=2, padx=(35, 5), pady=10, sticky="w")

        duty_frame = ctk.CTkFrame(editor_pane, fg_color=bg_panel_color)
        duty_frame.grid(row=1, column=3, padx=10, pady=10, sticky="w")

        self.edit_duty_scale = ctk.CTkSlider(
            duty_frame,
            from_=0,
            to=100,
            number_of_steps=20,
            width=220,
            height=20,
            command=self.on_duty_scale_changed,
        )
        self.edit_duty_scale.pack(side=tk.LEFT, padx=5)

        self.edit_duty_spin = tk.Spinbox(
            duty_frame,
            from_=0,
            to=100,
            increment=5,
            width=6,
            font=("Helvetica", 18),
            justify=tk.CENTER,
            command=self.on_duty_spin_changed,
        )
        self.edit_duty_spin.pack(side=tk.LEFT, padx=5, ipady=3)
        self.edit_duty_spin.bind("<KeyRelease>", self.on_duty_spin_changed)
        ctk.CTkLabel(duty_frame, text="%", font=("Helvetica", 18)).pack(side=tk.LEFT)

        # タイムアウト
        ctk.CTkLabel(
            editor_pane,
            text="タイムアウト:",
            font=("Helvetica", 18),
            width=140,
            anchor="w",
        ).grid(row=2, column=0, padx=(15, 5), pady=10, sticky="w")

        timeout_frame = ctk.CTkFrame(editor_pane, fg_color=bg_panel_color)
        timeout_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.edit_timeout_scale = ctk.CTkSlider(
            timeout_frame,
            from_=0,
            to=10000,
            number_of_steps=100,
            width=200,
            height=20,
            command=self.on_timeout_scale_changed,
        )
        self.edit_timeout_scale.pack(side=tk.LEFT, padx=5)

        self.edit_timeout_spin = tk.Spinbox(
            timeout_frame,
            from_=0,
            to=99999,
            increment=100,
            width=6,
            font=("Helvetica", 18),
            justify=tk.CENTER,
            command=self.on_timeout_spin_changed,
        )
        self.edit_timeout_spin.pack(side=tk.LEFT, padx=5, ipady=3)
        self.edit_timeout_spin.bind("<KeyRelease>", self.on_timeout_spin_changed)
        ctk.CTkLabel(timeout_frame, text="ms", font=("Helvetica", 18)).pack(
            side=tk.LEFT
        )

        # 目標制御量
        ctk.CTkLabel(
            editor_pane,
            text="目標制御量:",
            font=("Helvetica", 18),
            width=140,
            anchor="w",
        ).grid(row=2, column=2, padx=(35, 5), pady=10, sticky="w")

        target_frame = ctk.CTkFrame(editor_pane, fg_color=bg_panel_color)
        target_frame.grid(row=2, column=3, padx=10, pady=10, sticky="w")

        self.edit_target_scale = ctk.CTkSlider(
            target_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            width=220,
            height=20,
            command=self.on_target_scale_changed,
        )
        self.edit_target_scale.pack(side=tk.LEFT, padx=5)

        self.edit_target_spin = tk.Spinbox(
            target_frame,
            from_=0,
            to=100,
            increment=1,
            width=6,
            font=("Helvetica", 18),
            justify=tk.CENTER,
            command=self.on_target_spin_changed,
        )
        self.edit_target_spin.pack(side=tk.LEFT, padx=5, ipady=3)
        self.edit_target_spin.bind("<KeyRelease>", self.on_target_spin_changed)
        ctk.CTkLabel(target_frame, text="%", font=("Helvetica", 18)).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        # 使用しない (チェックボックス)
        # ★元の通り target_frame の内部にパックして戻すことで、右側の不要な突っ張りや画面の詰まりを解消
        self.target_unused_var = tk.BooleanVar(value=True)
        self.edit_target_check = ctk.CTkCheckBox(
            target_frame,
            text="使用しない",
            font=("Helvetica", 14, "bold"),
            variable=self.target_unused_var,
            command=self.on_target_check_toggled,
        )
        self.edit_target_check.pack(side=tk.LEFT, padx=5)

        self.update_combobox_choices()
        self.refresh_left_list()
        self.set_editor_state("disabled")

    def set_editor_state(self, state_str):
        self.edit_dir_combo.configure(
            state="disabled" if state_str == "disabled" else "readonly"
        )
        self.edit_duty_scale.configure(state=state_str)
        self.edit_duty_spin.config(state=state_str)
        self.edit_timeout_scale.configure(state=state_str)
        self.edit_timeout_spin.config(state=state_str)
        if state_str == "disabled":
            self.edit_target_scale.configure(state="disabled")
            self.edit_target_spin.config(state="disabled")
            self.edit_target_check.configure(state="disabled")
            self.delete_btn.configure(text="削除")
            self.edit_step_name_label.configure(
                text=""
            )  # ★追加：未選択時は非表示にする
        else:
            self.edit_target_check.configure(state="normal")
            if self.target_unused_var.get():
                self.edit_target_scale.configure(state="disabled")
                self.edit_target_spin.config(state="disabled")
            else:
                self.edit_target_scale.configure(state="normal")
                self.edit_target_spin.config(state="normal")

    def on_target_check_toggled(self):
        if self.is_updating_widgets:
            return
        if self.target_unused_var.get():
            self.edit_target_scale.configure(state="disabled")
            self.edit_target_spin.config(state="disabled")
        else:
            self.edit_target_scale.configure(state="normal")
            self.edit_target_spin.configure(state="normal")
        self.write_widgets_to_data()

    def on_duty_scale_changed(self, val):
        if self.is_updating_widgets:
            return
        self.is_updating_widgets = True
        try:
            duty_val = int(round(float(val) / 5) * 5)
            self.edit_duty_spin.delete(0, tk.END)
            self.edit_duty_spin.insert(0, str(duty_val))
        except ValueError:
            pass
        self.is_updating_widgets = False
        self.write_widgets_to_data()

    def on_duty_spin_changed(self, *args):
        if self.is_updating_widgets:
            return
        self.is_updating_widgets = True
        try:
            val = int(self.edit_duty_spin.get() or 0)
            val = max(0, min(100, val))
            self.edit_duty_scale.set(val)
        except ValueError:
            pass
        self.is_updating_widgets = False
        self.write_widgets_to_data()

    def on_timeout_scale_changed(self, val):
        if self.is_updating_widgets:
            return
        self.is_updating_widgets = True
        try:
            timeout_val = int(round(float(val) / 100) * 100)
            self.edit_timeout_spin.delete(0, tk.END)
            self.edit_timeout_spin.insert(0, str(timeout_val))
        except ValueError:
            pass
        self.is_updating_widgets = False
        self.write_widgets_to_data()

    def on_timeout_spin_changed(self, *args):
        if self.is_updating_widgets:
            return
        self.is_updating_widgets = True
        try:
            val = int(self.edit_timeout_spin.get() or 0)
            val = max(0, val)
            self.edit_timeout_scale.set(min(10000, val))
        except ValueError:
            pass
        self.is_updating_widgets = False
        self.write_widgets_to_data()

    def on_target_scale_changed(self, val):
        if self.is_updating_widgets:
            return
        self.is_updating_widgets = True
        try:
            target_val = int(round(float(val)))
            self.edit_target_spin.delete(0, tk.END)
            self.edit_target_spin.insert(0, str(target_val))
        except ValueError:
            pass
        self.is_updating_widgets = False
        self.write_widgets_to_data()

    def on_target_spin_changed(self, *args):
        if self.is_updating_widgets:
            return
        self.is_updating_widgets = True
        try:
            val = int(self.edit_target_spin.get() or 0)
            val = max(0, min(100, val))
            self.edit_target_scale.set(val)
        except ValueError:
            pass
        self.is_updating_widgets = False
        self.write_widgets_to_data()

    def update_combobox_choices(self, set_name=None):
        choices = list(self.manager.sequences.keys())
        self.seq_combobox.configure(values=choices)
        if choices:
            self.seq_combobox.set(
                str(set_name) if set_name in choices else str(choices[0])
            )
        else:
            self.seq_combobox.set("")
        self.refresh_right_timeline()

    def refresh_left_list(self):
        self.motor_listbox.delete(0, tk.END)
        for name in self.manager.motors.keys():
            self.motor_listbox.insert(tk.END, name)

    def refresh_right_timeline(self):
        self.timeline_listbox.unbind("<<ListboxSelect>>")
        self.timeline_listbox.delete(0, tk.END)
        self.timeline_mapping = []
        self.set_editor_state("disabled")

        current_seq_name = self.seq_combobox.get()
        if not current_seq_name or current_seq_name not in self.manager.sequences:
            self.add_new_step_btn.configure(state="disabled")
            self.add_parallel_btn.configure(state="disabled")
            self.timeline_listbox.bind("<<ListboxSelect>>", self.on_timeline_select)
            return

        seq_obj = self.manager.sequences[current_seq_name]
        for s_idx, parallel_step in enumerate(seq_obj.steps):
            sub_count = len(parallel_step)

            # 各ステップに含まれるモータ名をスラッシュ区切りで結合してヘッダーに表示
            motor_names = " / ".join([step.motor.name for step in parallel_step])
            self.timeline_listbox.insert(
                tk.END, f"ステップ {s_idx+1:02d}: {motor_names}"
            )
            self.timeline_mapping.append((s_idx, -1, True))

            for m_idx, step in enumerate(parallel_step):
                bullet = "┗ " if m_idx == sub_count - 1 else "┣ "
                dir_lbl = "CW" if step.dir == 1 else "CCW"
                tgt_lbl = "未使用" if step.target == -1 else str(step.target)

                # 先頭の半角スペースを完全に削除して左端に密着
                self.timeline_listbox.insert(
                    tk.END,
                    f"{bullet}{m_idx+1}. {step.motor.name} (ID: {step.motor.canID}, {dir_lbl}, {step.duty}%, {step.timeout}ms, 目標: {tgt_lbl})",
                )
                self.timeline_mapping.append((s_idx, m_idx, False))

        self.add_new_step_btn.configure(
            state="disabled" if len(seq_obj.steps) >= 10 else "normal"
        )
        self.add_parallel_btn.configure(state="normal" if seq_obj.steps else "disabled")
        self.timeline_listbox.bind("<<ListboxSelect>>", self.on_timeline_select)

    def on_timeline_select(self, event):
        if self.is_updating_widgets:
            return
        current_sel = self.timeline_listbox.curselection()
        if not current_sel:
            return

        idx = current_sel[0]
        step_idx, sub_idx, is_header = self.timeline_mapping[idx]

        if is_header:
            self.delete_btn.configure(text="ステップ全体削除")
            target_sub_idx = 0
        else:
            self.delete_btn.configure(text="同時モータ削除")
            target_sub_idx = sub_idx

        current_seq_name = self.seq_combobox.get()
        seq_obj = self.manager.sequences[current_seq_name]

        # 下部の編集タイトル右側の表示を「 : ステップxx: モータ名 / モータ名」の形式に更新
        parallel_step = seq_obj.steps[step_idx]
        motor_names = " / ".join([st.motor.name for st in parallel_step])
        self.edit_step_name_label.configure(
            text=f" : ステップ {step_idx+1:02d}: {motor_names}"
        )

        if step_idx >= len(seq_obj.steps) or target_sub_idx >= len(
            seq_obj.steps[step_idx]
        ):
            return

        step_obj = seq_obj.steps[step_idx][target_sub_idx]
        self.last_selected_step_sub = (step_idx, target_sub_idx)

        self.is_updating_widgets = True
        try:
            self.edit_dir_combo.configure(state="normal")
            self.edit_duty_scale.configure(state="normal")
            self.edit_duty_spin.config(state="normal")
            self.edit_timeout_scale.configure(state="normal")
            self.edit_timeout_spin.config(state="normal")
            self.edit_target_scale.configure(state="normal")
            self.edit_target_spin.config(state="normal")
            self.edit_target_check.configure(state="normal")

            self.edit_dir_combo.set(
                "1: CW (上 / 前)" if step_obj.dir == 1 else "2: CCW (下 / 後ろ)"
            )
            self.edit_duty_scale.set(step_obj.duty)
            self.edit_duty_spin.delete(0, tk.END)
            self.edit_duty_spin.insert(0, str(step_obj.duty))
            self.edit_timeout_scale.set(min(10000, step_obj.timeout))
            self.edit_timeout_spin.delete(0, tk.END)
            self.edit_timeout_spin.insert(0, str(step_obj.timeout))

            if step_obj.target == -1:
                self.target_unused_var.set(True)
                self.edit_target_scale.set(50)
                self.edit_target_spin.delete(0, tk.END)
                self.edit_target_spin.insert(0, "50")
            else:
                self.target_unused_var.set(False)
                self.edit_target_scale.set(step_obj.target)
                self.edit_target_spin.delete(0, tk.END)
                self.edit_target_spin.insert(0, str(step_obj.target))

            self.set_editor_state("normal")
            self.update_idletasks()
        finally:
            self.is_updating_widgets = False

    def write_widgets_to_data(self, *args):
        if self.is_updating_widgets or not hasattr(self, "last_selected_step_sub"):
            return
        current_seq_name = self.seq_combobox.get()
        step_idx, sub_idx = self.last_selected_step_sub

        seq_obj = self.manager.sequences[current_seq_name]
        if step_idx >= len(seq_obj.steps) or sub_idx >= len(seq_obj.steps[step_idx]):
            return

        step_obj = seq_obj.steps[step_idx][sub_idx]

        try:
            step_obj.dir = 1 if "1:" in self.edit_dir_combo.get() else 2
            try:
                d_val = int(self.edit_duty_spin.get() or 0)
                d_val = max(0, min(100, d_val))
            except ValueError:
                d_val = step_obj.duty
            step_obj.duty = d_val

            try:
                t_val = int(self.edit_timeout_spin.get() or 0)
                t_val = max(0, t_val)
            except ValueError:
                t_val = step_obj.timeout
            step_obj.timeout = t_val

            step_obj.target = (
                -1
                if self.target_unused_var.get()
                else int(round(float(self.edit_target_scale.get())))
            )
            self.manager.has_changes = True
        except ValueError:
            return

        dir_lbl = "CW" if step_obj.dir == 1 else "CCW"
        tgt_lbl = "未使用" if step_obj.target == -1 else str(step_obj.target)

        target_line_idx = -1
        for l_idx, (s, m, h) in enumerate(self.timeline_mapping):
            if s == step_idx and m == sub_idx and not h:
                target_line_idx = l_idx
                break

        if target_line_idx != -1:
            bullet = "┗ " if sub_idx == len(seq_obj.steps[step_idx]) - 1 else "┣ "
            # 先頭の半角スペースを除去した形式で書き換え
            action_str = f"{bullet}{sub_idx+1}. {step_obj.motor.name} (ID: {step_obj.motor.canID}, {dir_lbl}, {step_obj.duty}%, {step_obj.timeout}ms, 目標: {tgt_lbl})"

            self.is_updating_widgets = True
            self.timeline_listbox.unbind("<<ListboxSelect>>")
            try:
                self.timeline_listbox.delete(target_line_idx)
                self.timeline_listbox.insert(target_line_idx, action_str)
                self.timeline_listbox.select_set(target_line_idx)
                self.update_idletasks()
            finally:
                self.timeline_listbox.bind("<<ListboxSelect>>", self.on_timeline_select)
                self.is_updating_widgets = False

    def add_as_new_step(self):
        current_seq_name = self.seq_combobox.get()
        sel_m = self.motor_listbox.curselection()
        if not current_seq_name or not sel_m:
            messagebox.showwarning(
                "選択要求", "モータ一覧から追加するモータを選択してください。"
            )
            return

        m_obj = self.manager.motors[self.motor_listbox.get(sel_m[0])]
        new_step = SequenceStep(motor=m_obj, dir=1, duty=100, timeout=1000, target=-1)
        seq_obj = self.manager.sequences[current_seq_name]

        if len(seq_obj.steps) < 10:
            seq_obj.steps.append([new_step])
            self.manager.has_changes = True

            # 安全に再描画し、流し込みを同期
            if hasattr(self, "last_selected_step_sub"):
                delattr(self, "last_selected_step_sub")
            self.refresh_right_timeline()

            last_idx = len(self.timeline_mapping) - 1
            self.timeline_listbox.select_clear(0, tk.END)
            self.timeline_listbox.select_set(last_idx)
            self.timeline_listbox.event_generate("<<ListboxSelect>>")
        else:
            messagebox.showerror("制限エラー", "最大10ステップまでです。")

    def add_as_parallel_motor(self):
        current_seq_name = self.seq_combobox.get()
        sel_m = self.motor_listbox.curselection()
        if not current_seq_name or not sel_m:
            messagebox.showwarning(
                "選択要求", "モータ一覧から追加するモータを選択してください。"
            )
            return

        current_sel = self.timeline_listbox.curselection()
        if not current_sel:
            messagebox.showwarning(
                "ステップ未選択",
                "同時駆動を追加したい対象のスロット（ステップ）をタイムライン一覧から選択してください。",
            )
            return

        m_obj = self.manager.motors[self.motor_listbox.get(sel_m[0])]
        new_step = SequenceStep(motor=m_obj, dir=1, duty=100, timeout=1000, target=-1)
        seq_obj = self.manager.sequences[current_seq_name]

        step_idx, _, _ = self.timeline_mapping[current_sel[0]]

        for existing_sub in seq_obj.steps[step_idx]:
            if existing_sub.motor.name == m_obj.name:
                messagebox.showerror(
                    "重複エラー",
                    f"モータ '{m_obj.name}' は既にこのステップ内に登録されています。",
                )
                return

        if len(seq_obj.steps[step_idx]) < 3:
            seq_obj.steps[step_idx].append(new_step)
            self.manager.has_changes = True

            # 安全に再描画し、流し込みを同期
            if hasattr(self, "last_selected_step_sub"):
                delattr(self, "last_selected_step_sub")
            self.refresh_right_timeline()

            for l_idx, (s, m, h) in enumerate(self.timeline_mapping):
                if s == step_idx and m == len(seq_obj.steps[step_idx]) - 1 and not h:
                    self.timeline_listbox.select_clear(0, tk.END)
                    self.timeline_listbox.select_set(l_idx)
                    self.timeline_listbox.event_generate("<<ListboxSelect>>")
                    break
        else:
            messagebox.showerror(
                "制限エラー",
                "1つのステップ内で同時に駆動できるモータは最大3個までです。",
            )

    def move_step_up(self):
        sel = self.timeline_listbox.curselection()
        if not sel:
            return
        step_idx, _, _ = self.timeline_mapping[sel[0]]
        if step_idx == 0:
            return

        steps = self.manager.sequences[self.seq_combobox.get()].steps
        steps[step_idx], steps[step_idx - 1] = steps[step_idx - 1], steps[step_idx]
        self.manager.has_changes = True

        if hasattr(self, "last_selected_step_sub"):
            delattr(self, "last_selected_step_sub")
        self.refresh_right_timeline()

        for l_idx, (s, m, h) in enumerate(self.timeline_mapping):
            if s == step_idx - 1:
                self.timeline_listbox.select_set(l_idx)
                self.timeline_listbox.event_generate("<<ListboxSelect>>")
                break

    def move_step_down(self):
        sel = self.timeline_listbox.curselection()
        if not sel:
            return
        step_idx, _, _ = self.timeline_mapping[sel[0]]
        steps = self.manager.sequences[self.seq_combobox.get()].steps
        if step_idx >= len(steps) - 1:
            return

        steps[step_idx], steps[step_idx + 1] = steps[step_idx + 1], steps[step_idx]
        self.manager.has_changes = True

        if hasattr(self, "last_selected_step_sub"):
            delattr(self, "last_selected_step_sub")
        self.refresh_right_timeline()

        for l_idx, (s, m, h) in enumerate(self.timeline_mapping):
            if s == step_idx + 1:
                self.timeline_listbox.select_set(l_idx)
                self.timeline_listbox.event_generate("<<ListboxSelect>>")
                break

    def delete_step(self):
        sel = self.timeline_listbox.curselection()
        if not sel:
            return
        step_idx, sub_idx, is_header = self.timeline_mapping[sel[0]]
        seq_obj = self.manager.sequences[self.seq_combobox.get()]

        if is_header or len(seq_obj.steps[step_idx]) == 1:
            seq_obj.steps.pop(step_idx)
        else:
            seq_obj.steps[step_idx].pop(sub_idx)

        self.manager.has_changes = True

        # ★重要：削除後は選択位置の記憶を完全に抹消して誤上書きをシャットアウト
        if hasattr(self, "last_selected_step_sub"):
            delattr(self, "last_selected_step_sub")

        self.refresh_right_timeline()

    def create_sequence(self):
        from ui.ui_dialogs import SequenceEditDialog

        dialog = SequenceEditDialog(self, "新規Sequenceの追加")
        if dialog.result:
            if dialog.result in self.manager.sequences:
                return
            self.manager.sequences[dialog.result] = Sequence(name=dialog.result)
            self.manager.has_changes = True
            self.update_combobox_choices(set_name=dialog.result)
            self.main_window.notify_sequence_changed()

    def rename_sequence(self):
        c_name = self.seq_combobox.get()
        if not c_name:
            return
        from ui.ui_dialogs import SequenceEditDialog

        dialog = SequenceEditDialog(self, "シーケンス名の変更", current_name=c_name)
        if dialog.result and dialog.result != c_name:
            if dialog.result in self.manager.sequences:
                return
            self.manager.rename_sequence(c_name, dialog.result)
            self.manager.has_changes = True
            self.update_combobox_choices(set_name=dialog.result)
            self.main_window.notify_sequence_changed()

    def delete_sequence(self):
        c_name = self.seq_combobox.get()
        if not c_name:
            return
        if messagebox.askyesno("削除確認", f"Sequence '{c_name}' を削除しますか？"):
            for s_idx, seq in self.manager.export_slots.items():
                if seq and seq.name == c_name:
                    self.manager.export_slots[s_idx] = None
            del self.manager.sequences[c_name]
            self.manager.has_changes = True
            self.update_combobox_choices()
            self.main_window.notify_sequence_changed()

    def save_sequence_pool(self):
        self.manager.save_all()
        self.save_status_label.configure(text="✔ 設定を保存しました")
        self.after(2000, lambda: self.save_status_label.configure(text=""))
