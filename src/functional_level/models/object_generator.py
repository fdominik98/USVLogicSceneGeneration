from functional_level.metamodels.functional_scenario import FuncObject

class IdGenerator():
    def __init__(self) -> None:
        self.__id_count = -1
    
    def next(self) -> int:
        self.__id_count += 1
        return self.__id_count

class ObjectGenerator():
    def __init__(self) -> None:
        self.id_generator = IdGenerator()
    
    @property    
    def new_object(self) -> FuncObject:        
        return FuncObject(self.id_generator.next())