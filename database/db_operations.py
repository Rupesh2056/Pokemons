
from .models import pokemon_type_association,Pokemon,Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from decouple import config

# function that takes name,image_url, and type_names(list) and inserts them into the database table
async def insert_pokemon_with_type(connection,pokemon_name,image_url, type_names):
    try:
        # check if the pokemon instance has already been created.
        pokemon_id = await connection.fetchval('SELECT id FROM pokemon WHERE title = $1', pokemon_name)

        if not pokemon_id:
            pokemon_created = False

            for type_name in type_names:
                 # Check if the Type with the given name exists
                type_id = await connection.fetchval('SELECT id FROM type WHERE name = $1', type_name)

                if type_id:
                    # If the Type exists, insert a new Pokemon associated with it
                    pokemon_id = await connection.fetchval('SELECT id FROM pokemon WHERE title = $1', pokemon_name)

                    if not pokemon_created:
                        # create the pokemon first 
                        await connection.execute('INSERT INTO pokemon (title,image) VALUES ($1,$2)', pokemon_name,image_url)
                        pokemon_id = await connection.fetchval('SELECT id FROM pokemon WHERE title = $1', pokemon_name)
                        pokemon_created = True
                        
                    else:
                        # the pokemon has already been created, so just retrieve it
                        pokemon_id = await connection.fetchval('SELECT id FROM pokemon WHERE title = $1', pokemon_name)
                        pokemon_created = True
                    
                    # create the association if pokemon with the current type
                    await connection.execute('INSERT INTO pokemon_type_association (pokemon_id, type_id) VALUES ($1, $2)', pokemon_id, type_id)
                
                else:
                    # the Type doesn't exist,so insert it first
                    await connection.execute('INSERT INTO type (name) VALUES ($1)', type_name)

                    # get the newly created Type's ID
                    type_id = await connection.fetchval('SELECT id FROM type WHERE name = $1', type_name)


                    if not pokemon_created:
                        await connection.execute('INSERT INTO pokemon (title,image) VALUES ($1,$2)', pokemon_name,image_url)
                        pokemon_id = await connection.fetchval('SELECT id FROM pokemon WHERE title = $1', pokemon_name)                 
                        # Insert the new Pokemon associated with the newly created Type
                        await connection.execute('INSERT INTO pokemon_type_association (pokemon_id, type_id) VALUES ($1, $2)', pokemon_id, type_id)
                        pokemon_created = True
                    else:
                        pokemon_id = await connection.fetchval('SELECT id FROM pokemon WHERE title = $1', pokemon_name)     
                        await connection.execute('INSERT INTO pokemon_type_association (pokemon_id, type_id) VALUES ($1, $2)', pokemon_id, type_id)            
                    print("Data inserted successfully!")
            

    except Exception as e:
        print("exception-----------------------")
        print(f"Error: {e}")




POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_HOST = config("POSTGRES_HOST")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
DATABASE_NAME = config("DATABASE_NAME")

# SQLAlchemy engine with the asyncpg driver
engine = create_async_engine(f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{DATABASE_NAME}", echo=True)

# Create an async session
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# retrieves all the pokemon datas in our requireed format.
async def get_all_pokemon_data(pokemon_name: str = None, type_name: str = None):
    async with async_session() as session:
        stmt = select(Pokemon).select_from(Pokemon)

        # Join the necessary tables and specify the join conditions
        stmt = stmt.join(pokemon_type_association).join(Type)

        if pokemon_name:
            stmt = stmt.filter(Pokemon.title.ilike(f"%{pokemon_name}%"))
            
        if type_name:
            stmt = stmt.filter(Type.name.ilike(f"%{type_name}%"))

        result = await session.execute(stmt)
        pokemon_data = result.fetchall()

        # dictionary to store Pokemon data by id to avoid duplicates
        pokemon_data_dict = {}

        for pokemon in pokemon_data:
            pokemon_id = pokemon[0].id
            name = pokemon[0].title
            image_url = pokemon[0].image

            #subquery to fetch the associated types
            types_subquery = select(Type.name).filter(
                (pokemon_type_association.c.pokemon_id == pokemon_id) &
                (Type.id == pokemon_type_association.c.type_id)
            )
            types_result = await session.execute(types_subquery)

            # Deduplicate and filter types that belong to the pokemon
            types = set()
            for type_ in types_result.fetchall():
                types.add(type_[0])

            # Create or update the pokemon data in the dictionary
            if pokemon_id not in pokemon_data_dict:
                pokemon_data_dict[pokemon_id] = {
                    'name': name,
                    'image_url': image_url,
                    'types': list(types), 
                }
            else:
                # If the pokemon already exists in the dictionary, update its types
                existing_types = pokemon_data_dict[pokemon_id]['types']
                existing_types.extend(types)
                pokemon_data_dict[pokemon_id]['types'] = list(set(existing_types))

        pokemon_data_list = list(pokemon_data_dict.values())

        return pokemon_data_list