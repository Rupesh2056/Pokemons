Setup Guide:

1. Setup a virtual python environment inside the project directory.
    -> python3 -m venv venv

2. Activte the virtual environment
    -> source venv/bin/activate (for linux)

3. Install requirements.
    -> pip install -r requirements.txt

4. Make the .env file in the project directory (where the main.py file is located)to configure the database
    -> nano .env
    -> Configure the environment file with appropriate variables. (follow sample_env.txt for reference)

.Run the project
    -> uvicorn main:app --reload --loop asyncio



Project Briefing.

I have splitted the data retrieval part to five different phases such that each phases (first 4) gets 260 new pokemons and
the last phase retrieves the remaining pokemons into our database. You can simply retrieve any phase, wait untill the loading is finished and new pokemons are displayed. 

Steps:
    1. Go to the url "http://127.0.0.1:8000/v1/pokemon/"
    2. Fetch data from any phase buttons.
    3. AS soon as the data is fetched (takes around 1 minutes), the page reloads itself and displays the pokemon.  
