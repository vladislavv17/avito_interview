import datetime
from avito_parser import parse_response, single_parser
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, types


class DataBase:
    __engine = create_engine(
        'sqlite:///AvitoRequests.db',
        echo=True,
        connect_args={'check_same_thread': False}
    )

    __meta = MetaData()

    # -----------------------------------------
    # Table *Requests*.
    # Contains all requests: |id|phrase|region|
    # -----------------------------------------
    __requests = Table(
        'Requests', __meta,
        Column('id', Integer, primary_key=True),
        Column('phrase', String),
        Column('region', String),
    )

    # -----------------------------------------------------
    # Table *Logs*.
    # Contains all logs: |id|unique_id|time|ads_count|top5|
    # -----------------------------------------------------
    __logs = Table(
        'Logs', __meta,
        Column('id', Integer, primary_key=True),
        Column('unique_id', Integer),
        Column('time', types.DateTime),
        Column('ads_count', Integer),
        Column('top5', String)
    )
    # ------------------------------------
    # Create database. Create both tables.
    # ------------------------------------
    __meta.create_all(__engine)

    # -----------------------------------------------
    # Add request in *Requests* and mark it in *Logs*
    # -----------------------------------------------
    async def add_request(self, phrase: str, region: str):

        # Add record to Requests table
        insert = self.__requests.insert().values(phrase=phrase, region=region)
        res = self.__engine.connect().execute(insert)
        unique_id = res.inserted_primary_key[0]

        # Add record to Logs table
        await self.add_log(unique_id, phrase=phrase, region=region)

        return unique_id

    # ---------------------------------------------
    # Get statistics of ads.
    # if option isn't given => get ads count
    # else get top 5 ads.
    # ---------------------------------------------
    async def get_ads_statistics(self, unique_id, time_from, time_to, option="count"):
        f = datetime.datetime.strptime(time_from, '%Y-%m-%d %H:%M:%S.%f')
        t = datetime.datetime.strptime(time_to, '%Y-%m-%d %H:%M:%S.%f')
        select = self.__logs.select().where(self.__logs.c.unique_id == unique_id and f <= self.__logs.c.time <= t)
        result = self.__engine.connect().execute(select).fetchall()

        time_stamps = [a[2] for a in result]
        if option == "count":
            answers = [a[3] for a in result]
        else:
            answers = [a[4] for a in result]

        return dict(zip(time_stamps, answers))

    # -----------------------------------------------------------------
    # Add log in *Logs*.
    # If response is not given => use single_parser to get data
    # Else *add_log* came from async parser and we shall parse response.
    # -----------------------------------------------------------------
    async def add_log(self, unique_id: int, phrase="", region="", response=None):

        if not response:  # Sync Parser
            count, top = await single_parser(phrase, region)
        else:
            count, top = parse_response(response)

        insert = self.__logs.insert().values(unique_id=unique_id,
                                             time=datetime.datetime.now(),
                                             ads_count=count,
                                             top5=top
                                             )
        self.__engine.connect().execute(insert)

    # -----------------------------------
    # List of all phrases in url format.
    # ex: "iphone+X+красный"
    # -----------------------------------
    def get_all_phrases(self):
        select = self.__requests.select().where(self.__requests.c.phrase != "")
        return ['+'.join(a[1].split()) for a in self.__engine.execute(select).fetchall()]

    # ---------------------------------------
    # List of all regions in *Requests* table
    # ---------------------------------------
    def get_all_regions(self):
        select = self.__requests.select().where(self.__requests.c.phrase != "")
        return [a[2] for a in self.__engine.execute(select).fetchall()]

    # --------------------------------------------------
    # Not the most efficient way to get *Requests* size
    # --------------------------------------------------
    @staticmethod
    def get_size():
        select = DataBase.__requests.select().where(DataBase.__requests.c.phrase != "")
        return len(DataBase.__engine.execute(select).fetchall())
