import asyncio
import aiohttp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Character  # Импортируем модель из первого скрипта

API_URL = "https://swapi.py4e.com/api/people/{}/"

# Настройка базы данных
DATABASE_URL = "sqlite+aiosqlite:///star_wars_characters.db"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def fetch_character(session, character_id):
    url = f"https://swapi.py4e.com/api/people/{character_id}/"
    async with session.get(url) as response:
        character_data = await response.json()

        character_data['id'] = character_id

        return character_data


async def fetch_movie(session, film_url):
   async with session.get(film_url) as response:
        film_data = await response.json()
        return film_data['title']


async def fetch_species(session, species_url):
    async with session.get(species_url) as response:
        species_data = await response.json()
        return species_data['name']


async def fetch_starships(session, starships_url):
    async with session.get(starships_url) as response:
        starships_data = await response.json()
        return starships_data['name']


async def fetch_vehicles(session, vehicles_url):
    async with session.get(vehicles_url) as response:
        vehicles_data = await response.json()
        return vehicles_data['name']


# async def fetch_homeworld(session, homeworld_url):
#     async with session.get(homeworld_url) as response:
#         homeworld_data = await response.json()
#         print(homeworld_data)
#         return homeworld_data['name']


async def save_character(character_data, session):
    character = Character(
        id=character_data['id'],
        birth_year=character_data['birth_year'],
        eye_color=character_data['eye_color'],
        films=character_data['films'],
        gender=character_data['gender'],
        hair_color=character_data['hair_color'],
        height=character_data['height'],
        homeworld=character_data['homeworld'],
        mass=character_data['mass'],
        name=character_data['name'],
        skin_color=character_data['skin_color'],
        species=character_data['species'],
        starships=character_data['starships'],
        vehicles=character_data['vehicles']
    )

    session.add(character)
    await session.commit()


async def main():
    async with aiohttp.ClientSession() as session:
        async with SessionLocal() as db_session:
            character_ids = range(1, 83)  # Будем извлекать персонажей с ID от 1 до 82

            tasks = []
            for character_id in character_ids:
                tasks.append(fetch_character(session, character_id))

            characters = await asyncio.gather(*tasks)

            for character_data in characters:
                film_title_tasks = []
                film_urls = character_data.get('films', [])
                film_title_tasks = [fetch_movie(session, film_url) for film_url in film_urls]
                film_titles = await asyncio.gather(*film_title_tasks)
                film_titles_str = ', '.join(film_titles)
                character_data['films'] = film_titles_str

                species_tasks = []
                species_urls = character_data.get('species')
                species_tasks = [fetch_species(session, species_url) for species_url in species_urls]
                species_name = await asyncio.gather(*species_tasks)
                species = ', '.join(species_name)
                character_data['species'] = species

                starships_tasks = []
                starships_urls = character_data.get('starships')
                starships_tasks = [fetch_starships(session, starships_url) for starships_url in starships_urls]
                starships_name = await asyncio.gather(*starships_tasks)
                starships = ', '.join(starships_name)
                character_data['starships'] = starships

                vehicles_tasks = []
                vehicles_urls = character_data.get('vehicles')
                vehicles_tasks = [fetch_vehicles(session, vehicles_url) for vehicles_url in vehicles_urls]
                vehicles_name = await asyncio.gather(*vehicles_tasks)
                vehicles = ', '.join(vehicles_name)
                character_data['vehicles'] = vehicles
                #
                # homeworld_tasks = []
                # homeworld_urls = character_data.get('homeworld')
                # homeworld_tasks = [fetch_homeworld(session, homeworld_url) for homeworld_url in homeworld_urls]
                # homeworld_name = await asyncio.gather(*homeworld_tasks)
                # homeworld = ', '.join(homeworld_name)
                # character_data['homeworld'] = homeworld
                print(character_data)
                await save_character(character_data, db_session)



if __name__ == "__main__":
    asyncio.run(main())