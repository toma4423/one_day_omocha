/**
 * 🎡 ルーレット描画・アニメーション・音響ロジック
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

    let currentRotation = 0; // 0 rad
    let isSpinning = false;
    let audioCtx = null;

    function playClickSound() {
        if (!soundEnabled) return;
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();
            
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(900, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.04);
            gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.04);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.04);
        } catch (e) { console.error(e); }
    }

    function drawWheel(rotation) {
        ctx.clearRect(0, 0, width, height);
        
        // 外枠
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius + 5, 0, 2 * Math.PI);
        ctx.fillStyle = "#333";
        ctx.fill();

        let startAngle = rotation;
        items.forEach((item, i) => {
            const sliceAngle = (item.weight / totalWeight) * 2 * Math.PI;
            ctx.beginPath();
            ctx.fillStyle = item.color;
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.fill();
            ctx.strokeStyle = "white";
            ctx.lineWidth = 1;
            ctx.stroke();

            // ラベル
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(startAngle + sliceAngle / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "white";
            ctx.font = "bold 16px sans-serif";
            ctx.shadowBlur = 4;
            ctx.shadowColor = "rgba(0,0,0,0.5)";
            const label = item.label.length > 10 ? item.label.substring(0, 8) + '..' : item.label;
            ctx.fillText(label, radius - 15, 6);
            ctx.restore();

            startAngle += sliceAngle;
        });

        // 固定針
        ctx.fillStyle = "#FF4B4B";
        ctx.beginPath();
        ctx.moveTo(width - 5, centerY);
        ctx.lineTo(width - 25, centerY - 15);
        ctx.lineTo(width - 25, centerY + 15);
        ctx.closePath();
        ctx.fill();

        // センター
        ctx.beginPath();
        ctx.arc(centerX, centerY, 15, 0, 2 * Math.PI);
        ctx.fillStyle = "white";
        ctx.fill();
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 2;
        ctx.stroke();
    }

    function startAnimation() {
        if (winnerIndex === null || winnerIndex === undefined) {
            drawWheel(0);
            return;
        }

        // 抽選結果に合わせるロジック
        // 針は右端 (0 rad)
        // 累積ウェイトから、winnerIndex が占める角度範囲を計算
        let weightSumBefore = 0;
        for (let i = 0; i < winnerIndex; i++) weightSumBefore += items[i].weight;
        const winnerSliceAngle = (items[winnerIndex].weight / totalWeight) * 2 * Math.PI;
        const winnerStartAngle = (weightSumBefore / totalWeight) * 2 * Math.PI;
        
        // 停止時に針の方向に来るべき角度 (逆転させる)
        const targetStopAngle = (2 * Math.PI - (winnerStartAngle + winnerSliceAngle / 2)) % (2 * Math.PI);
        
        // 最低回転数 (3-5回)
        const totalRotation = 10 * Math.PI + targetStopAngle;
        
        let start = null;
        const duration = 4000; // 4秒
        let lastClickIndex = -1;

        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = (timestamp - start) / duration;

            if (progress < 1) {
                // イージング関数 (Quartic Out: 最初速く、最後ゆっくり)
                const easing = 1 - Math.pow(1 - progress, 4);
                const currentRotation = totalRotation * easing;
                
                // カチカチ音の判定
                const needlePos = (2 * Math.PI - (currentRotation % (2 * Math.PI))) % (2 * Math.PI);
                let currentWeightSum = 0;
                let currentSliceIndex = 0;
                for(let i=0; i<items.length; i++) {
                    currentWeightSum += (items[i].weight / totalWeight) * 2 * Math.PI;
                    if (needlePos < currentWeightSum) {
                        currentSliceIndex = i;
                        break;
                    }
                }
                if (currentSliceIndex !== lastClickIndex) {
                    playClickSound();
                    lastClickIndex = currentSliceIndex;
                }

                drawWheel(currentRotation);
                requestAnimationFrame(animate);
            } else {
                drawWheel(totalRotation);
                document.getElementById('status').innerText = "当選： " + items[winnerIndex].label;
            }
        }
        requestAnimationFrame(animate);
    }

    // 初回描画
    if (spinTrigger) {
        startAnimation();
    } else {
        drawWheel(0);
    }
}
