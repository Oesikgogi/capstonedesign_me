from app.core.constants import BooStage


def get_boo_stage(total_score: int) -> BooStage:
    if total_score >= 800:
        return BooStage.GRADUATE
    if total_score >= 300:
        return BooStage.JACKET
    return BooStage.BABY


def get_next_stage(total_score: int) -> tuple[str | None, int | None]:
    if total_score < 300:
        return BooStage.JACKET, 300
    if total_score < 800:
        return BooStage.GRADUATE, 800
    return None, None
