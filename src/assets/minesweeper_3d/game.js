/**
 * 3D Minesweeper Engine using Three.js (Super Lightweight Array Mode)
 */

window.initMinesweeper3D = function(config) {
    console.log("M3D: Initializing with Lightweight Array Mode...");
    const container = document.getElementById('m3d-container');
    if (!container) return;

    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(config.w, config.h, config.d * 1.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    scene.add(directionalLight);

    const cubes = [];
    const geometry = new THREE.BoxGeometry(0.85, 0.85, 0.85);

    // フラット配列からの復元ロジック
    // config.c = [status, neighbor_mines, status, neighbor_mines, ...]
    const cellArray = config.c || [];
    let idx = 0;
    for (let z = 0; z < config.d; z++) {
        for (let y = 0; y < config.h; y++) {
            for (let x = 0; x < config.w; x++) {
                const status = cellArray[idx];
                const neighbors = cellArray[idx + 1];
                idx += 2;

                // 状態: 0=未開封, 1=開封済, 2=フラグ, 3=地雷(開封)
                // 開封済みかつ空(0)の場合は描画をスキップ
                if (status === 1 && neighbors === 0) continue;

                let material;
                if (status === 0 || status === 2) {
                    // 未開封 or フラグ
                    material = new THREE.MeshPhongMaterial({
                        color: status === 2 ? 0xffff00 : 0xcccccc,
                        transparent: true,
                        opacity: 0.7
                    });
                } else if (status === 3) {
                    // 地雷
                    material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
                } else {
                    // 数字あり
                    material = new THREE.MeshPhongMaterial({
                        color: 0x444444,
                        transparent: true,
                        opacity: 0.2
                    });
                }

                const cube = new THREE.Mesh(geometry, material);
                cube.position.set(
                    x - (config.w - 1) / 2,
                    y - (config.h - 1) / 2,
                    z - (config.d - 1) / 2
                );
                
                cube.userData = { x, y, z };
                scene.add(cube);
                cubes.push(cube);

                // 数字の表示
                if (status === 1 && neighbors > 0) {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = 128;
                    canvas.height = 128;
                    ctx.fillStyle = 'white';
                    ctx.font = 'Bold 80px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(neighbors, 64, 64);
                    
                    const texture = new THREE.CanvasTexture(canvas);
                    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
                    const sprite = new THREE.Sprite(spriteMaterial);
                    sprite.position.copy(cube.position);
                    sprite.scale.set(0.8, 0.8, 0.8);
                    scene.add(sprite);
                }
            }
        }
    }

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onMouseClick = (event) => {
        event.preventDefault();
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(cubes);

        if (intersects.length > 0) {
            const target = intersects[0].object.userData;
            const action = (event.button === 2 || event.ctrlKey) ? 'flag' : 'open';
            
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
    renderer.domElement.addEventListener('contextmenu', (e) => e.preventDefault());

    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    });
};
