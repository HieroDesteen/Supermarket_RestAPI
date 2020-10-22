from enum import Enum


class OrderChoices(str, Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    PAID = 'paid'

    @classmethod
    def choices(self):
        return tuple((x.value, x.name) for x in self)

    def __str__(self):
        return self.value
