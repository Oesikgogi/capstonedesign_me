from enum import StrEnum


class BooStage(StrEnum):
    BABY = "BABY"
    JACKET = "JACKET"
    GRADUATE = "GRADUATE"


STAGE_THRESHOLDS = {
    BooStage.BABY: 0,
    BooStage.JACKET: 300,
    BooStage.GRADUATE: 800,
}


QUIZ_DEFAULT_SCORE = 50
MEAL_DEFAULT_SCORE = 30
