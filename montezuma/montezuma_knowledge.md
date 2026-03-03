## Montezuma’s Revenge Knowledge

### Game Overview

*Montezuma’s Revenge* is a challenging platform‑adventure game from the
1980s known for its multi‑room maze, deadly traps and puzzle‑like
exploration.  Players control a character exploring an underground
pyramid filled with treasure, keys, doors and hazards.  This demo
captures the essence of Montezuma’s Revenge in a simplified grid‑based
format.

### Simplified Rules

1. **Movement** – The player moves one cell at a time using the four
   cardinal directions (up, down, left and right).  In the original
   game, jumping and climbing ladders is required, but this demo
   simplifies movement to a grid.
2. **Walls and floors** – Walls (`#`) block movement; floors (` `) can be
   traversed.  Spikes (`S`) act as traps: stepping on spikes resets
   the room.
   *New mechanics:* Gates (`G`) act as purple walls blocking movement until a Switch (`W`) is stepped on. Stepping on the Switch permanently removes all gates in the room.
3. **Key and door** – A key (`K`) must be collected before the door
   (`D`) can be opened.  Touching the door without a key will have no
   effect.  Once the key is collected, touching the door clears the
   level and increments the room counter.
4. **Reset and progress** – Clearing a room resets the level layout and
   places the player back at the starting position.  The number of
   rooms cleared tracks progress.

### Strategy and Tactics

Montezuma’s Revenge is renowned for its requirement of careful
planning and exploration.  Key strategies include:

* **Plan your path** – Study the layout and identify the key’s
  location and obstacles.  Plan a route that collects the key and
  reaches the door while avoiding traps.
* **Avoid hazards** – Be mindful of spikes and other deadly tiles.  In
  more complex versions, enemies and moving platforms also pose
  threats.
* **Explore methodically** – In the original game, players must
  remember the connections between rooms.  Taking notes helps avoid
  backtracking and dead ends.

### Demo AI Overview

The demo includes a built‑in AI that uses breadth‑first search (BFS) to
plan a shortest path to the key and then to the door.  The AI computes
a path whenever it reaches the start of a new room or after collecting
the key.  It then follows this path step by step.  A reference agent
(`montezuma_agent.py`) implements the same algorithm over WebSockets,
demonstrating how an Omni Link agent can navigate the maze autonomously.

### WebSocket Integration

To allow your Omni Link agent to observe and control the game:

* The game connects to `ws://localhost:6789/game_montezuma` and sends
  state messages containing the player’s coordinates, whether the key
  is collected, the number of rooms cleared and the current grid
  layout as an array of strings.
* The relay server (`montezuma_ws_server.py`) forwards messages between
  the game and an agent connected to `/agent_montezuma`.
* The reference agent (`montezuma_agent.py`) reconstructs the grid
  from the state, computes BFS paths and sends `action` messages
  (`up`, `down`, `left` or `right`) to move the player.
* Alternatively, for an in-browser OmniLink TS Tool agent, the proxy
  server (`montezuma_api_server.py`) can be used to bridge WebSockets
  to an HTTP API (`/data` and `/callback`), which `montezuma_tool_agent.ts` polls.

By uploading this knowledge file to Omni Link and configuring
appropriate commands, the agent can answer questions about
Montezuma’s Revenge, describe the simplified rules and strategies used
in the demo, and control the player via WebSockets.