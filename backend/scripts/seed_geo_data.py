import argparse
import asyncio

from app.db.session import AsyncSessionLocal
from app.services.ingestion_service import seed_geo_data


async def _run(reset_first: bool):
    async with AsyncSessionLocal() as session:
        stats = await seed_geo_data(session, reset_first=reset_first)
        print(stats)


def main():
    parser = argparse.ArgumentParser(description="Seed global geo data with flexible hierarchy")
    parser.add_argument("--reset", action="store_true", help="Delete existing geo data before seeding")
    args = parser.parse_args()
    asyncio.run(_run(reset_first=args.reset))


if __name__ == "__main__":
    main()
"""Seed database with geo data."""
import asyncio
import json
import logging
import httpx
from app.db.database import AsyncSessionLocal
from app.utils.ingestion import GeoDataIngester

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data source URLs
NIGERIA_LGA_URL = "https://raw.githubusercontent.com/temikeezy/nigeria-geojson-data/master/data/full.json"


async def seed_nigeria_lgas():
    """Seed Nigeria LGA data."""
    logger.info("Fetching Nigeria LGA data...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(NIGERIA_LGA_URL)
            response.raise_for_status()
            nigeria_data = response.json()
        
        logger.info(f"Fetched {len(nigeria_data.get('features', []))} features")
        
        async with AsyncSessionLocal() as db:
            logger.info("Ingesting Nigeria LGA data...")
            await GeoDataIngester.ingest_nigeria_lgas(db, nigeria_data)
            logger.info("✅ Nigeria LGA data ingested successfully")
    
    except Exception as e:
        logger.error(f"❌ Failed to seed Nigeria data: {e}")
        raise


async def seed_sample_countries():
    """Seed sample countries data for testing."""
    from app.schemas import CountryCreate, AdminDivisionCreate, CityCreate
    from app.services import CountryService, AdminDivisionService, CityService
    
    logger.info("Seeding sample countries data...")
    
    sample_countries = [
        {
            "name": "United States",
            "iso2": "US",
            "iso3": "USA",
            "phone_code": "+1",
            "capital": "Washington, D.C.",
            "currency": "USD",
        },
        {
            "name": "United Kingdom",
            "iso2": "GB",
            "iso3": "GBR",
            "phone_code": "+44",
            "capital": "London",
            "currency": "GBP",
        },
        {
            "name": "Canada",
            "iso2": "CA",
            "iso3": "CAN",
            "phone_code": "+1",
            "capital": "Ottawa",
            "currency": "CAD",
        },
    ]
    
    async with AsyncSessionLocal() as db:
        for country_data in sample_countries:
            existing = await CountryService.get_by_iso2(db, country_data["iso2"])
            if not existing:
                await CountryService.create(db, CountryCreate(**country_data))
                logger.info(f"Created country: {country_data['name']}")


async def main():
    """Main seeding function."""
    logger.info("🌍 Starting geo data seeding...")
    
    try:
        # Seed sample countries
        await seed_sample_countries()
        
        # Seed Nigeria LGA data
        await seed_nigeria_lgas()
        
        logger.info("✅ All data seeded successfully!")
    
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
