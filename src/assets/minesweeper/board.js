function setupMinesweeper(config) {
    const container = document.getElementById('ms-app');
    if (!container) return;

    const { width, height, board, revealed, flags, status } = config;

    const boardEl = document.createElement('div');
    boardEl.className = 'ms-board';
    boardEl.style.gridTemplateColumns = `repeat(${width}, 1fr)`;

    for (let r = 0; r < height; r++) {
        for (let c = 0; c < width; c++) {
            const tile = document.createElement('div');
            tile.className = 'ms-tile';
            
            if (revealed[r][c]) {
                tile.classList.add('revealed');
                const val = board[r][c];
                if (val === -1) {
                    tile.textContent = '💣';
                    tile.classList.add('mine');
                } else if (val > 0) {
                    tile.textContent = val;
                    tile.classList.add(`num-${val}`);
                }
            } else if (flags[r][c]) {
                tile.textContent = '🚩';
                tile.classList.add('flagged');
            }

            // クリックイベント
            tile.onclick = (e) => {
                if (status !== 'playing') return;
                handleTileAction(r, c, 'reveal');
            };

            // 右クリック（フラグ）
            tile.oncontextmenu = (e) => {
                e.preventDefault();
                if (status !== 'playing') return;
                handleTileAction(r, c, 'flag');
            };

            boardEl.appendChild(tile);
        }
    }

    container.innerHTML = '';
    container.appendChild(boardEl);
}

function handleTileAction(r, c, action) {
    const event = new CustomEvent('ms_action', { 
        detail: { r, c, action } 
    });
    window.dispatchEvent(event);
}
