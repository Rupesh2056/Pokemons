import asyncio
import asyncpg
from database.database_setup import connect_create_if_not_exists, create_tables
import nest_asyncio

from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from decouple import config
from fastapi.middleware.cors import CORSMiddleware


from database.db_operations import get_all_pokemon_data
from scrapper import api_scrapper


nest_asyncio.apply()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
v1 = APIRouter()

POSTGRES_USER = config("POSTGRES_USER")
DATABASE_NAME = config("DATABASE_NAME")
templates = Jinja2Templates(directory="templates")


asyncio.get_event_loop().run_until_complete(
    connect_create_if_not_exists(user=POSTGRES_USER, database=DATABASE_NAME)
)

# Call create_tables function to create tables on startup
@app.on_event("startup")
async def startup_event():
    await create_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@v1.get("/pokemon/",response_class=HTMLResponse)
async def get_pokemon_list(request: Request,name: str = None, type: str = None,phase:str=None) :
    conn = await asyncpg.connect(user=POSTGRES_USER, database=DATABASE_NAME)
    # Create an asynchronous SQLAlchemy session
    rows = await conn.fetch("SELECT * FROM pokemon;")
    data = [dict(row) for row in rows]

    record_count = await conn.fetchval("SELECT COUNT(*) FROM fetch_info")

    # If no records exist, create a new row
    if record_count == 0:
        await conn.execute(
            """
            INSERT INTO fetch_info (phase_1_complete, phase_2_complete, phase_3_complete, phase_4_complete, phase_5_complete)
            VALUES ($1, $2, $3, $4, $5)
            """,
            False, False, False, False, False,
        )

    if len(data) == 0:
        context = {
            "btns" : ["Phase1","Phase2","Phase3","Phase4", "Phase5"]
        }

        if phase:
            await api_scrapper(DATABASE_NAME,POSTGRES_USER,phase=phase)
        
        return templates.TemplateResponse("index.html", {"request": request, **context})
        
    else:
        data = await get_all_pokemon_data(name,type)

    fetch_info = await conn.fetch("SELECT * FROM fetch_info WHERE id=1")
    fetch_data = [dict(info) for info in fetch_info ]
    btns = []
    if fetch_data:
        fetch_data = fetch_data[0]
        if not fetch_data["phase_1_complete"]:
            btns.append("Phase1")
        if not fetch_data["phase_2_complete"]:
            btns.append("Phase2")
        if not fetch_data["phase_3_complete"]:
            btns.append("Phase3")
        if not fetch_data["phase_4_complete"]:
            btns.append("Phase4")
        if not fetch_data["phase_5_complete"]:
            btns.append("Phase5")

    context = {
        "pokemons": data,
        "name":name if name else "",
        "type" : type if type else "",
        "btns" : btns
    }
    await conn.close()
    return templates.TemplateResponse("index.html", {"request": request, **context})



@v1.get("/fetch_data/")
async def fetch_api_data(phase:str=None):
    fetched = await api_scrapper(DATABASE_NAME,POSTGRES_USER,phase)
    return {"Fetched":fetched}
app.include_router(v1, prefix="/v1")