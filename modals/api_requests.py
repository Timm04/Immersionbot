import aiohttp
import logging
import asyncio
from discord import app_commands

log = logging.getLogger(__name__)

async def vndb_autocomplete(query: str):
    url = 'https://api.vndb.org/kana/vn'
    data = {'filters': ['search', '=', f'{query}'], 'fields': 'title, alttitle'}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            log.info(resp.status)
            json_data = await resp.json()

            suggestions = [(result['title'], result['id']) for result in json_data['results']]
            return [app_commands.Choice(name=title, value=str(id)) for title, id in suggestions if query.lower() in title.lower()]

async def anilist_autocomplete(query: str, media_type: str):
    url = 'https://graphql.anilist.co'
    graphql_query = f'''
    query ($page: Int, $perPage: Int, $title: String) {{
        Page(page: $page, perPage: $perPage) {{
            media (search: $title, type: {media_type.upper()}) {{
                id
                title {{
                    romaji
                    native
                }}
            }}
        }}
    }}
    '''
    variables = {'title': query, 'page': 1, 'perPage': 10}
    data = {'query': graphql_query, 'variables': variables}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            log.info(resp.status)
            json_data = await resp.json()

            suggestions = [(f"{result['title']['romaji']} ({result['title']['native']})", result['id']) for result in json_data['data']['Page']['media']]
            return [app_commands.Choice(name=title, value=str(id)) for title, id in suggestions if query.lower() in title.lower()]

async def tmdb_autocomplete(query: str, tmdb_api_key: str):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api_key}&query={query}"
    params = {"api_key": tmdb_api_key, "query": query}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            log.info(f"Status: {resp.status}")
            json_data = await resp.json()

            if 'results' in json_data:
                suggestions = [
                    (result.get('name') or result.get('title'), result.get('original_title'), result.get('original_language'), result['id'], result['media_type'], result.get('poster_path'))
                    for result in json_data['results']
                ]
            
            await asyncio.sleep(0)
            
            return [
                app_commands.Choice(name=f'{org_lan}: {title} ({org_title}) ({media_type})', value=str([id, media_type, f'{poster}']))
                for title, org_title, org_lan, id, media_type, poster in suggestions if query.lower() in title.lower()
            ]
