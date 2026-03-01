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
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius + 10, 0, 2 * Math.PI);
        ctx.fillStyle = "#D4AF37";
        ctx.fill();
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 2;
        ctx.stroke();

        let startAngle = rotation;
        items.forEach((item, i) => {
            const sliceAngle = (item.weight / totalWeight) * 2 * Math.PI;
            ctx.beginPath();
            ctx.fillStyle = item.color;
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.fill();
            ctx.strokeStyle = "rgba(255,255,255,0.3)";
            ctx.lineWidth = 1;
            ctx.stroke();

            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(startAngle + sliceAngle / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "white";
            ctx.font = "bold 18px sans-serif";
            const displayLabel = item.label.length > 10 ? item.label.slice(0, 8) + '..' : item.label;
            ctx.fillText(displayLabel, radius - 20, 7);
            ctx.restore();
            startAngle += sliceAngle;
        });

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
        if (winnerIndex === null || winnerIndex === undefined) {
            drawWheel(0);
            return;
        }
        isSpinning = true;
        let weightSumBefore = 0;
        for (let i = 0; i < winnerIndex; i++) weightSumBefore += items[i].weight;
        const winnerSliceAngle = (items[winnerIndex].weight / totalWeight) * 2 * Math.PI;
        const winnerStartAngle = (weightSumBefore / totalWeight) * 2 * Math.PI;
        const targetStopAngle = (2 * Math.PI - (winnerStartAngle + winnerSliceAngle / 2)) % (2 * Math.PI);
        const totalRotation = 12 * Math.PI + targetStopAngle;
        const startTime = performance.now();
        const duration = 4500;
        let lastItemIdx = -1;

        function animate(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easing = 1 - Math.pow(1 - progress, 5);
            const currentRotation = totalRotation * easing;
            const currentAngleMod = (2 * Math.PI - (currentRotation % (2 * Math.PI))) % (2 * Math.PI);
            let tempSum = 0;
            let currentItemIdx = 0;
            for (let i = 0; i < items.length; i++) {
                tempSum += (items[i].weight / totalWeight) * 2 * Math.PI;
                if (currentAngleMod < tempSum) { currentItemIdx = i; break; }
            }
            if (currentItemIdx !== lastItemIdx) { playClickSound(); lastItemIdx = currentItemIdx; }
            drawWheel(currentRotation);
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                isSpinning = false;
                const statusEl = document.getElementById('status');
                statusEl.innerHTML = `<span style="font-size: 40px; animation: bounce 0.5s infinite alternate;">🎊 ${items[winnerIndex].label} 🎊</span>`;
            }
        }
        requestAnimationFrame(animate);
    }

    if (spinTrigger > 0) startAnimation();
    else drawWheel(0);
}
