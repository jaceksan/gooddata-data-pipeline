from enum import Enum

class AppMode(Enum):
    INSIGHT_VIEWER="Insight Viewer"
    INSIGHT_BUILDER="Insight Builder"

APP_MODES = [AppMode.INSIGHT_VIEWER.value, AppMode.INSIGHT_BUILDER.value]
