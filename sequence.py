# sequence.py

from typing import List
from motor import Motor


class SequenceStep:
    """シーケンス内の1ステップを表す（モータ参照と個別パラメータを保持）"""

    def __init__(
        self,
        motor: Motor,
        dir: int = 1,
        duty: int = 0,
        timeout: int = 0,
        target: int = -1,
    ):
        self.motor = motor
        self.dir = dir  # 1: CW, 2: CCW
        self.duty = duty  # 0〜100
        self.timeout = timeout  # ms
        self.target = target  # 使用しない場合は -1


class Sequence:
    """複数の動作ステップを時系列順に保持する配列管理クラス（同時3駆動対応）"""

    def __init__(self, name: str = ""):
        self.__name = name
        # 各要素は同時に駆動する SequenceStep のリスト（最大3要素）を格納する2次元リスト
        self.__steps: List[List[SequenceStep]] = []

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def steps(self) -> List[List[SequenceStep]]:
        return self.__steps

    def add_step(self, step: SequenceStep) -> bool:
        """末尾に新しいタイムラインステップを追加（最大10ステップ制限）"""
        if len(self.__steps) >= 10:
            return False
        self.__steps.append([step])
        return True

    def remove_step(self, index: int) -> bool:
        """指定位置のタイムラインステップ（同時駆動の塊ごと）を削除して自動上詰め"""
        if 0 <= index < len(self.__steps):
            self.__steps.pop(index)
            return True
        return False

    def to_dict(self) -> dict:
        """同時駆動の2次元配列構造に対応した辞書オブジェクトへの変換"""
        return {
            "name": self.__name,
            "steps": [
                [
                    {
                        "motor_name": sub_step.motor.name,  # "motor_name" に統一
                        "dir": sub_step.dir,
                        "duty": sub_step.duty,
                        "timeout": sub_step.timeout,
                        "target": sub_step.target,
                    }
                    for sub_step in parallel_step
                ]
                for parallel_step in self.__steps
            ],
        }
