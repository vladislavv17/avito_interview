import asyncio
from models import Models
from fastapi import FastAPI
from data_base import DataBase
from avito_parser import async_refresh
from fastapi_utils.tasks import repeat_every


app = FastAPI(title="Avito interview task",
              version="beta 0.0.2",
              description="""

              Доброго времени суток!

              Мой сервис предоставляет следующие методы:

              - **/add**: добавляет запрос в базу;

              - **/stat**: выдает статистику по запросу за временной интервал (кол-во объявлений);

              - **/top5**: выдает статистику по запросу за временной интервал (топ 5 объявлений).

              """
              )

db = DataBase()


# -------------------------------------------------------
# Add request from requirement
# The new record in "Requests" is formed
# Then add record in the "Logs" table
# After birth our request will be resending once per hour
# -------------------------------------------------------
@app.post(
    "/add", tags=['Add request'],
    description="""
    На вход подается поисковый запрос (формат задан). 
    Необходимо указать 'phrase' - поисковую фразу и 'region' - регион.
    Пример ввода:
    {"phrase": "Iphone 12 Max Pro", "region": "moskva"}
    Запросы, которые не соотвествуют реальному формату (например, регионы, состоящие из цифр),
    обработаны не будут!
    """,
    response_description="Уникальный идентификатор для данного запроса",
    response_model=Models.AddSuccessResponseModel
)
async def add_request(request: Models.AddRequestModel):
    unique_id = await db.add_request(request.phrase, request.region)
    return {"id": unique_id}


# ------------------------------------------------------
# State request from requirement
# Check logs for current *id* in the given time interval
# ------------------------------------------------------
@app.post(
    "/state", tags=['Get ads count statistics '],
    description="""
    На вход подается запрос на получение статистики по уникальному идентификатору.

    Необходимо указать: "id" - идентификатор, "time_from", "time_to" - интервал времени.
    Время указывается в формате 'год-месяц-день часы:минуты:секунды.fraction'

    Составленный неверно запрос вызовет ошибку!
    """,
    response_description="Статистика по данному **id** с указанием количества объявлений",
    response_model=Models.StateSuccessResponseModel
)
async def ads_count_state(req: Models.StateRequestModel):
    res = await db.get_ads_statistics(req.id, req.time_from, req.time_to)
    return res


# ------------------------------------------------------
# Top5 request from requirement
# Check logs for current *id* in the given time interval
# ------------------------------------------------------
@app.post(
    "/top", tags=['Get top 5 ads statistics'],
    description="""
    На вход подается запрос на получение статистики по уникальному идентификатору.

    Необходимо указать: "id" - идентификатор, "time_from", "time_to" - интервал времени.
    Время указывается в формате 'год-месяц-день часы:минуты:секунды.fraction'

    Составленный неверно запрос вызовет ошибку!
    """,
    response_description="Статистика по данному **id** с указанием ссылок на топ 5 объявлений",
    response_model=Models.TopSuccessResponseModel
)
async def top5_state(req: Models.TopRequestModel):
    res = await db.get_ads_statistics(req.id, req.time_from, req.time_to, option="top5")
    return res


# ----------------------------
# Refresh all of our requests.
# Add new records to logs.
# ----------------------------
@app.on_event("startup")
@repeat_every(seconds=60 * 60)
def remove_expired_tokens_task():
    asyncio.run(async_refresh(database=db))

# ------------------------------------
# Run FastAPI app: $ uvicorn main:app
# ------------------------------------
