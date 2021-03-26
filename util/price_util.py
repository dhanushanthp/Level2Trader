from config import Config


class PriceUtil:
    def __init__(self):
        self.config = Config()
        self.slot_size = self.config.get_slot_size()

    def slot_convertor(self, size: int):
        """
        Convert the size of slots.
        WARNING: Only use during the visualisation. NOT during the data dictionary aggregation
        :param size:
        :return:
        """
        num_slots = round(size/ self.slot_size)
        return num_slots
