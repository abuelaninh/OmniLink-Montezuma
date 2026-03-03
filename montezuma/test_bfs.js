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

function bfs(grid, start, targetChar, keyCollected) {
    const rows = grid.length;
    const cols = grid[0].length;
    const visited = Array.from({ length: rows }, () => Array(cols).fill(false));
    const queue = [];

    queue.push({ x: start.x, y: start.y, path: [] });
    visited[start.y][start.x] = true;

    const dirs = [
        { dx: 0, dy: -1, move: "UP" },
        { dx: 0, dy: 1, move: "DOWN" },
        { dx: -1, dy: 0, move: "LEFT" },
        { dx: 1, dy: 0, move: "RIGHT" }
    ];

    while (queue.length > 0) {
        const current = queue.shift();

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

console.log(bfs(grid, { x: 10, y: 1 }, 'D', true));
