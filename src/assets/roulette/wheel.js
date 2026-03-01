/**
 * 🎡 高機能ルーレット描画・物理演算・音響・演出
 */

function setupWheel(config) {
    const { items, soundEnabled, spinTrigger, winnerIndex } = config;
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
    let needleWiggle = 0; // 針の揺れ

    // 音源の初期化
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
            needleWiggle = 0.4; // 音と同時に針を動かす
        } catch (e) { console.error(e); }
    }

    function drawWheel(rotation) {
        ctx.clearRect(0, 0, width, height);

        // 外側の装飾（ゴールド）
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius + 10, 0, 2 * Math.PI);
        ctx.fillStyle = "#D4AF37"; // Gold
        ctx.fill();
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 2;
        ctx.stroke();

        let startAngle = rotation;
        items.forEach((item, i) => {
            const sliceAngle = (item.weight / totalWeight) * 2 * Math.PI;
            
            // スライス描画
            ctx.beginPath();
            ctx.fillStyle = item.color;
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.fill();
            ctx.strokeStyle = "rgba(255,255,255,0.3)";
            ctx.lineWidth = 1;
            ctx.stroke();

            // テキスト
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(startAngle + sliceAngle / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "white";
            ctx.font = "bold 18px 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
            ctx.shadowBlur = 4;
            ctx.shadowColor = "rgba(0,0,0,0.5)";
            const displayLabel = item.label.length > 10 ? item.label.slice(0, 8) + '..' : item.label;
            ctx.fillText(displayLabel, radius - 20, 7);
            ctx.restore();

            startAngle += sliceAngle;
        });

        // センター
        ctx.beginPath();
        ctx.arc(centerX, centerY, 20, 0, 2 * Math.PI);
        ctx.fillStyle = "#fff";
        ctx.fill();
        ctx.strokeStyle = "#D4AF37";
        ctx.lineWidth = 4;
        ctx.stroke();

        // ポインター（針）の描画
        drawPointer();
    }

    function drawPointer() {
        ctx.save();
        ctx.translate(width - 5, centerY);
        ctx.rotate(needleWiggle); // 音に合わせて揺れる
        
        ctx.beginPath();
        ctx.moveTo(-30, 0); // 頂点を左（盤面方向）に向ける
        ctx.lineTo(5, -15);
        ctx.lineTo(5, 15);
        ctx.closePath();
        
        ctx.fillStyle = "#FF4B4B";
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
        
        // 針の揺れを戻す（減衰）
        needleWiggle *= 0.8;
    }

    function startAnimation() {
        if (winnerIndex === null || winnerIndex === undefined) {
            drawWheel(0);
            return;
        }

        isSpinning = true;
        
        // 針は右端 (0 rad)
        let weightSumBefore = 0;
        for (let i = 0; i < winnerIndex; i++) weightSumBefore += items[i].weight;
        const winnerSliceAngle = (items[winnerIndex].weight / totalWeight) * 2 * Math.PI;
        const winnerStartAngle = (weightSumBefore / totalWeight) * 2 * Math.PI;
        
        // 当選項目の中央が「0 rad (右端)」に来るように、回転の終着点を計算
        // 盤面を時計回りに回すと rotation が増える。針が 0 なら slice を 0 に向かわせる。
        const targetStopAngle = (2 * Math.PI - (winnerStartAngle + winnerSliceAngle / 2)) % (2 * Math.PI);
        
        // 5回転 + 調整分
        const minLaps = 6;
        const totalRotation = minLaps * 2 * Math.PI + targetStopAngle;
        
        const startTime = performance.now();
        const duration = 4500; // 4.5秒
        let lastItemIdx = -1;

        function animate(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // イージング（後半にかけて急激に減速）
            const easing = 1 - Math.pow(1 - progress, 5);
            const currentRotation = totalRotation * easing;
            
            // 現在の針の位置にあるアイテムを特定して音を鳴らす
            const currentAngleMod = (2 * Math.PI - (currentRotation % (2 * Math.PI))) % (2 * Math.PI);
            let tempSum = 0;
            let currentItemIdx = 0;
            for (let i = 0; i < items.length; i++) {
                tempSum += (items[i].weight / totalWeight) * 2 * Math.PI;
                if (currentAngleMod < tempSum) {
                    currentItemIdx = i;
                    break;
                }
            }

            if (currentItemIdx !== lastItemIdx) {
                playClickSound();
                lastItemIdx = currentItemIdx;
            }

            drawWheel(currentRotation);

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                isSpinning = false;
                document.getElementById('status').innerText = "結果： " + items[winnerIndex].label;
            }
        }
        requestAnimationFrame(animate);
    }

    // 即座に実行
    if (spinTrigger > 0) {
        startAnimation();
    } else {
        drawWheel(0);
    }
}
