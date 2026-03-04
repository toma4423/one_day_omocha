function setupKurohige(config) {
    const container = document.getElementById('kurohige-app');
    if (!container) return;

    const { numSlots, clickedSlots, status, targetSlot } = config;

    let html = `
        <div class="kurohige-container">
            <div class="barrel-wrapper">
                <div class="kurohige-man ${status === 'boom' ? 'boom' : ''}">🏴‍☠️</div>
                <div class="barrel">
                    <div class="barrel-band band-top"></div>
                    <div class="barrel-band band-middle"></div>
                    <div class="barrel-band band-bottom"></div>
                </div>
            </div>
            <div class="slots-grid">
    `;

    for (let i = 0; i < numSlots; i++) {
        const isClicked = clickedSlots.includes(i);
        const isBoom = status === 'boom' && i === targetSlot;
        const className = `slot-btn ${isClicked ? 'clicked' : ''} ${isBoom ? 'boom' : ''}`;
        const content = isClicked ? '🗡️' : (isBoom ? '💥' : (i + 1));
        
        html += `
            <button 
                class="${className}" 
                onclick="handleSlotClick(${i})" 
                ${(isClicked || status !== 'playing') ? 'disabled' : ''}
            >
                ${content}
            </button>
        `;
    }

    html += `
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function handleSlotClick(idx) {
    // Streamlit 側にクリックイベントを通知する
    // (実際には st.components.v1.html 内での実行になるため、
    // window.parent.postMessage などを使用するか、
    // 単純に streamlit の値を書き換える hidden button を経由する)
    
    // シンプルにするため、ここでは sessionStorage に値をセットして
    // Streamlit 側でそれを監視する仕組みを想定するか、
    // あるいは st.components.v1.html の戻り値を利用する。
    // 今回は Streamlit の標準的な st.button を透過的に使う方法を検討するが、
    // JS 側で完結させて最後に状態を戻す方式がスムーズ。
    
    // イベントを発火
    const event = new CustomEvent('slot_clicked', { detail: { index: idx } });
    window.dispatchEvent(event);
}
