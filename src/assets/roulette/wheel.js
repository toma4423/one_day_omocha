/**
 * 🎡 高機能ルーレット描画・物理演算・音響・演出
 */

function setupWheel(config) {
    let { items, soundEnabled, spinTrigger, winnerIndex } = config;
    
    // 有効な項目のみに絞り込む
    items = items.filter(item => item.enabled !== false);
    
    const canvas = document.getElementById('wheel');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = width / 2 - 25;
    const totalWeight = items.reduce((sum, item) => sum + item.weight, 0);

    let isSpinning = false;
    let audioCtx = null;
    let needleWiggle = 0;

    function playClickSound() {
        if (!soundEnabled) return;
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(1000, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.04);
            gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.04);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.04);
            needleWiggle = 0.4;
        } catch (e) { console.error(e); }
    }

    function drawWheel(rotation) {
        ctx.clearRect(0, 0, width, height);
        
        // 外枠の装飾
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius + 10, 0, 2 * Math.PI);
        ctx.fillStyle = "#D4AF37";
        ctx.fill();
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 2;
        ctx.stroke();

        if (items.length === 0) {
            ctx.fillStyle = "#999";
            ctx.textAlign = "center";
            ctx.font = "20px sans-serif";
            ctx.fillText("項目がありません", centerX, centerY);
            return;
        }

        let startAngle = rotation;
        items.forEach((item, i) => {
            const sliceAngle = (item.weight / totalWeight) * 2 * Math.PI;
            
            // スライスの描画
            ctx.beginPath();
            ctx.fillStyle = item.color;
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.fill();
            ctx.strokeStyle = "rgba(255,255,255,0.3)";
            ctx.lineWidth = 1;
            ctx.stroke();

            // テキストの描画
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(startAngle + sliceAngle / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "white";
            
            // 文字数とスライスの大きさに応じてフォントサイズを調整
            const label = item.label;
            let fontSize = 18;
            if (label.length > 10) fontSize = 14;
            if (label.length > 15) fontSize = 12;
            
            // スライスが極端に狭い場合の調整
            const sliceWidthAtText = (sliceAngle * radius * 0.7);
            if (fontSize > sliceWidthAtText) fontSize = Math.max(8, sliceWidthAtText);

            ctx.font = `bold ${fontSize}px sans-serif`;
            ctx.shadowColor = "rgba(0,0,0,0.5)";
            ctx.shadowBlur = 2;
            
            // 長すぎる場合は省略
            let displayLabel = label;
            if (label.length > 20) displayLabel = label.slice(0, 18) + '...';
            
            ctx.fillText(displayLabel, radius - 20, fontSize / 3);
            ctx.restore();
            
            startAngle += sliceAngle;
        });

        // センターサークル
        ctx.beginPath();
        ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
        ctx.fillStyle = "#fff";
        ctx.fill();
        ctx.strokeStyle = "#D4AF37";
        ctx.lineWidth = 4;
        ctx.stroke();

        drawPointer();
    }

    function drawPointer() {
        ctx.save();
        ctx.translate(width - 5, centerY);
        ctx.rotate(needleWiggle);
        ctx.beginPath();
        ctx.moveTo(-30, 0);
        ctx.lineTo(5, -15);
        ctx.lineTo(5, 15);
        ctx.closePath();
        ctx.fillStyle = "#FF4B4B";
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
        needleWiggle *= 0.8;
    }

    function startAnimation() {
        if (winnerIndex === null || winnerIndex === undefined || items.length === 0) {
            drawWheel(0);
            return;
        }
        isSpinning = true;
        
        // 当選項目までの角度計算
        let weightSumBefore = 0;
        for (let i = 0; i < winnerIndex; i++) {
            // winnerIndexは元のリストのインデックスなので、有効な項目のみのインデックスに変換が必要な場合がある
            // ここではitemsはすでにフィルタ済みなので、winnerIndexの整合性を呼び出し側で保証するか、ここで探す
        }
        
        // フィルタ後のリストでのインデックスを確認
        // 呼び出し側のwinner_idxは全項目に対するものなので、フィルタ後のインデックスに変換
        const winnerItem = config.items[winnerIndex];
        const filteredWinnerIdx = items.findIndex(it => it.id === winnerItem.id);
        
        if (filteredWinnerIdx === -1) {
            drawWheel(0);
            return;
        }

        for (let i = 0; i < filteredWinnerIdx; i++) weightSumBefore += items[i].weight;
        const winnerSliceAngle = (items[filteredWinnerIdx].weight / totalWeight) * 2 * Math.PI;
        const winnerStartAngle = (weightSumBefore / totalWeight) * 2 * Math.PI;
        
        // 針(右端 0度/2PI)の位置に当選項目の中心が来るように調整
        const targetStopAngle = (2 * Math.PI - (winnerStartAngle + winnerSliceAngle / 2)) % (2 * Math.PI);
        const totalRotation = 10 * Math.PI + targetStopAngle; // 5回転 + 停止位置
        const startTime = performance.now();
        const duration = 5000;
        let lastItemIdx = -1;

        function animate(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // イージング関数 (Quintic Out)
            const easing = 1 - Math.pow(1 - progress, 5);
            const currentRotation = totalRotation * easing;
            
            // 現在どの項目が針の位置にあるか判定（音用）
            const currentAngleMod = (2 * Math.PI - (currentRotation % (2 * Math.PI))) % (2 * Math.PI);
            let tempSum = 0;
            let currentItemIdx = 0;
            for (let i = 0; i < items.length; i++) {
                tempSum += (items[i].weight / totalWeight) * 2 * Math.PI;
                if (currentAngleMod < tempSum) { currentItemIdx = i; break; }
            }
            if (currentItemIdx !== lastItemIdx) {
                if (progress < 0.95) playClickSound();
                lastItemIdx = currentItemIdx;
            }
            
            drawWheel(currentRotation);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                isSpinning = false;
                const statusEl = document.getElementById('status');
                statusEl.innerHTML = `<span style="font-size: 32px; animation: bounce 0.5s infinite alternate;">🎊 ${items[filteredWinnerIdx].label} 🎊</span>`;
            }
        }
        requestAnimationFrame(animate);
    }

    // 重複回転防止ロジック
    const storageKey = 'lastRouletteTrigger';
    const lastTrigger = sessionStorage.getItem(storageKey);
    
    if (spinTrigger > 0 && spinTrigger.toString() !== lastTrigger) {
        sessionStorage.setItem(storageKey, spinTrigger.toString());
        startAnimation();
    } else {
        // 回転させない場合、当選位置で静止させるか初期位置にする
        if (winnerIndex !== null && winnerIndex !== undefined) {
            const winnerItem = config.items[winnerIndex];
            const filteredWinnerIdx = items.findIndex(it => it.id === winnerItem.id);
            if (filteredWinnerIdx !== -1) {
                let weightSumBefore = 0;
                for (let i = 0; i < filteredWinnerIdx; i++) weightSumBefore += items[i].weight;
                const winnerSliceAngle = (items[filteredWinnerIdx].weight / totalWeight) * 2 * Math.PI;
                const winnerStartAngle = (weightSumBefore / totalWeight) * 2 * Math.PI;
                const stopAngle = (2 * Math.PI - (winnerStartAngle + winnerSliceAngle / 2)) % (2 * Math.PI);
                drawWheel(stopAngle);
                
                // 結果テキストも表示しておく
                const statusEl = document.getElementById('status');
                if (statusEl) {
                    statusEl.innerHTML = `<span style="font-size: 32px;">${items[filteredWinnerIdx].label}</span>`;
                }
                return;
            }
        }
        drawWheel(0);
    }
}
