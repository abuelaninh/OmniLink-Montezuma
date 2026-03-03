"""
WebSocket relay server for the Montezuma’s Revenge demo.

This server listens on localhost:6789 and allows two types of clients to connect:

* The **game** client connects at path `/game_montezuma`.  It should send
  state updates containing the player position, whether the key has been
  collected, how many rooms have been cleared and the current grid layout.
  Messages from the game will be forwarded to the connected agent client
  (if present).

* The **agent** client connects at path `/agent_montezuma`.  It should
  send action messages instructing the game to move the player up,
  down, left or right, or to enable the built‑in AI.  Messages from the
  agent will be forwarded to the game client.

Message format is JSON and passed through untouched.

Run this server in a terminal before starting the game and agent scripts:

    python montezuma_ws_server.py

The server runs indefinitely until interrupted (Ctrl+C).
"""

import asyncio
import json
import re
from typing import Dict
import websockets
import paho.mqtt.client as mqtt


class MontezumaRelayServer:
    """Relay between Montezuma game and agent WebSocket clients."""

    def __init__(self, host: str = "localhost", port: int = 6789) -> None:
        self.host = host
        self.port = port
        self.clients: Dict[str, websockets.ServerConnection] = {}
        self.latest_game_state = None
        
        # Setup MQTT
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        
        # For thread-safe passing of commands from MQTT thread to asyncio loop
        self.mqtt_command_queue = asyncio.Queue()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            client.subscribe("olink/commands")
        else:
            print(f"Failed to connect to MQTT broker, code {rc}")

    def on_mqtt_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8').strip()
        print(f"MQTT Rx on {topic}: {payload}")
        
        # Parse payload robustly. It might be:
        # 1. pause
        # 2. "pause"
        # 3. {"command": "pause"}
        command = ""
        
        # Try JSON first
        try:
            data = json.loads(payload)
            if isinstance(data, dict) and "command" in data:
                command = data["command"]
            elif isinstance(data, str):
                command = data
        except json.JSONDecodeError:
            # Not JSON, strip quotes if any
            command = payload.strip("'\"")
            
        command = command.lower()
        if command in ["pause", "resume"]:
            # Drop it in the queue for the asyncio loop to pick up safely
            self.mqtt_command_queue.put_nowait(command)

    async def handler(self, websocket: websockets.ServerConnection) -> None:
        path = websocket.request.path
        role = None
        if path == "/game_montezuma":
            role = "game"
        elif path == "/agent_montezuma":
            role = "agent"
        else:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                role = data.get("role")
            except Exception:
                await websocket.close(code=4000, reason="Unknown client role")
                return
        self.clients[role] = websocket
        print(f"Montezuma {role} client connected from {websocket.remote_address}")
        try:
            async for message in websocket:
                if role == "game":
                    # Cache latest state for MQTT
                    try:
                        data = json.loads(message)
                        if data.get("type") == "state":
                            self.latest_game_state = data
                    except json.JSONDecodeError:
                        pass
                        
                    if "agent" in self.clients:
                        await self.clients["agent"].send(message)
                elif role == "agent" and "game" in self.clients:
                    await self.clients["game"].send(message)
        except websockets.ConnectionClosed:
            pass
        finally:
            if self.clients.get(role) is websocket:
                del self.clients[role]
            print(f"Montezuma {role} client disconnected from {websocket.remote_address}")

    async def _mqtt_publish_loop(self):
        """Repeatedly publish state to olink/context every 10 seconds."""
        while True:
            if self.latest_game_state:
                # We can extract and build a concise payload for standard olink context
                # "The game back-end to publish the state of the game (score and whatever info)"
                mqtt_payload = {
                    "game": "montezuma",
                    "score": self.latest_game_state.get("score", 0),
                    "roomsCleared": self.latest_game_state.get("roomsCleared", 0),
                    "isPaused": self.latest_game_state.get("isPaused", False),
                    "keyCollected": self.latest_game_state.get("keyCollected", False)
                }
                self.mqtt_client.publish("olink/context", json.dumps(mqtt_payload))
            await asyncio.sleep(10)

    async def _mqtt_command_processor_loop(self):
        """Processes commands coming from the MQTT thread into WebSocket messages."""
        while True:
            command = await self.mqtt_command_queue.get()
            if "game" in self.clients:
                try:
                    msg = json.dumps({"type": "control", "command": command})
                    await self.clients["game"].send(msg)
                    print(f"Relayed {command} control to game via WS")
                except Exception as e:
                    print(f"Error sending control to game: {e}")
            self.mqtt_command_queue.task_done()

    async def run(self) -> None:
        # Start the background MQTT thread
        try:
            self.mqtt_client.connect("localhost", 1883, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"MQTT Broker connect failed (is mosquitto running?): {e}")

        # Start the background tasks
        asyncio.create_task(self._mqtt_publish_loop())
        asyncio.create_task(self._mqtt_command_processor_loop())

        async with websockets.serve(self.handler, self.host, self.port):
            print(f"Montezuma relay server running on ws://{self.host}:{self.port}")
            await asyncio.Future()


if __name__ == "__main__":
    server = MontezumaRelayServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("Server stopped")