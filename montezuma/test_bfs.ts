interface Position { x: number; y: number; }

function bfs(grid: string[], start: Position, targetChar: string, keyCollected: boolean): ("UP" | "DOWN" | "LEFT" | "RIGHT")[] {
    const rows = grid.length;
    const cols = grid[0].length;
    const visited: boolean[][] = Array.from({ length: rows }, () => Array(cols).fill(false));
    const queue: { x: number, y: number, path: ("UP" | "DOWN" | "LEFT" | "RIGHT")[] }[] = [];
    
    queue.push({ x: start.x, y: start.y, path: [] });
    visited[start.y][start.x] = true;
    
    const dirs = [
        { dx: 0, dy: -1, move: "UP" as const },
        { dx: 0, dy: 1, move: "DOWN" as const },
        { dx: -1, dy: 0, move: "LEFT" as const },
        { dx: 1, dy: 0, move: "RIGHT" as const }
    ];

    while (queue.length > 0) {
        const current = queue.shift()!;
        if (grid[current.y][current.x] === targetChar) {
            return current.path;
        }
        for (const dir of dirs) {
            const nx = current.x + dir.dx;
            const ny = current.y + dir.dy;
            if (nx < 0 || nx >= cols || ny < 0 || ny >= rows) continue;
            if (visited[ny][nx]) continue;
            const cell = grid[ny][nx];
            if (cell === '#' || cell === 'S') continue;
            if (cell === 'D' && !keyCollected) continue;
            visited[ny][nx] = true;
            queue.push({ x: nx, y: ny, path: [...current.path, dir.move] });
        }
    }
    return [];
}

const grid = [
    '############',
    '#     #    #',
    '# ## ### # #',
    '#    #     #',
    '#### # #####',
    '#      #  D#',
    '# ## ##### #',
    '############'
];
// Player is at where K was: x=10, y=1
console.log(bfs(grid, {x: 10, y: 1}, 'D', true));
