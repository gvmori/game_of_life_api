#!/usr/local/bin/python3

from pydantic import BaseModel

class BoardId(BaseModel):
    board_id: str

class BoardState(BaseModel):
    coordinates: set[tuple[int, int]]  # set of active cell coordinates
