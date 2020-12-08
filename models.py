import datetime
from data_base import DataBase
from pydantic import BaseModel, validator


# --------------------------------------------------------------
# Simple class-collection of all models (requests and responses).
# Inheritance from BaseModel from pydantic module.
#
# Request Models contains validators to check input data.
# If input is wrong, no records to DataBase are made.
# --------------------------------------------------------------
class Models:

    # ----------------------------------
    # Model of /add request to work with.
    # ----------------------------------
    class AddRequestModel(BaseModel):
        phrase: str
        region: str

        # -----------------------------------------------------------------
        # If some special symbols occurs in *region*, ValueError is raised.
        # -----------------------------------------------------------------
        @validator('region')
        def check_region(cls, reg: str):
            fine_symbols = ['-', '_']

            for symbol in reg:
                if not symbol.isalpha() and symbol not in fine_symbols or len(reg) >= 20 or len(reg) <= 4:
                    raise ValueError(
                        'Region must not contain any strange symbols and be real!'
                    )
            return reg

        # ----------------------------------------------------
        # No checker for special symbols, it depends on client
        # But the length of *phrase* must be \in (0, 30].
        # ----------------------------------------------------
        @validator('phrase')
        def check_phrase(cls, phrase: str):
            if len(phrase) == 0 or len(phrase) > 30:
                raise ValueError('Phrase must contain at least 1 symbol and be shorter than 31 symbol')
            return phrase

    # --------------------------------------------------------------
    # If the request is valid, add it to *Requests* and return id.
    # --------------------------------------------------------------
    class AddSuccessResponseModel(BaseModel):
        id: int

    # --------------------------------------------------------
    # Model of /stat request to work with.
    # --------------------------------------------------------

    class StateRequestModel(BaseModel):
        id: int
        time_from: str
        time_to: str

        # --------------------------------
        # Check if id is in *Requests*
        # --------------------------------
        @validator('id')
        def check_id(cls, idx: int):
            if DataBase.get_size() < idx or idx <= 0:
                raise ValueError("Table does not contain current id")
            return idx

        # --------------------------------------------------------
        # Two time checkers. I decided to use datetime own checker
        # Raise ValueError.
        # --------------------------------------------------------
        @validator('time_from')
        def check_time(cls, f: str):
            x = datetime.datetime.strptime(f, '%Y-%m-%d %H:%M:%S.%f')
            return f

        @validator('time_to')
        def check_time2(cls, f: str):
            x = datetime.datetime.strptime(f, '%Y-%m-%d %H:%M:%S.%f')
            return f

    # ------------------------
    # Unlimited-sized dict
    # ------------------------
    StateSuccessResponseModel = dict

    # ----------------------------------
    # Model of /top request to work with
    # ----------------------------------
    class TopRequestModel(BaseModel):
        id: int
        time_from: str
        time_to: str

        # ---------------------------------
        # Same checkers from State request
        # ---------------------------------
        @validator('id')
        def check_id(cls, idx: int):
            if DataBase.get_size() < idx or idx <= 0:
                raise ValueError("Table does not contain current id")
            return idx

        @validator('time_from')
        def check_time(cls, f: str):
            x = datetime.datetime.strptime(f, '%Y-%m-%d %H:%M:%S.%f')
            return f

        @validator('time_to')
        def check_time2(cls, f: str):
            x = datetime.datetime.strptime(f, '%Y-%m-%d %H:%M:%S.%f')
            return f

    # ------------------------
    # Unlimited-sized dict
    # ------------------------
    TopSuccessResponseModel = dict
