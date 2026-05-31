# manager.py

import json
import os
from motor import Motor
from sequence import Sequence, SequenceStep


class Manager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.init_manager()
        return cls._instance

    def init_manager(self):
        self.motors = {}
        self.sequences = {}
        self.export_slots = {i: None for i in range(1, 10)}
        self.has_changes = False
        self.load_all()

    def is_motor_used(self, motor_name):
        for seq in self.sequences.values():
            for parallel_step in seq.steps:
                for step in parallel_step:
                    if step.motor.name == motor_name:
                        return True
        return False

    def update_motor(self, old_name, new_motor_obj):
        if old_name in self.motors:
            del self.motors[old_name]
        self.motors[new_motor_obj.name] = new_motor_obj
        for seq in self.sequences.values():
            for parallel_step in seq.steps:
                for step in parallel_step:
                    if step.motor.name == old_name:
                        step.motor = new_motor_obj

    def rename_sequence(self, old_name, new_name):
        if old_name in self.sequences:
            seq = self.sequences.pop(old_name)
            seq.name = new_name
            self.sequences[new_name] = seq
            for slot_idx, s in self.export_slots.items():
                if s and s.name == old_name:
                    self.export_slots[slot_idx] = seq

    def load_all(self):
        # 1. json/motor.json の読み込み (文字コード自動判別対応)
        motor_path = os.path.join("json", "motor.json")
        if os.path.exists(motor_path):
            motors_data = None
            for enc in ["utf-8-sig", "utf-8", "cp932"]:
                try:
                    with open(motor_path, "r", encoding=enc) as f:
                        motors_data = json.load(f)
                    break
                except Exception:
                    continue

            if motors_data and isinstance(motors_data, list):
                for m_data in motors_data:
                    if "name" in m_data and "canID" in m_data:
                        self.motors[m_data["name"]] = Motor(
                            m_data["name"], m_data["canID"]
                        )

        # 2. json/sequence.json の読み込み (同時駆動の2次元展開互換)
        seq_path = os.path.join("json", "sequence.json")
        if os.path.exists(seq_path):
            data = None
            for enc in ["utf-8-sig", "utf-8", "cp932"]:
                try:
                    with open(seq_path, "r", encoding=enc) as f:
                        data = json.load(f)
                    break
                except Exception:
                    continue

            if data and isinstance(data, dict):
                sequences_data = data.get("sequences", {})
                for seq_name, s_data in sequences_data.items():
                    if not isinstance(s_data, dict) or "name" not in s_data:
                        continue
                    seq = Sequence(s_data["name"])

                    for step_entry in s_data.get("steps", []):
                        # 従来の1次元構造（辞書型）を自動で同時駆動用のリスト構造にラップして復元
                        if isinstance(step_entry, dict):
                            m_name = step_entry.get("motor_name") or step_entry.get(
                                "motor"
                            )
                            m_obj = self.motors.get(m_name)
                            if m_obj:
                                seq.steps.append(
                                    [
                                        SequenceStep(
                                            motor=m_obj,
                                            dir=step_entry.get("dir", 1),
                                            duty=step_entry.get("duty", 0),
                                            timeout=step_entry.get("timeout", 0),
                                            target=step_entry.get("target", -1),
                                        )
                                    ]
                                )
                        # 同時駆動対応の2次元構造（リスト型）のパース
                        elif isinstance(step_entry, list):
                            parallel_list = []
                            for sub in step_entry:
                                if isinstance(sub, dict):
                                    m_name = sub.get("motor_name") or sub.get("motor")
                                    m_obj = self.motors.get(m_name)
                                    if m_obj:
                                        parallel_list.append(
                                            SequenceStep(
                                                motor=m_obj,
                                                dir=sub.get("dir", 1),
                                                duty=sub.get("duty", 0),
                                                timeout=sub.get("timeout", 0),
                                                target=sub.get("target", -1),
                                            )
                                        )
                            if parallel_list:
                                seq.steps.append(parallel_list)

                    self.sequences[seq.name] = seq

                slot_data = data.get("slots", {})
                for slot_str, seq_name in slot_data.items():
                    try:
                        slot_idx = int(slot_str)
                        if seq_name in self.sequences:
                            self.export_slots[slot_idx] = self.sequences[seq_name]
                        elif seq_name == "None":
                            self.export_slots[slot_idx] = None
                    except Exception:
                        pass

    def save_all(self):
        # 保存先ディレクトリの自動生成（エラー防止）
        os.makedirs("json", exist_ok=True)

        # 1. json/motor.json の保存
        motors_data = []
        for m in self.motors.values():
            motors_data.append({"name": m.name, "canID": m.canID})
        motor_path = os.path.join("json", "motor.json")
        with open(motor_path, "w", encoding="utf-8") as f:
            json.dump(motors_data, f, indent=4, ensure_ascii=False)

        # 2. json/sequence.json の保存
        data = {"sequences": {}, "slots": {}}
        for seq in self.sequences.values():
            seq_data = {"name": seq.name, "steps": []}
            for parallel_step in seq.steps:
                parallel_data = []
                for step in parallel_step:
                    parallel_data.append(
                        {
                            "motor_name": step.motor.name,
                            "dir": step.dir,
                            "duty": step.duty,
                            "timeout": step.timeout,
                            "target": step.target,
                        }
                    )
                seq_data["steps"].append(parallel_data)
            data["sequences"][seq.name] = seq_data

        for slot_idx, seq in self.export_slots.items():
            data["slots"][str(slot_idx)] = seq.name if seq else "None"

        seq_path = os.path.join("json", "sequence.json")
        with open(seq_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.has_changes = False

    def export_csv(self):
        # 1スロットにつき10行 × 9スロット ＝ 合計90行の縦並びリストを生成
        csv_lines = []

        for slot_idx in range(1, 10):
            seq = self.export_slots.get(slot_idx)
            for step_idx in range(10):
                # シーケンスが割り当てられており、かつ該当ステップが存在する場合
                if seq and step_idx < len(seq.steps):
                    parallel_step = seq.steps[step_idx]
                    parts = []
                    for m_idx, step in enumerate(parallel_step):
                        if m_idx > 0:
                            parts.append(
                                " "
                            )  # 同時ステップの間に半角スペース1つの空白列を挿入

                        # 個々のモータ動作の5パラメータをカンマで結合
                        step_parts = [
                            str(step.motor.canID),
                            str(step.duty),
                            str(step.timeout),
                            str(step.dir),
                            str(step.target) if step.target != -1 else "n",
                        ]
                        parts.append(",".join(step_parts))

                    # 各パーツをさらにカンマで結合
                    csv_lines.append(",".join(parts))
                else:
                    # ★修正：ステップが10個に満たない空き枠、または未設定(None)のスロットは "n,n,n,n,n" を出力
                    csv_lines.append("n,n,n,n,n")

        # sequence.csv として縦一列（合計90行）に書き出し
        with open("sequence.csv", "w", newline="", encoding="utf-8") as f:
            for line in csv_lines:
                f.write(line + "\n")
