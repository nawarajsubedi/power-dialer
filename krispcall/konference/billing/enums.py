from enum import IntEnum


class BillingTypeEnum(IntEnum):
    SIP_CHARGE = 0
    CONFERENCE_CHARGE = 1
    CALL_CHARGE = 2


class ConferencParticipantEnum(IntEnum):
    DEFAULT_TOTAL_PARTICIPANTS = 2
