from ddd import AggregateRoot, Identity

class User(AggregateRoot):
    def __init__(self, _id: Identity, first_name: str, last_name: str):
        super().__init__(_id)
        self.__first_name = first_name
        self.__last_name = last_name