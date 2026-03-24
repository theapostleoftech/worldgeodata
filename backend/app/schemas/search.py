from app.schemas.common import ORMModel


class SearchResultOut(ORMModel):
    entity_type: str
    id: int
    name: str
    score: int
    country_id: int | None = None
    parent_id: int | None = None
