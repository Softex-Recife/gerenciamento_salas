class Event:
    def __init__(self, tipo, begin, end, room, id_reserva, name, phone, obs, emails):
        self.__tipo = tipo
        self.__end = end
        self.__begin = begin
        self.__room = room
        self.__id_reserva = id_reserva
        self.__name = name
        self.__phone = phone
        self.__obs = obs
        self.__emails = emails
        self.__senha = id_reserva[0:4]
    
    def get_tipo(self):
        return self.__tipo

    def get_begin(self):    
        return self.__begin

    def get_end(self):    
        return self.__end

    def get_room(self):    
        return self.__room

    def get_id_reserva(self):    
        return self.__id_reserva

    def get_name(self):    
        return self.__name

    def get_phone(self):    
        return self.__phone

    def get_obs(self):    
        return self.__obs

    def get_emails(self):    
        return self.__emails

    def get_senha(self):    
        return self.__senha

    def __str__(self):
        return f"{self.__tipo},{self.__begin}, {self.__end} , {self.__room}, {self.__id_reserva}, {self.__name}, {self.__phone}, {self.__obs}, {self.__emails}"
        