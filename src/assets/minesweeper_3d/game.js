/**
 * 3D Minesweeper Engine using Three.js
 */

window.initMinesweeper3D = function(config) {
    const container = document.getElementById('m3d-container');
    if (!container) return;

    // 前回のレンダラーがあれば削除
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(config.width, config.height, config.depth * 2);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // 照明
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    scene.add(directionalLight);

    const cubes = [];
    const geometry = new THREE.BoxGeometry(0.9, 0.9, 0.9);

    // グリッド生成
    Object.values(config.cells).forEach(cell => {
        // 開封済みかつ地雷なし(0)の場合は表示しない（透過性向上のため）
        if (cell.opened && !cell.is_mine && cell.neighbor_mines === 0) {
            return;
        }

        let material;
        if (!cell.opened) {
            // 未開封
            material = new THREE.MeshPhongMaterial({
                color: cell.flagged ? 0xffff00 : 0xcccccc,
                transparent: true,
                opacity: 0.8
            });
        } else if (cell.is_mine) {
            // 地雷
            material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
        } else {
            // 数字あり
            material = new THREE.MeshPhongMaterial({
                color: 0x444444,
                transparent: true,
                opacity: 0.3
            });
        }

        const cube = new THREE.Mesh(geometry, material);
        // 中心を (0,0,0) に持ってくるためのオフセット
        cube.position.set(
            cell.x - (config.width - 1) / 2,
            cell.y - (config.height - 1) / 2,
            cell.z - (config.depth - 1) / 2
        );
        
        cube.userData = { x: cell.x, y: cell.y, z: cell.z };
        scene.add(cube);
        cubes.push(cube);

        // 数字の表示 (Spriteを使用)
        if (cell.opened && !cell.is_mine && cell.neighbor_mines > 0) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 64;
            canvas.height = 64;
            ctx.fillStyle = 'white';
            ctx.font = 'Bold 48px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(cell.neighbor_mines, 32, 48);
            
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.position.copy(cube.position);
            sprite.scale.set(0.8, 0.8, 0.8);
            scene.add(sprite);
        }
    });

    // クリック判定 (Raycaster)
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onMouseClick = (event) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(cubes);

        if (intersects.length > 0) {
            const target = intersects[0].object.userData;
            // Python側に通知するためのカスタムイベント
            const action = event.button === 2 || event.ctrlKey ? 'flag' : 'open';
            
            // Streamlit 連携用に hidden input や query params を使う代わりに、
            // Streamlit コンポーネントの返り値として機能させるための仕組みが必要。
            // ここでは簡易的に、window オブジェクト経由で値を渡す。
            if (window.Streamlit) {
                window.Streamlit.setComponentValue({
                    action: action,
                    x: target.x,
                    y: target.y,
                    z: target.z,
                    trigger: Date.now()
                });
            }
        }
    };

    renderer.domElement.addEventListener('mousedown', onMouseClick);
    // 右クリックメニューを禁止
    renderer.domElement.addEventListener('contextmenu', (e) => e.preventDefault());

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // リサイズ対応
    window.addEventListener('resize', () => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    });
};
