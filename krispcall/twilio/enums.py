from enum import Enum


class ActiveStatusEnum(Enum):
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    QUEUED = "queued"


class NotActiveStatusEnum(Enum):
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"
