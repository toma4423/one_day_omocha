/**
 * 3D Minesweeper Engine using Three.js (Highlight Mode)
 */

window.initMinesweeper3D = function(config) {
    console.log("M3D: Initializing with Highlight Mode...");
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

    // 選択中の座標を取得
    const sel = config.sel; // [x, y, z] or null

    const cellArray = config.c || [];
    for (let i = 0; i < cellArray.length; i += 5) {
        const x = cellArray[i];
        const y = cellArray[i + 1];
        const z = cellArray[i + 2];
        const status = cellArray[i + 3];
        const neighbors = cellArray[i + 4];

        // 状態: 0=未開封, 1=開封済, 2=フラグ, 3=地雷(開封)
        // 開封済みかつ空(0)の場合は描画をスキップ（選択中以外）
        const isSelected = sel && x === sel[0] && y === sel[1] && z === sel[2];
        if (status === 1 && neighbors === 0 && !isSelected) continue;

        let material;
        if (isSelected) {
            // 選択中のセルを赤く強調
            material = new THREE.MeshPhongMaterial({
                color: 0xff0000,
                emissive: 0x330000,
                transparent: true,
                opacity: 0.9
            });
        } else if (status === 0 || status === 2) {
            material = new THREE.MeshPhongMaterial({
                color: status === 2 ? 0xffff00 : 0xcccccc,
                transparent: true,
                opacity: 0.6
            });
        } else if (status === 3) {
            material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
        } else {
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
            ctx.fillStyle = isSelected ? 'yellow' : 'white';
            ctx.font = 'Bold 80px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(neighbors, 64, 64);
            
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.position.copy(cube.position);
            sprite.scale.set(0.7, 0.7, 0.7);
            scene.add(sprite);
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
