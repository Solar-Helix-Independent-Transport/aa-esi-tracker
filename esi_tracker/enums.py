from enum import IntEnum

class ESIStatus(IntEnum):
  RED  = 1
  YELLOW = 2
  GREEN = 3
  
  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]
