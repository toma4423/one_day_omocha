window.setupSentenceSlot = function(config) {
    const container = document.getElementById('sentence-slot-app');
    if (!container) return;

    // 前回のタイマーをクリア（メモリリーク防止）
    if (window._sentenceSlotTimers) {
        window._sentenceSlotTimers.forEach(clearTimeout);
    }
    window._sentenceSlotTimers = [];

    config.reels.forEach((reel, index) => {
        const wrapper = document.getElementById(`reel-wrapper-${index}`);
        if (!wrapper) return;

        const content = wrapper.querySelector('.reel-content');
        if (!content) return;

        // アイテムの高さを取得 (CSSで120pxに固定)
        const itemHeight = 120;

        // スピン演出
        if (reel.isSpinning) {
            wrapper.classList.add('spinning');
            
            // 演出用にダミーアイテムをたくさん並べる（実際には移動距離を稼ぐだけ）
            // 最終位置 = -(targetIndex * itemHeight)
            // 10周分くらい回す演出
            const totalItems = reel.items.length;
            const targetIdx = reel.items.indexOf(reel.target);
            const extraSpins = 3; // 何周させるか
            const finalY = -( (extraSpins * totalItems + targetIdx) * itemHeight );

            content.style.transition = 'none';
            content.style.transform = 'translateY(0)';
            
            // 次のフレームでアニメーション開始
            const timer1 = setTimeout(() => {
                content.style.transition = `transform ${1.5 + index * 0.3}s cubic-bezier(0.45, 0.05, 0.55, 0.95)`;
                content.style.transform = `translateY(${finalY}px)`;
            }, 50);
            window._sentenceSlotTimers.push(timer1);

            // アニメーション終了後にブラーを除去
            const timer2 = setTimeout(() => {
                wrapper.classList.remove('spinning');
            }, 2000);
            window._sentenceSlotTimers.push(timer2);
        } else {
            // 静止状態
            const targetIdx = reel.items.indexOf(reel.target);
            const finalY = -(targetIdx * itemHeight);
            content.style.transition = 'transform 0.5s ease-out';
            content.style.transform = `translateY(${finalY}px)`;
        }
    });
};
