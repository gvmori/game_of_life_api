#!/usr/local/bin/python3

import requests

# run api with fastapi dev ./main.py
# ensure valkey is running locally

def main():
    for coord_list in [
        # Glider
        [(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)],
        # Negative-range glider
        [(-1, -2), (-2, -3), (-3, -1), (-3, -2), (-3, -3)],
        # Block
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        # Blinker
        [(0, 0), (1, 0), (2, 0)],
        # Toad
        [(1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)],
        # Beacon
        [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2), (2, 3), (3, 2), (3, 3)],
        # Bad pattern (should die out)
        [(0, 0), (0, 1), (1, 0)],
        # Empty board
        [],
        # Large sparse pattern
        [(0, 0), (100, 100), (200, 200), (300, 300), (400, 400)],
        # Dense pattern
        [(i, j) for i in range(10) for j in range(10)],

    ]:
        print(f"Testing board with initial coordinates: {coord_list}")
        run_test(coord_list)
        print("-" * 40)
     
    

def run_test(coords):
    post_data = {
        "coordinates": coords,
    }

    url = "http://127.0.0.1:8000/boards/"

    response = requests.post(url, json=post_data)

    board_id = response.json().get("board_id")
    print(f"Created board with ID: {board_id}")

    next_url = f"{url}{board_id}/next"
    for x in range(10):
        next_response = requests.get(next_url)
        if not next_response.ok:
            print(f"Error retrieving next state: {next_response.text}")
            return
        next_state = next_response.json().get("coordinates")
        print(f"Next state coordinates: {next_state}")

    states_url = f"{url}{board_id}/iterate/200"
    states_response = requests.get(states_url)
    if not states_response.ok:
        print(f"Error retrieving state after 200 iterations: {states_response.text}")
        return
    print(f"State after 200 iterations coordinates: {states_response.json().get('coordinates')}")

    final_url = f"{url}{board_id}/final/1000"
    final_response = requests.get(final_url)
    if not final_response.ok:
        if "Board did not reach final state within requested iterations" in final_response.text:
            print("Board did not reach final state within 500 iterations.")
            return
        else:
            print(f"Error retrieving final state: {final_response.text}")
            return
    final_state = final_response.json().get("coordinates")
    print(f"Final state coordinates: {final_state}")

if __name__ == "__main__":
    main()
