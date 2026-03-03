/**
 * Agent Tool for Montezuma's Revenge Demo
 * 
 * Target: Browser (EcmaScript Module) / OmniLink Tool Section
 * 
 * Responsibilities:
 * 1. Poll http://localhost:5000/data for Game State.
 * 2. Parse the Grid & calculate the shortest path (BFS) to Key, then Door.
 * 3. Decide Move (Up/Down/Left/Right).
 * 4. Post Move to http://localhost:5000/callback.
 */

// Interfaces matching the Proxy's JSON structure
interface PythonState {
    command: "IDLE" | "ACTIVATE";
    payload: string; // JSON string of the GameState
    version: number;
}

interface Position {
    x: number;
    y: number;
}

interface GameState {
    type: "state";
    player: Position;
    keyCollected: boolean;
    roomsCleared: number;
    grid: string[]; // Array of strings e.g. ["####", "#P #", ...]
}

interface AgentAction {
    action: "UP" | "DOWN" | "LEFT" | "RIGHT" | "STOP";
    version: number;
    timestamp: string;
}

const API_URL = "http://localhost:5000";
const DEBUG_FLAGS = {
    logState: false,       // Log raw state occasionally
    logPathfinding: true,  // Log when a new path is calculated
    logMoves: false        // Log every single move sent
};

// Global Agent State Memory
let currentPath: ("UP" | "DOWN" | "LEFT" | "RIGHT")[] = [];
let lastKeyCollectedState = false;
let lastRoomClearedState = 0;

/**
 * Breadth-First Search matching the logic of the Python agent.
 */
function bfs(grid: string[], start: Position, targetChar: string, keyCollected: boolean): ("UP" | "DOWN" | "LEFT" | "RIGHT")[] {
    const rows = grid.length;
    const cols = grid[0].length;

    // Create visited boolean grid
    const visited: boolean[][] = Array.from({ length: rows }, () => Array(cols).fill(false));

    // queue elements: { x, y, path }
    const queue: { x: number, y: number, path: ("UP" | "DOWN" | "LEFT" | "RIGHT")[] }[] = [];

    queue.push({ x: start.x, y: start.y, path: [] });
    visited[start.y][start.x] = true;

    const dirs: { dx: number, dy: number, move: "UP" | "DOWN" | "LEFT" | "RIGHT" }[] = [
        { dx: 0, dy: -1, move: "UP" },
        { dx: 0, dy: 1, move: "DOWN" },
        { dx: -1, dy: 0, move: "LEFT" },
        { dx: 1, dy: 0, move: "RIGHT" }
    ];

    while (queue.length > 0) {
        const current = queue.shift()!;

        // Check if we hit the target char
        if (grid[current.y][current.x] === targetChar) {
            return current.path;
        }

        for (const dir of dirs) {
            const nx = current.x + dir.dx;
            const ny = current.y + dir.dy;

            // Bounds check
            if (nx < 0 || nx >= cols || ny < 0 || ny >= rows) continue;

            // Visited check
            if (visited[ny][nx]) continue;

            const cell = grid[ny][nx];

            // Wall / Spike check
            if (cell === '#' || cell === 'S') continue;

            // Door without key check
            if (cell === 'D' && !keyCollected) continue;

            // Valid move
            visited[ny][nx] = true;
            queue.push({
                x: nx,
                y: ny,
                path: [...current.path, dir.move]
            });
        }
    }

    return []; // No path found
}


async function agentLoop() {
    try {
        // --- STEP 1: GET Game State ---
        const response = await fetch(`${API_URL}/data`);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

        const wrapper: PythonState = await response.json();

        if (wrapper.command === "ACTIVATE") {
            // Parse the inner payload (Game State)
            const gameState: GameState = JSON.parse(wrapper.payload);

            if (DEBUG_FLAGS.logState && Math.random() < 0.05) {
                console.log("[AGENT] Current State:", gameState);
            }

            // Detect environment resets/changes
            if (gameState.roomsCleared > lastRoomClearedState) {
                console.log(`[AGENT] Room Cleared! Total: ${gameState.roomsCleared}`);
                lastRoomClearedState = gameState.roomsCleared;
                currentPath = []; // reset path
                lastKeyCollectedState = false;
            }

            if (gameState.keyCollected && !lastKeyCollectedState) {
                console.log("[AGENT] Key Collected! Repathing to Door...");
                lastKeyCollectedState = true;
                currentPath = []; // reset path
            }

            // --- STEP 2: Logic (The Brain) ---
            if (currentPath.length === 0) {
                const targetChar = gameState.keyCollected ? 'D' : 'K';
                currentPath = bfs(gameState.grid, gameState.player, targetChar, gameState.keyCollected);

                if (DEBUG_FLAGS.logPathfinding && currentPath.length > 0) {
                    console.log(`[AGENT] New Path Calculated to '${targetChar}': ${currentPath.length} steps`);
                }
            }

            let move: "UP" | "DOWN" | "LEFT" | "RIGHT" | "STOP" = "STOP";

            if (currentPath.length > 0) {
                // Peek the next move (but don't pop it until we know it succeeded... or just assume we send one per tick)
                // Actually since polling is 5ms, and game loop runs at requestAnimationFrame (16ms), 
                // we might send the same move multiple times if we aren't careful, but since game WS 
                // processes 1 move per tick, we should pop it to avoid getting stuck.
                // However, `player` position in gameState tells us exactly where we are!
                // Best approach for TS BFS agent: Pop 1 step, send it. If we haven't moved next poll, we might jitter.
                // We'll pop it, because the Python agent pops it.
                move = currentPath.shift()!;
            }

            if (move !== "STOP") {
                if (DEBUG_FLAGS.logMoves) {
                    console.log(`[AGENT] Moving ${move}`);
                }

                // --- STEP 3: Act (POST Command) ---
                const actionPayload: AgentAction = {
                    action: move,
                    version: wrapper.version,
                    timestamp: new Date().toISOString()
                };

                await fetch(`${API_URL}/callback`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(actionPayload),
                });
            }
        }
    } catch (error) {
        console.error("[AGENT] Connection Error:", error);
    }
}

// Start the Polling Loop
console.log(`🚀 Montezuma TS Agent Started. Polling ${API_URL} as fast as possible...`);

// Loop continuously so the environment doesn't exit the script context early
async function startAgent() {
    console.log(`🚀 Montezuma TS Agent Started. Polling ${API_URL} as fast as possible...`);
    while (true) {
        await agentLoop();
        await new Promise(resolve => setTimeout(resolve, 50));
    }
}

startAgent();

export { };
