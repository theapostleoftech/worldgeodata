import pytest

from app.services import geo_service


class DummyResult:
    def __init__(self, rows):
        self._rows = rows

    def __iter__(self):
        return iter(self._rows)


class DummyScalarResult:
    def __init__(self, rows):
        self.rows = rows

    def __iter__(self):
        return iter(self.rows)


class DummyDivision:
    def __init__(self, name: str):
        self.name = name


class DummyDB:
    def __init__(self):
        self.executed = []
        self.scalars_calls = 0

    async def scalar(self, _):
        return 0

    async def execute(self, query):
        self.executed.append(str(query))
        class Row:
            def __init__(self, data):
                self._mapping = data
        return DummyResult([Row({"entity_type": "city", "id": 1, "name": "Lagos", "score": 100, "country_id": 1, "parent_id": 2})])

    async def scalars(self, _):
        self.scalars_calls += 1
        return DummyScalarResult([DummyDivision("Ikeja LGA"), DummyDivision("Epe LGA")])


@pytest.mark.asyncio
async def test_weighted_search_prioritizes_city_schema_shape():
    db = DummyDB()
    total, rows = await geo_service.weighted_search(db, query="lagos", page=1, page_size=20)
    assert total == 0
    assert rows[0]["entity_type"] == "city"
    assert rows[0]["name"] == "Lagos"


@pytest.mark.asyncio
async def test_get_lgas_by_state_returns_rows():
    db = DummyDB()
    rows = await geo_service.get_lgas_by_state(db, state_id=10)
    assert len(rows) == 2
    assert rows[0].name == "Ikeja LGA"
