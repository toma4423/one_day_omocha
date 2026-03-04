function setupKurohige(config) {
    const container = document.getElementById('kurohige-app');
    if (!container) return;

    const { status } = config;

    // 表示をシンプルに演出に特化させる
    container.innerHTML = `
        <div class="kurohige-container">
            <div class="barrel-wrapper">
                <div class="kurohige-man ${status === 'boom' ? 'boom' : ''}">🏴‍☠️</div>
                <div class="barrel">
                    <div class="barrel-band band-top"></div>
                    <div class="barrel-band band-middle"></div>
                    <div class="barrel-band band-bottom"></div>
                </div>
            </div>
        </div>
    `;
}
