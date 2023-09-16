import requests
import asyncpg
from database.db_operations import  insert_pokemon_with_type

async def api_scrapper(pg_database,pg_user,phase=None):

    url = "https://pokeapi.co/api/v2/pokemon/?limit=260"

    if phase:
        if phase== "Phase1":
            offset= 0
            field_name= "phase_1_complete"
        elif phase == "Phase2":
            offset= 260
            field_name= "phase_2_complete"

        elif phase == "Phase3":
            offset= 520
            field_name= "phase_3_complete"

        elif phase == "Phase4":
            field_name= "phase_4_complete"
            offset= 780
        elif phase == "Phase5":
            field_name= "phase_5_complete"
            offset= 1040

        url += f"&offset={offset}"
        response = requests.get(url)
        data = response.json()
        conn = await asyncpg.connect(user=pg_user, database=pg_database)

        for pokemon in data["results"]:
            pokemon_name = pokemon["name"]
            pokemon_id = await conn.fetchval('SELECT id FROM pokemon WHERE title = $1', pokemon_name)
            if not pokemon_id:
                image,types=get_image_and_types(pokemon["url"])   
                await insert_pokemon_with_type(conn,pokemon_name,image,types)
        
        query = f"UPDATE fetch_info SET {field_name} = True WHERE id = 1"
        await conn.execute(query
        )
        return True


def get_image_and_types(pokemon_url):
    response = requests.get(pokemon_url)
    data = response.json()
    types = []
    for type in data["types"]:
        types.append(type["type"]["name"])
    image = data["sprites"]["other"]["official-artwork"]["front_default"]
    return image,types