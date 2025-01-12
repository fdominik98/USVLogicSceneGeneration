from functional_level.metamodels.functional_scenario import FuncObject

class ObjectGenerator():
    def __init__(self) -> None:
        self.__id_count = 0
    
    @property    
    def new_object(self) -> FuncObject:
        id = self.__id_count
        self.__id_count += 1
        return FuncObject(id)