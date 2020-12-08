import re
import asyncio
# ------------------------------------------------
# Seems weirdly to import so large framework
# And use the only function...
# But it was made for async checking statistics
# ------------------------------------------------
import aiohttp
from bs4 import BeautifulSoup


# ------------------------------------
# HTML downloaded page parser.
# Use of BeautifulSoup.
# Returns number of pages for request.
# ------------------------------------
def parse_response(response, block_name='span', class_='page-title-count-1oJOc'):
    if "Доступ временно заблокирован" in response:
        return None, "Avito blocks connection"

    soup = BeautifulSoup(response, 'html.parser')
    count_ads = soup.findAll(block_name, class_=class_)

    block_name = 'div'
    class_ = 'iva-item-titleStep-2bjuh'

    ads = ''.join(map(str, soup.findAll(block_name, class_=class_)))
    soup = BeautifulSoup(ads, 'html.parser')
    ads = ["https://www.avito.ru" + a['href'] for a in soup.find_all('a', href=True)]

    if len(count_ads) == 0:
        return 0, ""
    if len(ads) > 4:
        ads = ads[:5]
    return re.compile(r'\d+').findall(str(count_ads))[-1], ' '.join(ads)


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


# ---------------------------------
# Single parser.
# Used when we add NEW request
# To *Requests* db.
# ---------------------------------
async def single_parser(phrase: str, region: str, parser=parse_response, url_model="https://www.avito.ru/{}/?q={}"):
    url = url_model.format('-'.join(region.split()), '+'.join(phrase.split()))
    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url)

    return parser(response)


# ----------------------------------
# Async sending requests to Avito
# From *Requests* db. Adding result
# For all of the requests to *Logs*
# ----------------------------------
async def run_async(database):
    regions = database.get_all_regions()
    phrases = database.get_all_phrases()
    url_model = "https://www.avito.ru/{}/?q={}"

    urls = [url_model.format(regions[i], phrases[i]) for i in range(len(regions))]

    # ------------------------------------------------
    # Risky step but what if I suppose
    # That futures will be placed in the right order?
    # ------------------------------------------------
    tasks = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(fetch(session, url))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # --------------------------------------------
        # Sync variant of adding all responses to logs
        # --------------------------------------------
        for i in range(len(regions)):
            await database.add_log(unique_id=i + 1, response=responses[i])


# ------------------------------------------
# Coroutine to refresh requests in database.
# ------------------------------------------
async def async_refresh(database):
    await run_async(database)
