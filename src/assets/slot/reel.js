let reels = [];
let isSpinning = false;
let startSound, winSound;

function setupSlot(config) {
    const container = document.getElementById('slot-container');
    container.innerHTML = '';
    reels = [];

    // 音源の準備
    startSound = new Audio("https://actions.google.com/sounds/v1/science_fiction/beep_button.ogg");
    winSound = new Audio("https://actions.google.com/sounds/v1/celebration/horns_hooray.ogg");

    for (let i = 0; i < 3; i++) {
        const window = document.createElement('div');
        window.className = 'reel-window';
        
        const strip = document.createElement('div');
        strip.className = 'reel-strip';
        strip.id = `reel-${i}`;
        
        // 初期図柄（config.initialReels）
        const initialSymbol = config.initialReels[i];
        renderSymbol(strip, initialSymbol);
        
        window.appendChild(strip);
        container.appendChild(window);
        reels.push(strip);
    }

    // スピン実行の検知
    if (config.spinTrigger > 0 && !isSpinning) {
        startSpin(config);
    }
}

function renderSymbol(parent, symbol) {
    const div = document.createElement('div');
    div.className = 'symbol';
    if (symbol.image_url) {
        div.innerHTML = `<img src="${symbol.image_url}">`;
    } else {
        div.textContent = symbol.char;
    }
    parent.appendChild(div);
}

function startSpin(config) {
    isSpinning = true;
    if (config.soundEnabled) startSound.play();

    reels.forEach((strip, i) => {
        // 回転演出用のダミー図柄を大量に追加
        strip.innerHTML = '';
        
        // 現在の図柄
        renderSymbol(strip, config.initialReels[i]);
        
        // ダミー（20個くらい）
        for (let d = 0; d < 20; d++) {
            const randSym = config.symbols[Math.floor(Math.random() * config.symbols.length)];
            renderSymbol(strip, randSym);
        }
        
        // 最終的な当たり図柄
        renderSymbol(strip, config.targetReels[i]);

        // アニメーション開始
        const symbolHeight = 120;
        const totalHeight = (20 + 1) * symbolHeight;
        
        strip.classList.remove('stopping');
        strip.style.transition = 'none';
        strip.style.transform = 'translateY(0)';
        
        // 次のフレームでアニメーション実行
        requestAnimationFrame(() => {
            // 停止タイミングをずらす (0.5s, 1.0s, 1.5s)
            strip.classList.add('stopping');
            strip.style.transition = `transform ${1.5 + i * 0.5}s cubic-bezier(0.1, 0.7, 0.1, 1.0)`;
            strip.style.transform = `translateY(-${totalHeight}px)`;
        });
    });

    // 全リール停止後の処理 (一番遅いリールに合わせる)
    setTimeout(() => {
        isSpinning = false;
        if (config.isWin && config.soundEnabled) {
            winSound.play();
        }
    }, 1500 + 2 * 500);
}

function renderSymbol(parent, symbol) {
    const div = document.createElement('div');
    div.className = 'symbol';
    if (symbol.image_url) {
        div.innerHTML = `<img src="${symbol.image_url}">`;
    } else {
        div.textContent = symbol.char;
    }
    parent.appendChild(div);
}
