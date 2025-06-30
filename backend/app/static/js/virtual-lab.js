// Virtual Lab 3D Experience
console.log('Virtual Lab script loaded');

class VirtualLab {
    constructor() {
        console.log('VirtualLab constructor called');
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.raycaster = null;
        this.mouse = null;
        this.hoveredObject = null;
        this.objects = [];
        this.isLoading = true;
        
        // Check if THREE.js is available
        if (typeof THREE === 'undefined') {
            console.error('THREE.js is not loaded!');
            this.showError('THREE.js library is not loaded. Please check your internet connection and try again.');
            return;
        }
        
        console.log('THREE.js is available, initializing...');
        this.init();
    }
    
    showError(message) {
        const container = document.getElementById('lab3d');
        if (container) {
            container.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100%; background: #1a1a2e; color: white;">
                    <div style="text-align: center; padding: 20px;">
                        <h3>⚠️ Error de carga</h3>
                        <p>${message}</p>
                        <button onclick="location.reload()" style="margin-top: 10px; padding: 10px 20px; background: #6c5ce7; color: white; border: none; border-radius: 5px; cursor: pointer;">
                            Recargar página
                        </button>
                    </div>
                </div>
            `;
        }
    }
    
    init() {
        console.log('Initializing Virtual Lab...');
        try {
            this.setupScene();
            this.setupCamera();
            this.setupRenderer();
            this.setupControls();
            this.setupLighting();
            this.setupRaycaster();
            this.createLabEnvironment();
            this.setupEventListeners();
            this.animate();
            
            // Hide loading screen after setup
            setTimeout(() => {
                this.hideLoadingScreen();
            }, 2000);
            
            console.log('Virtual Lab initialized successfully!');
        } catch (error) {
            console.error('Error initializing Virtual Lab:', error);
            this.showError('Error al inicializar la experiencia 3D: ' + error.message);
        }
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);
        this.scene.fog = new THREE.Fog(0xf0f0f0, 50, 200);
    }
    
    setupCamera() {
        const container = document.getElementById('lab3d');
        this.camera = new THREE.PerspectiveCamera(
            75,
            container.clientWidth / container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.set(15, 12, 15);
        this.camera.lookAt(0, 0, 0);
    }
    
    setupRenderer() {
        const container = document.getElementById('lab3d');
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setClearColor(0xf0f0f0);
        container.appendChild(this.renderer.domElement);
    }
    
    setupControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 5;
        this.controls.maxDistance = 50;
        this.controls.maxPolarAngle = Math.PI / 2;
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(20, 20, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -25;
        directionalLight.shadow.camera.right = 25;
        directionalLight.shadow.camera.top = 25;
        directionalLight.shadow.camera.bottom = -25;
        this.scene.add(directionalLight);
        
        // Additional spot lights for better illumination
        const spotLight1 = new THREE.SpotLight(0xffffff, 0.5);
        spotLight1.position.set(-15, 15, 15);
        spotLight1.angle = Math.PI / 6;
        spotLight1.penumbra = 0.1;
        this.scene.add(spotLight1);
        
        const spotLight2 = new THREE.SpotLight(0xffffff, 0.5);
        spotLight2.position.set(15, 15, -15);
        spotLight2.angle = Math.PI / 6;
        spotLight2.penumbra = 0.1;
        this.scene.add(spotLight2);
    }
    
    setupRaycaster() {
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
    }
    
    createLabEnvironment() {
        // Create floor
        this.createFloor();
        
        // Create walls
        this.createWalls();
        
        // Create 3D printers area (top orange zone)
        this.create3DPrinters();
        
        // Create collaborative work tables (green zone)
        this.createWorkTables();
        
        // Create storage areas
        this.createStorageAreas();
        
        // Create digital board
        this.createDigitalBoard();
        
        // Create specialized equipment
        this.createSpecializedEquipment();
    }
    
    createFloor() {
        const floorGeometry = new THREE.PlaneGeometry(30, 20);
        const floorMaterial = new THREE.MeshLambertMaterial({ 
            color: 0xf0f0f0,
            transparent: true,
            opacity: 0.8
        });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        this.scene.add(floor);
        
        // Add grid pattern
        const gridHelper = new THREE.GridHelper(30, 30, 0xcccccc, 0xcccccc);
        gridHelper.material.opacity = 0.3;
        gridHelper.material.transparent = true;
        this.scene.add(gridHelper);
    }
    
    createWalls() {
        const wallMaterial = new THREE.MeshLambertMaterial({ color: 0xe8e8e8 });
        
        // Back wall
        const backWallGeometry = new THREE.PlaneGeometry(30, 8);
        const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
        backWall.position.set(0, 4, -10);
        this.scene.add(backWall);
        
        // Side walls
        const sideWallGeometry = new THREE.PlaneGeometry(20, 8);
        
        const leftWall = new THREE.Mesh(sideWallGeometry, wallMaterial);
        leftWall.position.set(-15, 4, 0);
        leftWall.rotation.y = Math.PI / 2;
        this.scene.add(leftWall);
        
        const rightWall = new THREE.Mesh(sideWallGeometry, wallMaterial);
        rightWall.position.set(15, 4, 0);
        rightWall.rotation.y = -Math.PI / 2;
        this.scene.add(rightWall);
    }
    
    create3DPrinters() {
        const printerPositions = [-6, -2, 2];
        
        printerPositions.forEach((x, index) => {
            const printer = this.create3DPrinter();
            printer.position.set(x, 0, -6);
            printer.userData = {
                name: `Impresora 3D ${index + 1}`,
                description: `Impresora 3D para prototipado rápido y fabricación de objetos. Tecnología FDM con filamento PLA/ABS.`,
                type: 'equipment'
            };
            this.scene.add(printer);
            this.objects.push(printer);
        });
    }
    
    create3DPrinter() {
        const group = new THREE.Group();
        
        // Base
        const baseGeometry = new THREE.BoxGeometry(1.5, 0.2, 1.5);
        const baseMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.1;
        base.castShadow = true;
        group.add(base);
        
        // Frame
        const frameGeometry = new THREE.BoxGeometry(0.1, 2, 0.1);
        const frameMaterial = new THREE.MeshLambertMaterial({ color: 0x666666 });
        
        // Vertical frame posts
        const positions = [
            [-0.7, 1, -0.7], [0.7, 1, -0.7],
            [-0.7, 1, 0.7], [0.7, 1, 0.7]
        ];
        
        positions.forEach(pos => {
            const post = new THREE.Mesh(frameGeometry, frameMaterial);
            post.position.set(...pos);
            post.castShadow = true;
            group.add(post);
        });
        
        // Print bed
        const bedGeometry = new THREE.BoxGeometry(1.2, 0.05, 1.2);
        const bedMaterial = new THREE.MeshLambertMaterial({ color: 0x444444 });
        const bed = new THREE.Mesh(bedGeometry, bedMaterial);
        bed.position.y = 0.5;
        bed.castShadow = true;
        group.add(bed);
        
        // Extruder head
        const extruderGeometry = new THREE.BoxGeometry(0.3, 0.2, 0.3);
        const extruderMaterial = new THREE.MeshLambertMaterial({ color: 0xff6600 });
        const extruder = new THREE.Mesh(extruderGeometry, extruderMaterial);
        extruder.position.set(0.2, 1.2, 0.2);
        extruder.castShadow = true;
        group.add(extruder);
        
        return group;
    }
    
    createWorkTables() {
        const tablePositions = [
            [-6, 0, 2], [-2, 0, 2], [2, 0, 2], [6, 0, 2]
        ];
        
        tablePositions.forEach((pos, index) => {
            const table = this.createCollaborativeTable();
            table.position.set(...pos);
            table.userData = {
                name: `Mesa Colaborativa ${index + 1}`,
                description: `Mesa para trabajo en equipo con capacidad para 4-6 personas. Incluye conectividad eléctrica y espacios para dispositivos.`,
                type: 'furniture'
            };
            this.scene.add(table);
            this.objects.push(table);
            
            // Add chairs around table
            this.createChairsAroundTable(pos[0], pos[2]);
        });
    }
    
    createCollaborativeTable() {
        const group = new THREE.Group();
        
        // Table top
        const topGeometry = new THREE.BoxGeometry(2.5, 0.1, 1.5);
        const topMaterial = new THREE.MeshLambertMaterial({ color: 0x8b4513 });
        const top = new THREE.Mesh(topGeometry, topMaterial);
        top.position.y = 0.8;
        top.castShadow = true;
        top.receiveShadow = true;
        group.add(top);
        
        // Table legs
        const legGeometry = new THREE.CylinderGeometry(0.05, 0.05, 0.8);
        const legMaterial = new THREE.MeshLambertMaterial({ color: 0x555555 });
        
        const legPositions = [
            [-1, 0.4, -0.6], [1, 0.4, -0.6],
            [-1, 0.4, 0.6], [1, 0.4, 0.6]
        ];
        
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeometry, legMaterial);
            leg.position.set(...pos);
            leg.castShadow = true;
            group.add(leg);
        });
        
        return group;
    }
    
    createChairsAroundTable(tableX, tableZ) {
        const chairPositions = [
            [tableX - 1.8, tableZ], [tableX + 1.8, tableZ],
            [tableX, tableZ - 1.2], [tableX, tableZ + 1.2]
        ];
        
        chairPositions.forEach((pos, index) => {
            const chair = this.createChair();
            chair.position.set(pos[0], 0, pos[1]);
            
            // Rotate chairs to face table
            if (index < 2) chair.rotation.y = index === 0 ? Math.PI / 2 : -Math.PI / 2;
            else chair.rotation.y = index === 2 ? 0 : Math.PI;
            
            chair.userData = {
                name: 'Silla Ergonómica',
                description: 'Silla de trabajo ergonómica con respaldo ajustable y ruedas para facilitar el movimiento.',
                type: 'furniture'
            };
            
            this.scene.add(chair);
            this.objects.push(chair);
        });
    }
    
    createChair() {
        const group = new THREE.Group();
        
        // Seat
        const seatGeometry = new THREE.BoxGeometry(0.5, 0.05, 0.5);
        const seatMaterial = new THREE.MeshLambertMaterial({ color: 0x2c3e50 });
        const seat = new THREE.Mesh(seatGeometry, seatMaterial);
        seat.position.y = 0.45;
        seat.castShadow = true;
        group.add(seat);
        
        // Backrest
        const backGeometry = new THREE.BoxGeometry(0.5, 0.6, 0.05);
        const backMaterial = new THREE.MeshLambertMaterial({ color: 0x34495e });
        const back = new THREE.Mesh(backGeometry, backMaterial);
        back.position.set(0, 0.75, -0.22);
        back.castShadow = true;
        group.add(back);
        
        // Base
        const baseGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.05);
        const baseMaterial = new THREE.MeshLambertMaterial({ color: 0x7f8c8d });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.y = 0.1;
        base.castShadow = true;
        group.add(base);
        
        // Central post
        const postGeometry = new THREE.CylinderGeometry(0.03, 0.03, 0.3);
        const postMaterial = new THREE.MeshLambertMaterial({ color: 0x95a5a6 });
        const post = new THREE.Mesh(postGeometry, postMaterial);
        post.position.y = 0.3;
        post.castShadow = true;
        group.add(post);
        
        return group;
    }
    
    createStorageAreas() {
        // Left storage shelves
        const leftShelf = this.createShelfUnit();
        leftShelf.position.set(-10, 0, 6);
        leftShelf.userData = {
            name: 'Estantería de Materiales',
            description: 'Almacenamiento de materiales, herramientas y componentes para proyectos. Incluye filamentos para impresión 3D, componentes electrónicos y herramientas básicas.',
            type: 'storage'
        };
        this.scene.add(leftShelf);
        this.objects.push(leftShelf);
        
        // Right storage area
        const rightStorage = this.createStorageCabinet();
        rightStorage.position.set(10, 0, 6);
        rightStorage.userData = {
            name: 'Armario de Equipos',
            description: 'Almacenamiento seguro para equipos especializados, dispositivos de medición y proyectos en desarrollo.',
            type: 'storage'
        };
        this.scene.add(rightStorage);
        this.objects.push(rightStorage);
    }
    
    createShelfUnit() {
        const group = new THREE.Group();
        
        // Frame
        const frameGeometry = new THREE.BoxGeometry(2, 2.5, 0.4);
        const frameMaterial = new THREE.MeshLambertMaterial({ color: 0x8b4513 });
        const frame = new THREE.Mesh(frameGeometry, frameMaterial);
        frame.position.y = 1.25;
        frame.castShadow = true;
        group.add(frame);
        
        // Shelves
        const shelfGeometry = new THREE.BoxGeometry(1.8, 0.05, 0.35);
        const shelfMaterial = new THREE.MeshLambertMaterial({ color: 0xa0522d });
        
        for (let i = 0; i < 4; i++) {
            const shelf = new THREE.Mesh(shelfGeometry, shelfMaterial);
            shelf.position.set(0, 0.3 + (i * 0.6), 0);
            shelf.castShadow = true;
            shelf.receiveShadow = true;
            group.add(shelf);
        }
        
        return group;
    }
    
    createStorageCabinet() {
        const group = new THREE.Group();
        
        // Cabinet body
        const bodyGeometry = new THREE.BoxGeometry(1.5, 2, 0.6);
        const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x708090 });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.position.y = 1;
        body.castShadow = true;
        group.add(body);
        
        // Doors
        const doorGeometry = new THREE.BoxGeometry(0.7, 1.8, 0.05);
        const doorMaterial = new THREE.MeshLambertMaterial({ color: 0x778899 });
        
        const leftDoor = new THREE.Mesh(doorGeometry, doorMaterial);
        leftDoor.position.set(-0.35, 1, 0.32);
        leftDoor.castShadow = true;
        group.add(leftDoor);
        
        const rightDoor = new THREE.Mesh(doorGeometry, doorMaterial);
        rightDoor.position.set(0.35, 1, 0.32);
        rightDoor.castShadow = true;
        group.add(rightDoor);
        
        return group;
    }
    
    createDigitalBoard() {
        const group = new THREE.Group();
        
        // Board frame
        const frameGeometry = new THREE.BoxGeometry(3, 2, 0.1);
        const frameMaterial = new THREE.MeshLambertMaterial({ color: 0x2c3e50 });
        const frame = new THREE.Mesh(frameGeometry, frameMaterial);
        frame.position.set(0, 2, -9.8);
        frame.castShadow = true;
        group.add(frame);
        
        // Screen
        const screenGeometry = new THREE.BoxGeometry(2.8, 1.8, 0.02);
        const screenMaterial = new THREE.MeshLambertMaterial({ color: 0x1a1a1a });
        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        screen.position.set(0, 2, -9.75);
        group.add(screen);
        
        // Add some glow effect
        const glowGeometry = new THREE.BoxGeometry(2.9, 1.9, 0.05);
        const glowMaterial = new THREE.MeshLambertMaterial({ 
            color: 0x4a90e2,
            transparent: true,
            opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.set(0, 2, -9.73);
        group.add(glow);
        
        group.userData = {
            name: 'Pizarra Digital Interactiva',
            description: 'Display interactivo de gran formato para presentaciones, colaboración y visualización de proyectos. Incluye capacidades táctiles y conectividad inalámbrica.',
            type: 'equipment'
        };
        
        this.scene.add(group);
        this.objects.push(group);
    }
    
    createSpecializedEquipment() {
        // Electronics workstation
        const electronics = this.createElectronicsStation();
        electronics.position.set(0, 0, 8);
        electronics.userData = {
            name: 'Estación de Electrónica',
            description: 'Estación especializada para desarrollo de proyectos electrónicos. Incluye osciloscopio, fuente de alimentación, multímetros y herramientas de soldadura.',
            type: 'equipment'
        };
        this.scene.add(electronics);
        this.objects.push(electronics);
        
        // Computer workstation
        const computer = this.createComputerStation();
        computer.position.set(8, 0, 8);
        computer.userData = {
            name: 'Estación de Desarrollo',
            description: 'Computadora de alto rendimiento para desarrollo de software, diseño 3D, simulaciones y procesamiento de datos.',
            type: 'equipment'
        };
        this.scene.add(computer);
        this.objects.push(computer);
    }
    
    createElectronicsStation() {
        const group = new THREE.Group();
        
        // Workbench
        const benchGeometry = new THREE.BoxGeometry(2, 0.1, 1);
        const benchMaterial = new THREE.MeshLambertMaterial({ color: 0x8b4513 });
        const bench = new THREE.Mesh(benchGeometry, benchMaterial);
        bench.position.y = 0.8;
        bench.castShadow = true;
        bench.receiveShadow = true;
        group.add(bench);
        
        // Equipment boxes (oscilloscope, power supply, etc.)
        const equipmentPositions = [
            [-0.6, 0.9, -0.2], [0, 0.9, -0.2], [0.6, 0.9, -0.2]
        ];
        
        equipmentPositions.forEach((pos, index) => {
            const equipGeometry = new THREE.BoxGeometry(0.4, 0.15, 0.3);
            const colors = [0x4a4a4a, 0x6a6a6a, 0x5a5a5a];
            const equipMaterial = new THREE.MeshLambertMaterial({ color: colors[index] });
            const equip = new THREE.Mesh(equipGeometry, equipMaterial);
            equip.position.set(...pos);
            equip.castShadow = true;
            group.add(equip);
            
            // Add some LEDs/displays
            const ledGeometry = new THREE.BoxGeometry(0.05, 0.02, 0.05);
            const ledMaterial = new THREE.MeshLambertMaterial({ color: 0x00ff00 });
            const led = new THREE.Mesh(ledGeometry, ledMaterial);
            led.position.set(pos[0] - 0.1, pos[1] + 0.08, pos[2] + 0.16);
            group.add(led);
        });
        
        // Legs
        const legGeometry = new THREE.BoxGeometry(0.1, 0.8, 0.1);
        const legMaterial = new THREE.MeshLambertMaterial({ color: 0x555555 });
        const legPositions = [
            [-0.9, 0.4, -0.4], [0.9, 0.4, -0.4],
            [-0.9, 0.4, 0.4], [0.9, 0.4, 0.4]
        ];
        
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeometry, legMaterial);
            leg.position.set(...pos);
            leg.castShadow = true;
            group.add(leg);
        });
        
        return group;
    }
    
    createComputerStation() {
        const group = new THREE.Group();
        
        // Desk
        const deskGeometry = new THREE.BoxGeometry(1.5, 0.1, 0.8);
        const deskMaterial = new THREE.MeshLambertMaterial({ color: 0x8b4513 });
        const desk = new THREE.Mesh(deskGeometry, deskMaterial);
        desk.position.y = 0.8;
        desk.castShadow = true;
        desk.receiveShadow = true;
        group.add(desk);
        
        // Monitor
        const monitorGeometry = new THREE.BoxGeometry(0.6, 0.4, 0.05);
        const monitorMaterial = new THREE.MeshLambertMaterial({ color: 0x2c3e50 });
        const monitor = new THREE.Mesh(monitorGeometry, monitorMaterial);
        monitor.position.set(0, 1.2, -0.2);
        monitor.castShadow = true;
        group.add(monitor);
        
        // Computer tower
        const towerGeometry = new THREE.BoxGeometry(0.2, 0.5, 0.4);
        const towerMaterial = new THREE.MeshLambertMaterial({ color: 0x34495e });
        const tower = new THREE.Mesh(towerGeometry, towerMaterial);
        tower.position.set(0.5, 1.05, 0.2);
        tower.castShadow = true;
        group.add(tower);
        
        // Keyboard
        const keyboardGeometry = new THREE.BoxGeometry(0.4, 0.02, 0.15);
        const keyboardMaterial = new THREE.MeshLambertMaterial({ color: 0x2c3e50 });
        const keyboard = new THREE.Mesh(keyboardGeometry, keyboardMaterial);
        keyboard.position.set(0, 0.86, 0.1);
        keyboard.castShadow = true;
        group.add(keyboard);
        
        return group;
    }
    
    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Mouse events for interaction
        this.renderer.domElement.addEventListener('mousemove', (event) => this.onMouseMove(event));
        this.renderer.domElement.addEventListener('click', (event) => this.onMouseClick(event));
        
        // Control buttons
        document.getElementById('resetCamera').addEventListener('click', () => this.resetCamera());
        document.getElementById('topView').addEventListener('click', () => this.setTopView());
        document.getElementById('walkthrough').addEventListener('click', () => this.startWalkthrough());
        document.getElementById('toggleInfo').addEventListener('click', () => this.toggleInfo());
        document.getElementById('closeInfo').addEventListener('click', () => this.hideObjectInfo());
    }
    
    onWindowResize() {
        const container = document.getElementById('lab3d');
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }
    
    onMouseMove(event) {
        const container = document.getElementById('lab3d');
        const rect = container.getBoundingClientRect();
        
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Raycasting for hover effects
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.objects, true);
        
        if (intersects.length > 0) {
            const object = intersects[0].object.parent || intersects[0].object;
            
            if (this.hoveredObject !== object) {
                if (this.hoveredObject) {
                    this.unhighlightObject(this.hoveredObject);
                }
                this.hoveredObject = object;
                this.highlightObject(object);
                container.style.cursor = 'pointer';
            }
        } else {
            if (this.hoveredObject) {
                this.unhighlightObject(this.hoveredObject);
                this.hoveredObject = null;
                container.style.cursor = 'default';
            }
        }
    }
    
    onMouseClick(event) {
        if (this.hoveredObject && this.hoveredObject.userData) {
            this.showObjectInfo(this.hoveredObject.userData);
        }
    }
    
    highlightObject(object) {
        object.traverse((child) => {
            if (child.isMesh && child.material) {
                child.userData.originalColor = child.material.color.getHex();
                child.material.color.setHex(0x4a90e2);
            }
        });
    }
    
    unhighlightObject(object) {
        object.traverse((child) => {
            if (child.isMesh && child.material && child.userData.originalColor !== undefined) {
                child.material.color.setHex(child.userData.originalColor);
            }
        });
    }
    
    showObjectInfo(userData) {
        const infoPanel = document.getElementById('objectInfo');
        const title = document.getElementById('objectTitle');
        const description = document.getElementById('objectDescription');
        
        title.textContent = userData.name;
        description.textContent = userData.description;
        
        infoPanel.classList.remove('hidden');
    }
    
    hideObjectInfo() {
        const infoPanel = document.getElementById('objectInfo');
        infoPanel.classList.add('hidden');
    }
    
    resetCamera() {
        this.camera.position.set(15, 12, 15);
        this.camera.lookAt(0, 0, 0);
        this.controls.update();
    }
    
    setTopView() {
        this.camera.position.set(0, 25, 0);
        this.camera.lookAt(0, 0, 0);
        this.controls.update();
    }
    
    startWalkthrough() {
        // Implement guided tour animation
        const positions = [
            { pos: [15, 12, 15], target: [0, 0, 0] },  // Overview
            { pos: [0, 8, -12], target: [0, 2, -6] },  // 3D Printers
            { pos: [0, 5, 5], target: [0, 1, 2] },     // Work tables
            { pos: [-12, 6, 8], target: [-10, 2, 6] }, // Storage
            { pos: [12, 6, 8], target: [8, 2, 8] },    // Computer station
        ];
        
        let currentStep = 0;
        const animateStep = () => {
            if (currentStep >= positions.length) return;
            
            const step = positions[currentStep];
            const duration = 3000; // 3 seconds per step
            const startPos = this.camera.position.clone();
            const startTime = Date.now();
            
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Smooth interpolation
                const easedProgress = this.easeInOutCubic(progress);
                
                this.camera.position.lerpVectors(startPos, new THREE.Vector3(...step.pos), easedProgress);
                this.camera.lookAt(...step.target);
                this.controls.update();
                
                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    currentStep++;
                    setTimeout(animateStep, 1000); // Pause between steps
                }
            };
            animate();
        };
        
        animateStep();
    }
    
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
    }
    
    toggleInfo() {
        const infoPanel = document.getElementById('labInfo');
        const button = document.getElementById('toggleInfo');
        
        if (infoPanel.style.display === 'none') {
            infoPanel.style.display = 'block';
            button.classList.add('active');
        } else {
            infoPanel.style.display = 'none';
            button.classList.remove('active');
        }
    }
    
    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        loadingScreen.classList.add('hidden');
        this.isLoading = false;
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (!this.isLoading) {
            this.controls.update();
            this.renderer.render(this.scene, this.camera);
        }
    }
}

// Initialize the virtual lab when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VirtualLab();
});
