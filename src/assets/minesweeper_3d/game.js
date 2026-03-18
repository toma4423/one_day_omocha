/**
 * 3D Minesweeper Engine using Three.js (Optimized for List Data)
 */

window.initMinesweeper3D = function(config) {
    console.log("Initializing 3D Minesweeper (List Mode)...");
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
    camera.position.set(config.width, config.height, config.depth * 1.5);

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

    // リスト形式のデータを処理
    const cellList = config.cell_list || [];
    cellList.forEach(cell => {
        if (cell.opened && !cell.is_mine && cell.neighbor_mines === 0) {
            return;
        }

        let material;
        if (!cell.opened) {
            material = new THREE.MeshPhongMaterial({
                color: cell.flagged ? 0xffff00 : 0xcccccc,
                transparent: true,
                opacity: 0.7
            });
        } else if (cell.is_mine) {
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
            cell.x - (config.width - 1) / 2,
            cell.y - (config.height - 1) / 2,
            cell.z - (config.depth - 1) / 2
        );
        
        cube.userData = { x: cell.x, y: cell.y, z: cell.z };
        scene.add(cube);
        cubes.push(cube);

        if (cell.opened && !cell.is_mine && cell.neighbor_mines > 0) {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 128;
            canvas.height = 128;
            ctx.fillStyle = 'white';
            ctx.font = 'Bold 80px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(cell.neighbor_mines, 64, 64);
            
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
            const sprite = new THREE.Sprite(spriteMaterial);
            sprite.position.copy(cube.position);
            sprite.scale.set(0.8, 0.8, 0.8);
            scene.add(sprite);
        }
    });

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
