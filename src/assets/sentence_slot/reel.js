window.setupSentenceSlot = function(config) {
    if (!config || !config.reels) return;
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

        const itemHeight = 120; // CSSの.reel-itemのheightと一致させる
        const totalItems = reel.items.length;
        if (totalItems === 0) return;

        let targetIdx = reel.items.indexOf(reel.target);
        if (targetIdx === -1) targetIdx = 0; // 見つからない場合は先頭

        // スピン演出
        if (reel.isSpinning) {
            wrapper.classList.add('spinning');
            
            // 3周以上回してからターゲットに止める
            const extraSpins = 3;
            const finalY = -( (extraSpins * totalItems + targetIdx) * itemHeight );

            content.style.transition = 'none';
            content.style.transform = 'translateY(0)';
            
            const timer1 = setTimeout(() => {
                // DOMが再描画された直後の可能性があるため、少し待ってから遷移を開始
                content.style.transition = `transform ${2.0 + index * 0.5}s cubic-bezier(0.15, 0, 0.15, 1)`;
                content.style.transform = `translateY(${finalY}px)`;
            }, 50);
            window._sentenceSlotTimers.push(timer1);

            const timer2 = setTimeout(() => {
                if (wrapper) wrapper.classList.remove('spinning');
                // ループ演出用に位置を補正（0〜totalItemsの範囲内に戻す）
                const wrappedY = -(targetIdx * itemHeight);
                if (content) {
                    content.style.transition = 'none';
                    content.style.transform = `translateY(${wrappedY}px)`;
                }
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
