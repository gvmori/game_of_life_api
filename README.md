# Conway's Game of Life API


A simple API implementing the Game of Life.

TODOS:
  - make sure major board functions (run_iterations, _iterate especially) and valkey operations are async to avoid blocking
  - potential issue where multiple simultaneous requests for the same board id could lead to confusing results
      - use locking to block simultaneous requests?
      - stricter input requirements (require starting stage, etc.)?
