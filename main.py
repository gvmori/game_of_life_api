#!/usr/local/bin/python3

from fastapi import FastAPI, HTTPException
import uuid
import os
# valkey may or may not be appropriate for this use case, depending
# on expected load, data size, persistence requirements, etc.
import valkey
import json
from lib.board import Board
from lib.models import BoardId, BoardState

## this is entirely arbitrary, would need to reconfigure based on requirements
MAX_ALLOWED_ITERATIONS = 1000

app = FastAPI()
# allow overriding via environment so the app works from docker-compose
# in production we would also use a password pulled from e.g. secrets manager
valkey_host = os.getenv("VALKEY_HOST", "localhost")
valkey_port = int(os.getenv("VALKEY_PORT", "6379"))
pool = valkey.ConnectionPool(host=valkey_host, port=valkey_port, db=0)
v = valkey.Valkey(connection_pool=pool)

@app.post("/boards/", response_model=BoardId)
async def create_board(input_board: BoardState) -> dict:
    ''' Create a new board and store it.
        Returns the unique board ID.
    '''
    # board input format isn't defined, assume a list of (row, col) tuples
    # representing active cells only.
    # a simpler input format could be a dense 2D list, but that would be
    # inefficient for large, sparse boards.

    try:
        board = Board(coordinates=input_board.coordinates)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # use uuid for a unique board id
    # we could use e.g. a hash of the board, but this would cause issues with
    # how we're storing boards right now (id -> current state), meaning duplicate 
    # initial boards would overwrite each other, and would also make get_next_state
    # impossible (you wouldn't know which "next" state to return)
    board_id = str(uuid.uuid4())
 
    # store serialized sparse board in valkey
    v.set(board_id, board.to_string())
    return {"board_id": board_id}


@app.get("/boards/{board_id}/next", response_model=BoardState)
# @app.get("/boards/{board_id}/next")
async def get_next_state(board_id: str) -> dict:
    ''' Get the next state for the given board ID.
        Returns the board state after one iteration.
    '''
    return await _run_board_iterations(board_id, 1)


@app.get("/boards/{board_id}/iterate/{num_iters}", response_model=BoardState)
async def get_state(board_id: str, num_iters: int) -> dict:
    ''' Get the board state after num_iters iterations.
        If exception_on_incomplete is True, raises an error if the board
        does not reach a final state within the requested iterations.
    '''    
    return await _run_board_iterations(board_id, num_iters)


@app.get("/boards/{board_id}/final/{max_iterations}", response_model=BoardState)
async def get_final_state(board_id: str, max_iterations: int) -> dict:
    ''' Get the final state for the given board ID.
        If the board does not reach a final state within MAX_ALLOWED_ITERATIONS,
        raises an error.
    '''
    # it's not clear from specs whether the limit is client-provided or server-defined
    # assume user defined but sanity check (in _run_board_iterations) to prevent impossible requests
    return await _run_board_iterations(board_id, max_iterations, exception_on_incomplete=True)


async def _run_board_iterations(board_id: str, num_iters: int, exception_on_incomplete: bool = False) -> dict:
    ''' Get the board state after num_iters iterations.
        If exception_on_incomplete is True, raises an error if the board
        does not reach a final state within the requested iterations.
    '''

    if num_iters < 0:
        raise HTTPException(status_code=400, detail="num_iters must be non-negative")

    if num_iters > MAX_ALLOWED_ITERATIONS:
        raise HTTPException(status_code=400, detail=f"num_iters exceeds limit of {MAX_ALLOWED_ITERATIONS}")

    # retrieve current board state
    board_dict = await _retrieve_board(board_id)
    if board_dict is None:
        raise HTTPException(status_code=400, detail="Board not found")

    board = Board(**board_dict, max_iterations=MAX_ALLOWED_ITERATIONS)
    if num_iters == 0:
        return board.to_dict()

    completed_all_iterations = board.run_iterations(num_iters)

    # special handling for final state requests
    if (exception_on_incomplete
        and not board.is_finished 
        and completed_all_iterations):
        raise HTTPException(status_code=400, detail="Board did not reach final state within requested iterations")

    # it isn't clear if this should overwrite the stored board state or not,
    # but we'll assume we must or we'd need a different way to handle board ids/get_next_state.

    # if we needed to, we could generate a predictable key (e.g. f"{board_id}:{num_iters}")
    # which would also allow caching for repeat requests, but this wouldn't likely be useful
    # unless hashing were used instead of uuids for board ids, and would probably mean a lot of 
    # wasted storage.

    v.set(board_id, board.to_string())
    return board.to_dict()


async def _retrieve_board(board_id: str) -> Board:
    ''' Retrieve and deserialize a board from storage by its ID.
        Raises HTTPException if the board is not found.
    '''
    board_json = v.get(board_id)
    if board_json is None:
        raise HTTPException(status_code=400, detail="Board not found")
    
    board_dict = json.loads(board_json)
    return board_dict
