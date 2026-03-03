"""
Montezuma’s Revenge agent WebSocket client

This script connects to the Montezuma WebSocket relay server at
ws://localhost:6789/agent_montezuma.  It receives state messages from the
game, reconstructs the grid and plans a path to collect the key and reach
the door using breadth‑first search.  It then sends action messages to
move the player along this path.

Usage:

    python montezuma_agent.py

Ensure that the Montezuma relay server (`montezuma_ws_server.py`) is running
and that the game is connected to `/game_montezuma`.
"""

import asyncio
import json
from collections import deque
import websockets


def bfs(grid, start, target_cond, key_collected):
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    queue = deque()
    queue.append((start[0], start[1], []))
    visited[start[1]][start[0]] = True
    while queue:
        x, y, path = queue.popleft()
        if target_cond(x, y):
            return path
        for move, dx, dy in [("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0)]:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                continue
            if visited[ny][nx]:
                continue
            cell = grid[ny][nx]
            if cell == '#':
                continue
            if cell == 'S':
                continue
            if cell == 'D' and not key_collected:
                continue
            visited[ny][nx] = True
            queue.append((nx, ny, path + [move]))
    return []


async def run_montezuma_agent(host: str = "localhost", port: int = 6789) -> None:
    uri = f"ws://{host}:{port}/agent_montezuma"
    async with websockets.connect(uri) as ws:
        print(f"Connected to Montezuma server at {uri}")
        planned_path = []
        try:
            async for message in ws:
                data = json.loads(message)
                if data.get("type") != "state":
                    continue
                grid_strings = data["grid"]
                grid = [list(row) for row in grid_strings]
                player = (data["player"]["x"], data["player"]["y"])
                key_collected = data["keyCollected"]
                # if no planned path or finished, compute new path
                if not planned_path:
                    if not key_collected:
                        # find path to key
                        planned_path = bfs(grid, player, lambda x, y: grid[y][x] == 'K', key_collected)
                    else:
                        planned_path = bfs(grid, player, lambda x, y: grid[y][x] == 'D', key_collected)
                move = None
                if planned_path:
                    move = planned_path.pop(0)
                if move:
                    action = {"type": "action", "move": move}
                    await ws.send(json.dumps(action))
        except websockets.ConnectionClosed:
            print("Disconnected from Montezuma server")


if __name__ == "__main__":
    asyncio.run(run_montezuma_agent())