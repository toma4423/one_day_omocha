function setupKurohige(config) {
    const container = document.getElementById('kurohige-app');
    if (!container) return;

    const { status } = config;
    const isBoom = status === 'boom';

    // 演出に特化
    container.innerHTML = `
        <div class="kurohige-container ${isBoom ? 'boom' : ''}">
            <div class="barrel-wrapper">
                <div class="kurohige-man ${isBoom ? 'boom' : ''}">🏴‍☠️</div>
                <div class="barrel">
                    <div class="barrel-band band-top"></div>
                    <div class="barrel-band band-middle"></div>
                    <div class="barrel-band band-bottom"></div>
                </div>
                ${isBoom ? `
                <div class="explosion-container">
                    <div class="explosion-particle particle-1">💥</div>
                    <div class="explosion-particle particle-2">💥</div>
                    <div class="explosion-particle particle-3">💥</div>
                    <div class="explosion-particle particle-4">💥</div>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}
