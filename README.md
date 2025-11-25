# Conway's Game of Life API


A simple API implementing the Game of Life.

## Usage:
Clone repo  
Run "docker compose up" in game_of_life_api directory

## API

#### POST /boards/ - create new board with specified configuration  
Expected data:  
`{"coordinates": list[tuple[int, int]]}` - include only active squares  
Returns:  
`{"board_id": str}` to be used in subsequent requests  

#### GET /boards/{board_id}/next - get the next iteration of the given board  
Returns:  
`{"coordinates": list[tuple[int, int]]}` - list of only active squares after one iteration  

#### GET /boards/{board_id}/iterate/{num_iters} - get the state of the board after {num_iters} iterations  
Returns:  
`{"coordinates": list[tuple[int, int]]}` - list of only active squares after {num_iters} iterations  

#### GET /board/{board_id}/final/{limit} - get either the final state of the board or an error if final state not achieved within {limit} iterations  
Returns:  
`{"coordinates": list[tuple[int, int]]}` - list of only active squares in the board's final state, if achieved  
OR, if not achieved:  
`400` error "Board did not reach final state within requested iterations"  


## TODOS:
  - make sure major board functions (run_iterations, _iterate especially) and valkey operations are async to avoid blocking
  - potential issue where multiple simultaneous requests for the same board id could lead to confusing results
      - use locking to block simultaneous requests?
      - stricter input requirements (require starting stage, etc.)?
  - use post instead of get, since (almost) all requests affect the stored data
