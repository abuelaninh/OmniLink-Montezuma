const grid = [
    '############',
    '#P    #   K#',
    '# ## ### # #',
    '#    #     #',
    '#### # #####',
    '#      #  D#',
    '# ## ##### #',
    '############'
];
for (let y = 0; y < grid.length; y++) {
    console.log(grid[y].split('').map(c => c === ' ' ? '.' : c).join(''));
}
