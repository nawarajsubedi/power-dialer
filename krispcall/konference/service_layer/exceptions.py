class CampaignConversationNotFound(Exception):
    pass


class ConferenceNotInProgress(Exception):
    pass


class CallNotInProgress(Exception):
    pass


class ConferenceNotFoundInTwilio(Exception):
    pass


class ConferenceAlreadyCompleted(Exception):
    pass
