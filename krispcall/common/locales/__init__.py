import gettext
from pathlib import Path


def init_translation():
    # Initializing all language and storing instances on context
    available_languages = ["es", "da", "de", "fr"]
    context = {}
    localedir = Path(__file__).parent
    for language in available_languages:
        action = gettext.translation(
            "base",
            localedir=str(localedir),
            languages=[language],
        )
        action.install()
        context[language] = action.gettext
    context["en"] = gettext.gettext
    return context
