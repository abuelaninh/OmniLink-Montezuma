import asyncio
import json
import websockets
from flask import Flask, jsonify, request
from threading import Thread
import time
from flask_cors import CORS

app = Flask(__name__)
# Allow CORS so a browser TS script can access it easily if needed
CORS(app)

# Global state to hold the latest game data received from the WebSocket
latest_game_state = None
# Global variable to hold the action to be sent back to the game
pending_action = None

WS_URL = "ws://localhost:6789/agent_montezuma"


@app.route('/data', methods=['GET'])
def get_data():
    """
    Returns the latest game state from the WebSocket.
    Matches the PythonState wrapper format from the Pong example.
    """
    global latest_game_state
    
    # If we haven't received any state yet
    if latest_game_state is None:
        return jsonify({
            "command": "IDLE",
            "payload": "{}",
            "version": int(time.time() * 1000)
        })

    # Wrap the actual game state in the requested format
    wrapper = {
        "command": "ACTIVATE",
        "payload": json.dumps(latest_game_state),
        "version": int(time.time() * 1000)
    }
    return jsonify(wrapper)


@app.route('/callback', methods=['POST'])
def post_callback():
    """
    Receives the action (UP, DOWN, LEFT, RIGHT, STOP) from the TS agent 
    and sets it globally so the WebSocket thread can pick it up and send it.
    """
    global pending_action
    data = request.json
    
    if not data or "action" not in data:
        return jsonify({"status": "error", "message": "No action provided"}), 400
        
    action_str = data["action"].lower()
    
    if action_str in ["up", "down", "left", "right"]:
        pending_action = action_str
        
    return jsonify({"status": "action_received", "action": action_str})


async def websocket_loop():
    """
    Background asyncio loop that connects to the Montezuma Relay Server via WS.
    It constantly reads state and writes pending actions.
    """
    global latest_game_state
    global pending_action
    
    while True:
        try:
            print(f"[API Server] Connecting to WS {WS_URL}...")
            async with websockets.connect(WS_URL) as ws:
                print(f"[API Server] Connected to {WS_URL}")
                
                while True:
                    # 1. Check for pending actions to send
                    if pending_action:
                        action_msg = json.dumps({"type": "action", "move": pending_action})
                        await ws.send(action_msg)
                        print(f"[API Server] Sent action: {pending_action}")
                        pending_action = None
                        
                    # 2. Receive state (non-blocking with timeout to allow action sending)
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=0.01)
                        if message:
                            data = json.loads(message)
                            if data.get("type") == "state":
                                latest_game_state = data
                    except asyncio.TimeoutError:
                        pass # Normal timeout, just loop again
                        
        except Exception as e:
            print(f"[API Server] WS Connection Error: {e}, retrying in 2s...")
            await asyncio.sleep(2)


def start_websocket_thread():
    """Runs the asyncio event loop in a separate daemon thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_loop())

if __name__ == '__main__':
    print("Starting WS Thread...")
    ws_thread = Thread(target=start_websocket_thread, daemon=True)
    ws_thread.start()
    
    print("Starting Flask API Server on http://localhost:5000...")
    # Run Flask without the reloader so it doesn't duplicate the background thread
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
