# モータの基本情報を表す


class Motor:
    def __init__(self, name: str, canID: int):
        self.__name = name
        self.__canID = canID

    @property
    def name(self) -> str:
        return self.__name

    @property
    def canID(self) -> int:
        return self.__canID

    def to_dict(self) -> dict:
        return {"name": self.__name, "canID": self.__canID}
