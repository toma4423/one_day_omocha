let reels = [];
let isSpinning = false;
let startSound = null;
let winSound = null;

// 音源の初期化（一度だけ行う）
function initSounds() {
    if (!startSound) {
        startSound = new Audio("https://actions.google.com/sounds/v1/science_fiction/beep_button.ogg");
    }
    if (!winSound) {
        winSound = new Audio("https://actions.google.com/sounds/v1/celebration/horns_hooray.ogg");
    }
}

function setupSlot(config) {
    const container = document.getElementById('slot-container');
    container.innerHTML = '';
    reels = [];
    
    // 結果表示用のレイヤーを追加
    const overlay = document.createElement('div');
    overlay.id = 'slot-overlay';
    overlay.className = 'slot-overlay';
    container.appendChild(overlay);

    for (let i = 0; i < 3; i++) {
        const window = document.createElement('div');
        window.className = 'reel-window';
        
        const strip = document.createElement('div');
        strip.className = 'reel-strip';
        strip.id = `reel-${i}`;
        
        renderSymbol(strip, config.initialReels[i]);
        
        window.appendChild(strip);
        container.appendChild(window);
        reels.push(strip);
    }

    // スピン実行
    if (config.spinTrigger > 0 && !isSpinning) {
        initSounds();
        startSpin(config);
    }
}

function renderSymbol(parent, symbol) {
    const div = document.createElement('div');
    div.className = 'symbol';
    if (symbol.image_url) {
        div.innerHTML = `<img src="${symbol.image_url}" onerror="this.src=''; this.innerText='${symbol.char}';">`;
    } else {
        div.textContent = symbol.char;
    }
    parent.appendChild(div);
}

function startSpin(config) {
    isSpinning = true;
    const overlay = document.getElementById('slot-overlay');
    overlay.classList.remove('show');
    overlay.innerHTML = '';

    // 始動音の再生
    if (config.soundEnabled && startSound) {
        startSound.currentTime = 0;
        startSound.play().catch(e => console.log("Sound play blocked:", e));
    }

    const symbolHeight = 120;
    const dummyCount = 30; // 回転量

    reels.forEach((strip, i) => {
        strip.innerHTML = '';
        renderSymbol(strip, config.initialReels[i]);
        
        for (let d = 0; d < dummyCount; d++) {
            const randSym = config.symbols[Math.floor(Math.random() * config.symbols.length)];
            renderSymbol(strip, randSym);
        }
        
        renderSymbol(strip, config.targetReels[i]);

        strip.classList.remove('stopping');
        strip.style.transition = 'none';
        strip.style.transform = 'translateY(0)';
        
        const totalHeight = (dummyCount + 1) * symbolHeight;
        
        setTimeout(() => {
            strip.classList.add('stopping');
            // 停止時間をずらす（パチスロ風）
            const duration = 1.5 + (i * 0.6); 
            strip.style.transition = `transform ${duration}s cubic-bezier(0.1, 0.4, 0.1, 1.1)`;
            strip.style.transform = `translateY(-${totalHeight}px)`;
        }, 50);
    });

    // 全リール停止後（一番遅いリールが止まるタイミング）
    const totalDuration = (1.5 + (2 * 0.6)) * 1000;
    setTimeout(() => {
        isSpinning = false;
        if (config.isWin) {
            showWinEffect(config);
        }
    }, totalDuration + 100);
}

function showWinEffect(config) {
    const overlay = document.getElementById('slot-overlay');
    overlay.innerHTML = `<div class="win-announcement">🎊 ${config.winName} 🎊</div>`;
    overlay.classList.add('show');
    
    if (config.soundEnabled && winSound) {
        winSound.currentTime = 0;
        winSound.play().catch(e => console.log("Win sound play blocked:", e));
    }
    
    // 簡易的な紙吹雪エフェクトをJSで追加
    triggerConfetti();
}

function triggerConfetti() {
    // 簡易的なパーティクル生成
    const container = document.getElementById('slot-container');
    for (let i = 0; i < 50; i++) {
        const p = document.createElement('div');
        p.className = 'confetti';
        p.style.left = Math.random() * 100 + '%';
        p.style.backgroundColor = `hsl(${Math.random() * 360}, 70%, 50%)`;
        p.style.animationDelay = Math.random() * 2 + 's';
        container.appendChild(p);
        setTimeout(() => p.remove(), 4000);
    }
}
