# Montezuma’s Revenge Agent Documentation

## Overview

This document outlines the **Montezuma Master** demo built for the
Omni Link platform.  Inspired by the classic *Montezuma’s Revenge*,
the demo presents a simplified grid‑based maze where the player must
collect a key and reach a locked door while avoiding traps.  The
Omni Link agent controls the player character, making decisions based
on real‑time game state delivered over WebSockets.

Key responsibilities of the Montezuma Master agent include:

* Welcoming the user and explaining the objective of the maze.
* Describing the simplified rules (movement, key, door, spikes).
* Directing the user to open **montezuma.html** and start the relay
  server (and optionally the API proxy) to observe the game state.
* Navigating the maze by moving up, down, left or right, or starting
  the built‑in AI for automated path planning.

## Game Implementation and WebSocket Integration

The maze is implemented in `montezuma.html`.  A fixed map describes
walls (`#`), floor (` `), a key (`K`), a door (`D`), spikes (`S`) and a
starting position (`P`).  The game renders the grid and updates the
display at each frame.  Features include:

* **Grid‑based movement** – The player moves one cell at a time in the
  four cardinal directions.  Walls block movement; spikes reset the
  level; collecting the key allows entry through the door.
* **State reset** – When the player opens the door with the key or
  dies on spikes, the map resets to its initial state and a counter
  increments if the door was reached.
* **Agent control functions** – `tryMove(dx, dy)` is called internally
  when receiving action messages.  `startAgentAI()` triggers an
  internal BFS path planner that automatically finds a route to the
  key and then to the door.
* **WebSocket state** – After each frame, the game sends a JSON
  message containing the player’s coordinates, a Boolean indicating
  whether the key has been collected, the number of rooms cleared, and
  the current grid layout as an array of strings to
  `ws://localhost:6789/game_montezuma`.  It listens for action
  messages with a `move` property or an `ai` message to start the
  internal AI.

### Relay Server

The relay server (`montezuma_ws_server.py`) forwards messages between
the game (`/game_montezuma`) and the agent (`/agent_montezuma`).  It
maintains two sockets and passes JSON payloads through unchanged.  Run
the server before opening the game or connecting the agent.

### HTTP API Proxy (For TS Tool Agents)

If using a TypeScript agent running within the browser/OmniLink tool section,
an HTTP Proxy server (`montezuma_api_server.py`) must also be run alongside
the WS Relay Server. It bridges the WebSocket (`ws://localhost:6789`) to 
HTTP endpoints (`http://localhost:5000/data` and `/callback`) so TS scripts
can rapidly poll state and send actions via `fetch()`.

### Reference Agents

1. **Python Agent:** The sample Python agent (`montezuma_agent.py`) demonstrates a
   closed‑loop control algorithm over WebSockets directly.
2. **TypeScript Agent:** The TS script (`montezuma_tool_agent.ts`) connects to
   the `montezuma_api_server.py` HTTP proxy to demonstrate agent operation
   running inside a standard web browser context.

Both reconstruct the grid from the game state, perform a breadth‑first search 
to locate the key and then the door, and send movement commands to the game.  
When the planned path is exhausted, it recomputes a new path based on whether the key
has been collected.

## Knowledge File

The file **`montezuma_knowledge.md`** describes the history of
Montezuma’s Revenge, the simplified rules used in the demo, strategy
tips and an overview of the AI implementation.  Upload it to
Omni Link’s **Knowledge** section to give the agent the necessary
context.

## Agent Configuration

To configure the Montezuma Master agent in Omni Link, apply these
settings in the **Configuration** panel:

* **Main Task** – Define the agent as an explorer of a dangerous
  pyramid, capable of explaining the rules and guiding the user
  through the maze.  Instruct it to remind the user to start the
  relay server and open the HTML file to watch the game.
* **Available Commands** – For example:
  * `greet`: Welcomes the user and introduces the maze challenge.
  * `describe_montezuma_rules`: Describes movement, keys, doors and
    spikes.
  * `start_montezuma_game`: Instructs the user to run
    `montezuma_ws_server.py` and open `montezuma.html`, explaining
    what will be displayed.
  * `start_montezuma_ai`: Provides a JavaScript snippet that calls
    `startAgentAI()` or instructs the user to run the reference agent
    script.  The command should highlight that the AI plans paths via
    BFS.
* **Agent Name** – For instance **“Montezuma Master”**.
* **Agent Personality** – Adventurous, patient and analytical.  The
  agent encourages exploration and careful planning.
* **Custom Instructions** – Remind the agent to mention rooms cleared,
  whether the key has been collected and how many resets have
  occurred.  Encourage concise, supportive language.
* **Code Responses & Tool Usage** – Enable both.

After saving these settings and uploading the knowledge file, the
Montezuma Master agent can describe the game, guide the user and
control the player.

## Testing & Results

Testing was conducted in Omni Link’s text mode with the following
observations:

1. **Introduction** – The agent greeted the user, explained the goal
   (collect the key and reach the door), and offered to start a game.
2. **Rule explanation** – On request, the agent succinctly described
   movement, obstacles and the need to collect the key before
   opening the door.
3. **Game start** – When asked to start a game, the agent
   instructed running `montezuma_ws_server.py` and opening
   `montezuma.html`, noting that the maze would appear and the
   character would remain still until commands were sent or the AI
   was started.
4. **AI demonstration** – With the relay server running and the
   reference agent connected, the player automatically navigated to
   the key and then to the door using BFS.  The level reset after
   reaching the door, and the rooms‑cleared counter incremented.
   The Omni Link agent reported progress and emphasised careful
   planning and obstacle avoidance.【228638949760798†screenshot】

## Conclusion & Future Work

The Montezuma Master demo reveals how Omni Link agents can tackle
complex navigation tasks by combining search algorithms with real‑time
feedback.  Although simplified compared to the original game, the maze
still requires planning and hazard avoidance.  Future versions could
introduce moving enemies, multi‑room puzzles or additional items to
collect.  In its current form, the demo successfully demonstrates
knowledgeable guidance, automatic path planning and a closed‑loop
interaction between the agent and the game.