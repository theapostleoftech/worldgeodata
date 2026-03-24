# Global Geo Repository System

Production-grade, extensible geo data infrastructure that supports dynamic administrative hierarchies globally, including explicit Nigeria LGA support.

## 1. System architecture

- Backend: FastAPI (async), SQLAlchemy async ORM, PostgreSQL/PostGIS, Redis cache, Celery workers
- Frontend: Next.js App Router, TailwindCSS, TanStack Query, Leaflet map view
- Deployment: Docker Compose with Nginx reverse proxy
- CI/CD: GitHub Actions for backend compile check and frontend build
- Multi-tenant readiness: service layer and data models are tenant-extensible via additional tenant keys in future migrations

### Flexible hierarchy model

The model is dynamic and does not hardcode a fixed country structure:

- Country -> AdminDivision(level=1...) -> AdminDivision(level=n) -> City
- `AdminDivision` is self-referencing (`parent_id`) and typed (`state`, `lga`, `county`, etc.)

Examples represented:

- Nigeria: Country -> State -> LGA -> City/Town
- USA: Country -> State -> County -> City
- UK: Country -> County -> District -> City

## 2. Backend implementation

Key API base path:

- `/api/v1/geo`

Endpoints:

- Countries: `GET /countries`, `GET /countries/{id}`, `GET /countries/iso/{iso2}`
- Divisions: `GET /countries/{country_id}/divisions`, `GET /divisions/{id}`, `GET /divisions/{id}/children`, `GET /divisions/{id}/cities`
- Nigeria convenience: `GET /states/{id}/lgas`, `GET /lgas/{id}/cities`
- Cities: `GET /cities`, `GET /cities/{id}`
- Search: `GET /search?q=lagos` with weighted ranking `City > LGA/County > State > Country`
- Geo features: `GET /nearby`, `GET /reverse-geocode`

Security and performance:

- API key verification for write traffic
- In-memory rate limiting guard
- Redis caching for countries/divisions/cities payloads
- Pagination support for list endpoints
- Indexes on name, parent_id, country_id, level

## 3. Data ingestion pipeline

Sources:

- https://raw.githubusercontent.com/temikeezy/nigeria-geojson-data/master/data/full.json
- https://github.com/dr5hn/countries-states-cities-database
- https://countrystatecity.in/

What ingestion does:

- Fetches source JSON datasets
- Normalizes into one schema
- Dynamically sets administrative levels
- Deduplicates countries/divisions/cities
- Preserves referential integrity
- Tracks duplicates/inconsistencies in ingestion logs

Run seed:

```bash
cd backend
python manage.py seed_geo_data
```

Reset + reseed:

```bash
cd backend
python manage.py seed_geo_data --reset
```

Create DB tables:

```bash
cd backend
python scripts/create_tables.py
```

## 4. Frontend implementation

Routes:

- `/` overview
- `/countries` country list
- `/explorer` dynamic cascading selector
- `/cities` city explorer
- `/search` weighted search UI
- `/map` map visualization

Dynamic selector behavior:

- Country -> Division Level 1 -> Division Level 2 -> Optional Level 3 -> City list

## 5. Deployment

Local deployment via Docker:

```bash
docker compose up --build
```

Services:

- PostGIS DB
- Redis
- FastAPI backend
- Celery worker
- Next.js frontend
- Nginx reverse proxy

## 6. Future improvements

- Add GraphQL gateway (Ariadne or Strawberry)
- Add true Redis/Lua distributed rate limiter
- Add tenant isolation columns and row-level policies
- Add versioned dataset snapshots and delta ingestion
- Add language localization tables
- Add PostGIS geometry columns and spatial indexes
- Add robust conflict resolution with confidence scoring
- Add full test suite with ephemeral Postgres containers