window.setupSentenceSlot = function(config) {
    const container = document.getElementById('sentence-slot-app');
    if (!container) return;

    // 前回のタイマーをクリア
    if (window._sentenceSlotTimers) {
        window._sentenceSlotTimers.forEach(clearTimeout);
    }
    window._sentenceSlotTimers = [];

    config.reels.forEach((reel, index) => {
        const wrapper = document.getElementById(`reel-wrapper-${index}`);
        if (!wrapper) return;

        const content = wrapper.querySelector('.reel-content');
        if (!content) return;

        const itemHeight = 120;
        const totalItems = reel.items.length;
        const targetIdx = reel.items.indexOf(reel.target);

        // スピン演出
        if (reel.isSpinning) {
            wrapper.classList.add('spinning');
            
            // 3周以上回してからターゲットに止める
            const extraSpins = 3;
            const finalY = -( (extraSpins * totalItems + targetIdx) * itemHeight );

            content.style.transition = 'none';
            content.style.transform = 'translateY(0)';
            
            const timer1 = setTimeout(() => {
                content.style.transition = `transform ${2.0 + index * 0.5}s cubic-bezier(0.15, 0, 0.15, 1)`;
                content.style.transform = `translateY(${finalY}px)`;
            }, 50);
            window._sentenceSlotTimers.push(timer1);

            const timer2 = setTimeout(() => {
                wrapper.classList.remove('spinning');
                // ループ演出用に位置を補正（0〜totalItemsの範囲内に戻す）
                const wrappedY = -(targetIdx * itemHeight);
                content.style.transition = 'none';
                content.style.transform = `translateY(${wrappedY}px)`;
            }, 3000 + index * 500);
            window._sentenceSlotTimers.push(timer2);
        } else {
            // 静止状態（即座にターゲット位置へ）
            const finalY = -(targetIdx * itemHeight);
            content.style.transition = 'none';
            content.style.transform = `translateY(${finalY}px)`;
            wrapper.classList.remove('spinning');
        }
    });
};
