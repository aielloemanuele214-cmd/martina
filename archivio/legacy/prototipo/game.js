// game.js - 2D Pokémon Style Room Exploration Game (UPGRADED VERSION)
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Load AI-generated title image
const titleImg = new Image();
titleImg.src = 'assets/title_screen.jpg';
let titleImgLoaded = false;
titleImg.onload = () => {
    titleImgLoaded = true;
};

// Game state variables
let gameState = 'title'; // 'title', 'play', 'dialogue', 'polaroid', 'finale'
let player = {
    x: 8, // Grid X
    y: 8, // Grid Y
    screenX: 8 * 16,
    screenY: 8 * 16,
    dir: 'down', // 'up', 'down', 'left', 'right'
    isMoving: false,
    moveAnim: 0, // 0 to 1 transition progress
    targetX: 8,
    targetY: 8,
    speed: 0.1, // Movement transition speed
    path: [] // Path for auto-walk
};

// Partner (Lui) standing at the center
const partner = {
    x: 7,
    y: 8,
    dir: 'right'
};

// Map size and configuration
const TILE_SIZE = 16;
const MAP_WIDTH = 16;
const MAP_HEIGHT = 16;

// 16x16 Room Map
// 0: Floor (walkable)
// 1: Wall/Wood panel (collision)
// 2: Bed top (interactive) / 14: Bed top triggered
// 10: Bed bottom (interactive) / 15: Bed bottom triggered
// 3: TV (interactive) / 13: TV triggered
// 11: TV table side (collision)
// 4: Dresser (interactive) / 12: Dresser triggered
// 5: Plant (interactive) / 16: Plant triggered
// 6: Window (decorative wall)
// 7: Door/Exit (decorative wall)
// 9: Heart Rug (walkable, decorative floor)
// 17: Fireplace top (collision)
// 18: Fireplace bottom (collision, animated fire)
const map = [
    [1, 1, 1, 6, 1, 1, 6, 1, 1, 6, 17, 17, 6, 1, 1, 1],
    [1, 2, 2, 0, 0, 3, 3, 3, 0, 0, 18, 18, 0, 5, 5, 1],
    [1, 10, 10, 0, 0, 11, 3, 11, 0, 0, 0, 0, 0, 5, 5, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 9, 9, 9, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 9, 9, 9, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 7, 7, 1, 1, 1, 1, 1, 1, 1]
];

// Interactive Items Configuration
const memories = {
    bed: {
        id: 'bed',
        name: 'Il Letto dei Sogni',
        x: 2, y: 1,
        triggered: false,
        title: 'Il nostro primo incontro',
        text: 'Ti ricordi il nostro primo incontro? Quella timidezza iniziale, i sorrisi rubati e l\'emozione di stringerti la mano per la prima volta. Sembra passata un\'eternità, eppure ogni giorno con te è come il primo giorno.'
    },
    tv: {
        id: 'tv',
        name: 'La TV dei Film',
        x: 6, y: 3,
        triggered: false,
        title: 'Le serate passate a ridere',
        text: 'Quante serate passate sul divano, abbracciati sotto le coperte, a guardare film o serie tv di cui a volte dimentichiamo la trama. Non importa cosa guardiamo: l\'unica cosa che conta davvero è che siamo insieme.'
    },
    dresser: {
        id: 'dresser',
        name: 'La Cassettiera dei Viaggi',
        x: 2, y: 13,
        triggered: false,
        title: 'Crescere insieme',
        text: 'Ogni cassetto della nostra vita è pieno di ricordi speciali: biglietti di treni e aerei, scontrini di cene romantiche e piccoli oggetti che raccontano la nostra crescita. Costruiamo il nostro futuro, un giorno alla volta.'
    },
    plant: {
        id: 'plant',
        name: 'La Pianta dell\'Amore',
        x: 13, y: 2,
        triggered: false,
        title: 'Un amore che fiorisce',
        text: 'Proprio come questa pianta, il nostro legame cresce giorno dopo giorno, nutrito con cure quotidiane, sorrisi, baci e tanta pazienza. È bellissimo vedere come il nostro amore fiorisce e si rafforza nel tempo.'
    }
};

let activeMemory = null;
let triggeredCount = 0;
const totalMemories = 4;

// Dialogue System variables
let dialogueQueue = [];
let dialogueIndex = 0;
let dialogueTextVisible = '';
let dialogueCharIndex = 0;
let dialogueTypingTimer = null;
let isDialogueReady = false;

// Heart particles
let heartParticles = [];
let frameCount = 0;

// Fade transition system
let fadeAlpha = 0;
let fadeDirection = 0; // 0: no fade, 1: fading in (to black), -1: fading out (from black)
let fadeCallback = null;

// Burst particles on memory discovery
let burstParticles = [];

// Sparkles on active memories
let sparkles = [
    { x: 1, y: 1, active: true }, // Bed
    { x: 6, y: 1, active: true }, // TV
    { x: 1, y: 13, active: true }, // Dresser
    { x: 14, y: 1, active: true } // Plant
];

// Initialize Game
function init() {
    setupControls();
    setupFullscreen();
    simulateLoading();
    gameLoop();
}

// Simulated loading screen with progress bar
function simulateLoading() {
    const bar = document.getElementById('loadingBar');
    const screen = document.getElementById('loadingScreen');
    let progress = 0;
    const loadInterval = setInterval(() => {
        progress += 5 + Math.random() * 10;
        if (progress >= 100) {
            progress = 100;
            clearInterval(loadInterval);
            bar.style.width = '100%';
            setTimeout(() => {
                screen.classList.add('loaded');
                setTimeout(() => screen.remove(), 600);
            }, 400);
        } else {
            bar.style.width = progress + '%';
        }
    }, 120);
}

// Fullscreen API integration
function setupFullscreen() {
    const btn = document.getElementById('fullscreenBtn');
    btn.addEventListener('click', () => {
        const el = document.documentElement;
        if (!document.fullscreenElement) {
            if (el.requestFullscreen) el.requestFullscreen();
            else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
            else if (el.msRequestFullscreen) el.msRequestFullscreen();
        } else {
            if (document.exitFullscreen) document.exitFullscreen();
            else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
        }
    });
}

// Active key/D-pad movement state
const activeKeys = {
    up: false,
    down: false,
    left: false,
    right: false
};

function resetInputs() {
    activeKeys.up = false;
    activeKeys.down = false;
    activeKeys.left = false;
    activeKeys.right = false;
}

// Controller inputs setup
function setupControls() {
    window.addEventListener('keydown', (e) => {
        if (gameState === 'title') {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'a' || e.key === 'A') {
                startGame();
            }
            return;
        }

        if (gameState === 'play') {
            if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') { activeKeys.up = true; e.preventDefault(); }
            else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') { activeKeys.down = true; e.preventDefault(); }
            else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') { activeKeys.left = true; e.preventDefault(); }
            else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') { activeKeys.right = true; e.preventDefault(); }
            
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                interact();
            }
        } else if (gameState === 'dialogue') {
            if (e.key === ' ' || e.key === 'Enter' || e.key === 'a' || e.key === 'A') {
                e.preventDefault();
                advanceDialogue();
            }
        } else if (gameState === 'polaroid') {
            if (e.key === ' ' || e.key === 'Enter' || e.key === 'b' || e.key === 'B' || e.key === 'Escape') {
                e.preventDefault();
                closePolaroid();
            }
        }
    });

    window.addEventListener('keyup', (e) => {
        if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') activeKeys.up = false;
        else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') activeKeys.down = false;
        else if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') activeKeys.left = false;
        else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') activeKeys.right = false;
    });

    // Mobile D-pad inputs with pointer listeners for holding down
    const dpadButtons = {
        'pad-up': 'up',
        'pad-down': 'down',
        'pad-left': 'left',
        'pad-right': 'right'
    };
    
    for (const id in dpadButtons) {
        const btn = document.getElementById(id);
        const dir = dpadButtons[id];
        
        btn.addEventListener('pointerdown', (e) => {
            e.preventDefault();
            if (gameState === 'play') {
                player.path = [];
                activeKeys[dir] = true;
                player.dir = dir;
            }
        });
        
        const stopDir = (e) => {
            e.preventDefault();
            activeKeys[dir] = false;
        };
        
        btn.addEventListener('pointerup', stopDir);
        btn.addEventListener('pointerleave', stopDir);
        btn.addEventListener('pointercancel', stopDir);
    }
    
    // Action buttons
    document.getElementById('btn-a').addEventListener('click', () => {
        if (gameState === 'title') startGame();
        else if (gameState === 'play') interact();
        else if (gameState === 'dialogue') advanceDialogue();
    });
    
    document.getElementById('btn-b').addEventListener('click', () => {
        if (gameState === 'polaroid') closePolaroid();
    });

    document.getElementById('btn-start').addEventListener('click', () => {
        if (gameState === 'title') startGame();
    });

    // Auto-walk clicking
    canvas.addEventListener('click', (e) => {
        if (gameState !== 'play') return;
        const rect = canvas.getBoundingClientRect();
        const clickX = Math.floor((e.clientX - rect.left) / (rect.width / MAP_WIDTH));
        const clickY = Math.floor((e.clientY - rect.top) / (rect.height / MAP_HEIGHT));
        
        if (clickX >= 0 && clickX < MAP_WIDTH && clickY >= 0 && clickY < MAP_HEIGHT) {
            findPathTo(clickX, clickY);
        }
    });

    // Audio Switch
    document.getElementById('audioToggle').addEventListener('click', () => {
        const isMuted = GameAudio.toggleMute();
        const icon = document.getElementById('soundIcon');
        icon.innerText = isMuted ? '🔇' : '🔊';
        GameAudio.playSFX('click');
    });
}

function startGame() {
    GameAudio.init();
    GameAudio.playSFX('click');
    
    startFade(1, () => {
        gameState = 'play';
        document.getElementById('powerLed').classList.add('on');
        GameAudio.startMelody();
        
        triggerDialogue([
            "Sofia: Uh? Dove ci troviamo...?",
            "Lui: Ciao Sofia! Buon Anniversario! ❤️",
            "Lui: Ho nascosto 4 ricordi speciali in questa stanza.",
            "Lui: Esplora i punti luminosi per trovarli tutti!"
        ]);
    });
}

function movePlayer(dx, dy) {
    if (player.isMoving) return;

    const nextX = player.x + dx;
    const nextY = player.y + dy;

    if (nextX < 0 || nextX >= MAP_WIDTH || nextY < 0 || nextY >= MAP_HEIGHT) return;

    if (isCollidable(nextX, nextY)) return;

    player.targetX = nextX;
    player.targetY = nextY;
    player.isMoving = true;
    player.moveAnim = 0;
    
    // Differentiated footstep sounds based on surface
    const destTile = map[nextY][nextX];
    if (destTile === 9) {
        GameAudio.playSFX('step_carpet');
    } else {
        GameAudio.playSFX('step_wood');
    }
}

function isCollidable(x, y) {
    const tile = map[y][x];
    // Check collidable tiles including triggered variants
    const collidables = [1, 2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18];
    if (collidables.includes(tile)) {
        return true;
    }
    
    if (x === partner.x && y === partner.y) {
        return true;
    }
    
    return false;
}

function interact() {
    let checkX = player.x;
    let checkY = player.y;

    if (player.dir === 'up') checkY--;
    else if (player.dir === 'down') checkY++;
    else if (player.dir === 'left') checkX--;
    else if (player.dir === 'right') checkX++;

    // Partner interaction
    if (checkX === partner.x && checkY === partner.y) {
        partner.dir = getOppositeDirection(player.dir);
        GameAudio.playSFX('click');
        if (triggeredCount === totalMemories) {
            triggerDialogue([
                "Lui: Incredibile, hai trovato tutti i ricordi!",
                "Lui: Ora... apri la Pokéball finale!"
            ]);
        } else {
            triggerDialogue([
                "Lui: Ehi Sofia! Hai trovato solo " + triggeredCount + " di " + totalMemories + " ricordi.",
                "Lui: Cerca nei cassetti, sul letto, nella pianta e sulla TV!"
            ]);
        }
        return;
    }

    // Interactive items interaction
    for (const key in memories) {
        const item = memories[key];
        if (isNearMemory(checkX, checkY, item.id)) {
            triggerMemory(item);
            return;
        }
    }
}

function isNearMemory(x, y, id) {
    const tile = map[y]?.[x];
    if (id === 'bed' && [2, 10, 14, 15].includes(tile)) return true;
    if (id === 'tv' && [3, 11, 13].includes(tile)) return true;
    if (id === 'dresser' && [4, 12].includes(tile)) return true;
    if (id === 'plant' && [5, 16].includes(tile)) return true;
    return false;
}

function triggerDialogue(lines) {
    resetInputs();
    gameState = 'dialogue';
    dialogueQueue = lines;
    dialogueIndex = 0;
    document.getElementById('dialogueBox').style.display = 'flex';
    showDialogueLine();
}

function showDialogueLine() {
    if (dialogueIndex >= dialogueQueue.length) {
        closeDialogue();
        return;
    }

    const line = dialogueQueue[dialogueIndex];
    dialogueTextVisible = '';
    dialogueCharIndex = 0;
    isDialogueReady = false;
    document.getElementById('dialogueArrow').style.display = 'none';

    if (dialogueTypingTimer) clearInterval(dialogueTypingTimer);
    
    dialogueTypingTimer = setInterval(() => {
        if (dialogueCharIndex < line.length) {
            dialogueTextVisible += line[dialogueCharIndex];
            document.getElementById('dialogueText').innerText = dialogueTextVisible;
            dialogueCharIndex++;
            if (dialogueCharIndex % 3 === 0) {
                GameAudio.playSFX('rustle');
            }
        } else {
            clearInterval(dialogueTypingTimer);
            isDialogueReady = true;
            document.getElementById('dialogueArrow').style.display = 'block';
        }
    }, 30);
}

function advanceDialogue() {
    if (!isDialogueReady) {
        clearInterval(dialogueTypingTimer);
        document.getElementById('dialogueText').innerText = dialogueQueue[dialogueIndex];
        isDialogueReady = true;
        document.getElementById('dialogueArrow').style.display = 'block';
    } else {
        dialogueIndex++;
        showDialogueLine();
    }
}

function closeDialogue() {
    document.getElementById('dialogueBox').style.display = 'none';
    if (activeMemory) {
        openPolaroidCard(activeMemory);
    } else {
        gameState = 'play';
        if (triggeredCount === totalMemories) {
            triggerFinalCelebration();
        }
    }
}

// Trigger memory inspection and activate item animations on map
function triggerMemory(item) {
    activeMemory = item;
    let isNew = !item.triggered;
    
    if (isNew) {
        item.triggered = true;
        triggeredCount++;
        
        // Disable sparkle
        sparkles = sparkles.map(s => {
            if (item.id === 'bed' && s.x === 1 && s.y === 1) return { ...s, active: false };
            if (item.id === 'tv' && s.x === 6 && s.y === 1) return { ...s, active: false };
            if (item.id === 'dresser' && s.x === 1 && s.y === 13) return { ...s, active: false };
            if (item.id === 'plant' && s.x === 14 && s.y === 1) return { ...s, active: false };
            return s;
        });

        // Trigger visual changes on map and unique sound effects
        if (item.id === 'tv') {
            map[1][6] = 13; // TV active state (screen turns blue/heart pulses)
            GameAudio.playSFX('tv_on');
        } else if (item.id === 'dresser') {
            map[13][1] = 12; // Dresser open (gold glow inside drawer)
            GameAudio.playSFX('drawer');
        } else if (item.id === 'bed') {
            map[1][1] = 14; // Bed tilted pillow
            map[2][1] = 15; // Bed duvet messed up
            GameAudio.playSFX('item');
        } else if (item.id === 'plant') {
            map[1][13] = 16; // Plant with red flower
            map[2][13] = 16;
            GameAudio.playSFX('item');
        }
    } else {
        GameAudio.playSFX('click');
    }

    triggerDialogue([
        `Hai esaminato: ${item.name}!`,
        isNew ? "Un ricordo si è aperto..." : "Un ricordo speciale che conosciamo bene..."
    ]);

    // Update memory tracker hearts in the console UI
    if (isNew) {
        updateMemoryTracker();
        // Spawn burst particles at the item location
        spawnBurstParticles(item.x * TILE_SIZE + TILE_SIZE / 2, item.y * TILE_SIZE + TILE_SIZE / 2);
        // Mobile haptic feedback
        if (navigator.vibrate) navigator.vibrate(100);
    }
}

// Open themed memory card modal
function openPolaroidCard(item) {
    resetInputs();
    gameState = 'polaroid';
    
    const modal = document.getElementById('polaroidModal');
    const title = document.getElementById('polaroidTitle');
    const text = document.getElementById('polaroidText');
    const canvasArt = document.getElementById('polaroidCanvasArt');
    const cardElement = document.getElementById('polaroidCard');
    
    // Apply theme classes (card-tv, card-dresser, card-bed, card-plant)
    cardElement.className = `memory-card card-${item.id}`;
    
    title.innerText = item.title;
    text.innerText = item.text;
    
    drawPolaroidArt(canvasArt, item.id);
    
    modal.classList.add('show');
    GameAudio.playSFX('item');
}

function closePolaroid() {
    const modal = document.getElementById('polaroidModal');
    modal.classList.remove('show');
    activeMemory = null;
    gameState = 'play';
    
    if (triggeredCount === totalMemories) {
        triggerFinalCelebration();
    }
}

// Draw custom high-detail retro pixel art inside the memory card
function drawPolaroidArt(canvasElement, itemId) {
    const pCtx = canvasElement.getContext('2d');
    pCtx.imageSmoothingEnabled = false;
    pCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

    if (itemId === 'tv') {
        // Neon blue background grid
        pCtx.fillStyle = '#0f1115';
        pCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Scanlines inside TV art
        pCtx.fillStyle = 'rgba(255,255,255,0.05)';
        for(let i=0; i<canvasElement.height; i+=4) {
            pCtx.fillRect(0, i, canvasElement.width, 2);
        }

        // Draw pixel couple silhouette watching TV
        pCtx.fillStyle = '#ffd166'; // Glowing yellow TV beam
        pCtx.beginPath();
        pCtx.moveTo(canvasElement.width/2, 20);
        pCtx.lineTo(15, canvasElement.height - 10);
        pCtx.lineTo(canvasElement.width - 15, canvasElement.height - 10);
        pCtx.closePath();
        pCtx.fill();

        // TV outline
        pCtx.fillStyle = '#ff758f';
        pCtx.fillRect(canvasElement.width/2 - 16, 12, 32, 22);
        pCtx.fillStyle = '#98f5e1';
        pCtx.fillRect(canvasElement.width/2 - 12, 16, 24, 14);
        
        // Beating red heart inside screen
        pCtx.fillStyle = '#ff3366';
        drawPixelHeart(pCtx, canvasElement.width/2, 23, 2);

        // Couple silhouette in foreground (sitting)
        pCtx.fillStyle = '#222';
        pCtx.fillRect(canvasElement.width/2 - 12, canvasElement.height - 25, 10, 16); // Partner
        pCtx.fillRect(canvasElement.width/2 + 2, canvasElement.height - 25, 10, 16);  // Player
        // Heads
        pCtx.fillRect(canvasElement.width/2 - 11, canvasElement.height - 33, 8, 8);
        pCtx.fillRect(canvasElement.width/2 + 3, canvasElement.height - 33, 8, 8);
    } 
    else if (itemId === 'dresser') {
        // Warm brown oak background
        pCtx.fillStyle = '#ffeedb';
        pCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Draw a cozy open chest/dresser drawer overflowing with golden hearts
        pCtx.fillStyle = '#8b5e3c'; // Outer drawer front
        pCtx.fillRect(15, canvasElement.height/2 - 10, canvasElement.width - 30, 36);
        pCtx.fillStyle = '#eed6c4'; // Open drawer inside
        pCtx.fillRect(20, canvasElement.height/2 - 16, canvasElement.width - 40, 18);
        
        // Golden glowing items and envelopes inside
        pCtx.fillStyle = '#ffd166';
        pCtx.fillRect(30, canvasElement.height/2 - 20, 12, 10); // Envelope
        pCtx.fillRect(canvasElement.width - 42, canvasElement.height/2 - 22, 10, 12);
        
        // Red pixel hearts flying out of it
        pCtx.fillStyle = '#ff4d6d';
        drawPixelHeart(pCtx, canvasElement.width/2 - 15, canvasElement.height/2 - 25, 2);
        drawPixelHeart(pCtx, canvasElement.width/2 + 15, canvasElement.height/2 - 29, 1.5);
        drawPixelHeart(pCtx, canvasElement.width/2, canvasElement.height/2 - 32, 2.5);

        // Drawer handles
        pCtx.fillStyle = '#ffd166';
        pCtx.fillRect(canvasElement.width/2 - 15, canvasElement.height/2 + 8, 30, 4);
    } 
    else if (itemId === 'bed') {
        // Deep indigo night sky background with stars
        pCtx.fillStyle = '#1e1b4b';
        pCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Draw golden pixel stars
        pCtx.fillStyle = '#ffd166';
        pCtx.fillRect(15, 15, 2, 2);
        pCtx.fillRect(80, 20, 2, 2);
        pCtx.fillRect(35, 45, 2, 2);
        pCtx.fillRect(70, 50, 2, 2);
        
        // Floating cloud in the center
        pCtx.fillStyle = '#ffffff';
        pCtx.fillRect(canvasElement.width/2 - 24, canvasElement.height/2 - 15, 48, 20);
        pCtx.fillRect(canvasElement.width/2 - 16, canvasElement.height/2 - 20, 32, 26);
        pCtx.fillRect(canvasElement.width/2 - 28, canvasElement.height/2 - 10, 56, 12);
        
        // Beating heart on top of cloud
        pCtx.fillStyle = '#ff4d6d';
        const pulse = 2.5 + Math.sin(frameCount * 0.1) * 0.3;
        drawPixelHeart(pCtx, canvasElement.width/2, canvasElement.height/2 - 7, pulse);
    } 
    else if (itemId === 'plant') {
        // Soft green greenhouse grid background
        pCtx.fillStyle = '#e8f5e9';
        pCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);
        
        // Draw a flowerpot growing a giant rose
        pCtx.fillStyle = '#a06e4a'; // Flower pot
        pCtx.fillRect(canvasElement.width/2 - 14, canvasElement.height - 30, 28, 24);
        pCtx.fillStyle = '#8b5e3c'; // Rim
        pCtx.fillRect(canvasElement.width/2 - 17, canvasElement.height - 34, 34, 5);
        
        // Leaves and stem
        pCtx.fillStyle = '#2d6a4f'; // Green stem
        pCtx.fillRect(canvasElement.width/2 - 2, 25, 4, 30);
        pCtx.fillRect(canvasElement.width/2 - 16, 35, 14, 4); // Left leaf
        pCtx.fillRect(canvasElement.width/2 + 2, 42, 12, 4);  // Right leaf
        
        // Beautiful red rose bud on top
        pCtx.fillStyle = '#c9184a';
        pCtx.fillRect(canvasElement.width/2 - 10, 10, 20, 16);
        pCtx.fillStyle = '#ff4d6d'; // Highlights
        pCtx.fillRect(canvasElement.width/2 - 6, 13, 12, 10);
        pCtx.fillStyle = '#ff8fa3';
        pCtx.fillRect(canvasElement.width/2 - 3, 16, 6, 4);
    }
}

function drawPixelHeart(pCtx, cx, cy, scale) {
    const heartData = [
        [0,1,1,0,1,1,0],
        [1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1],
        [0,1,1,1,1,1,0],
        [0,0,1,1,1,0,0],
        [0,0,0,1,0,0,0]
    ];
    const rows = heartData.length;
    const cols = heartData[0].length;
    const startX = cx - (cols * scale) / 2;
    const startY = cy - (rows * scale) / 2;
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (heartData[r][c] === 1) {
                pCtx.fillRect(startX + c * scale, startY + r * scale, scale, scale);
            }
        }
    }
}

// Final celebration heart shower and letter overlay
function triggerFinalCelebration() {
    gameState = 'finale';
    GameAudio.stopMelody();
    GameAudio.playSFX('fanfare');
    
    heartParticles = [];
    for (let i = 0; i < 40; i++) {
        heartParticles.push({
            x: Math.random() * canvas.width,
            y: canvas.height + Math.random() * 50,
            vy: -1 - Math.random() * 2,
            size: 4 + Math.random() * 6,
            color: ['#ff4d6d', '#ff758f', '#ff8fa3', '#ffccd5', '#ffb3c1'][Math.floor(Math.random() * 5)],
            sway: Math.random() * 100,
            swaySpeed: 0.02 + Math.random() * 0.05
        });
    }

    setTimeout(() => {
        document.getElementById('letterOverlay').classList.add('show');
    }, 2000);
}

function restartGame() {
    resetInputs();
    document.getElementById('letterOverlay').classList.remove('show');
    gameState = 'title';
    triggeredCount = 0;
    activeMemory = null;
    player.x = 8;
    player.y = 8;
    player.screenX = 8 * 16;
    player.screenY = 8 * 16;
    player.isMoving = false;
    player.path = [];
    
    // Reset all map coordinates to default closed states
    map[1][6] = 3;   // Reset TV
    map[13][1] = 4;  // Reset Dresser
    map[1][1] = 2;   // Reset Bed top
    map[2][1] = 10;  // Reset Bed bottom
    map[1][13] = 5;  // Reset Plant
    map[2][13] = 5;
    
    for (const key in memories) {
        memories[key].triggered = false;
    }
    sparkles = [
        { x: 1, y: 1, active: true },
        { x: 6, y: 1, active: true },
        { x: 1, y: 13, active: true },
        { x: 14, y: 1, active: true }
    ];
    burstParticles = [];
    
    // Reset memory tracker hearts
    document.querySelectorAll('.tracker-heart').forEach(h => {
        h.classList.remove('found');
        h.innerHTML = '♡';
    });
    
    document.getElementById('powerLed').classList.remove('on');
    GameAudio.stopMelody();
}

document.getElementById('btnRestart').addEventListener('click', restartGame);

// Memory tracker heart updater
function updateMemoryTracker() {
    const hearts = document.querySelectorAll('.tracker-heart');
    const memoryOrder = ['bed', 'tv', 'dresser', 'plant'];
    memoryOrder.forEach((key, i) => {
        if (memories[key].triggered && hearts[i]) {
            hearts[i].classList.add('found');
            hearts[i].innerHTML = '❤️';
        }
    });
}

// Burst particle spawner for memory discoveries
function spawnBurstParticles(cx, cy) {
    const colors = ['#ff4d6d', '#ffd166', '#98f5e1', '#ffccd5', '#ff758f', '#ffffff'];
    for (let i = 0; i < 14; i++) {
        const angle = (Math.PI * 2 / 14) * i + Math.random() * 0.3;
        const speed = 1 + Math.random() * 2;
        burstParticles.push({
            x: cx,
            y: cy,
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            life: 30 + Math.random() * 20,
            maxLife: 50,
            color: colors[Math.floor(Math.random() * colors.length)],
            size: 2 + Math.random() * 2
        });
    }
}

// Fade transition helpers
function startFade(direction, callback) {
    fadeDirection = direction;
    fadeCallback = callback;
    if (direction === 1) fadeAlpha = 0;
    else fadeAlpha = 1;
}

function updateFade() {
    if (fadeDirection === 0) return;
    if (fadeDirection === 1) {
        fadeAlpha += 0.06;
        if (fadeAlpha >= 1) {
            fadeAlpha = 1;
            fadeDirection = 0;
            if (fadeCallback) {
                fadeCallback();
                fadeCallback = null;
                // Auto fade back out
                startFade(-1, null);
            }
        }
    } else if (fadeDirection === -1) {
        fadeAlpha -= 0.06;
        if (fadeAlpha <= 0) {
            fadeAlpha = 0;
            fadeDirection = 0;
        }
    }
}

function drawFade() {
    if (fadeAlpha <= 0) return;
    ctx.fillStyle = `rgba(0, 0, 0, ${fadeAlpha})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

// BFS Pathfinding Engine
function findPathTo(tx, ty) {
    if (isCollidable(tx, ty)) {
        const adj = [
            { x: tx, y: ty - 1 },
            { x: tx, y: ty + 1 },
            { x: tx - 1, y: ty },
            { x: tx + 1, y: ty }
        ];
        const validAdj = adj.filter(node => 
            node.x >= 0 && node.x < MAP_WIDTH && 
            node.y >= 0 && node.y < MAP_HEIGHT && 
            !isCollidable(node.x, node.y)
        );
        if (validAdj.length > 0) {
            let bestNode = validAdj[0];
            let minDist = Math.abs(player.x - bestNode.x) + Math.abs(player.y - bestNode.y);
            validAdj.forEach(node => {
                const dist = Math.abs(player.x - node.x) + Math.abs(player.y - node.y);
                if (dist < minDist) {
                    minDist = dist;
                    bestNode = node;
                }
            });
            tx = bestNode.x;
            ty = bestNode.y;
        } else {
            return;
        }
    }

    const queue = [[{ x: player.x, y: player.y }]];
    const visited = new Set();
    visited.add(`${player.x},${player.y}`);

    while (queue.length > 0) {
        const currentPath = queue.shift();
        const currentLoc = currentPath[currentPath.length - 1];

        if (currentLoc.x === tx && currentLoc.y === ty) {
            player.path = currentPath.slice(1);
            return;
        }

        const neighbors = [
            { x: currentLoc.x, y: currentLoc.y - 1 },
            { x: currentLoc.x, y: currentLoc.y + 1 },
            { x: currentLoc.x - 1, y: currentLoc.y },
            { x: currentLoc.x + 1, y: currentLoc.y }
        ];

        for (const neighbor of neighbors) {
            if (neighbor.x >= 0 && neighbor.x < MAP_WIDTH && neighbor.y >= 0 && neighbor.y < MAP_HEIGHT) {
                if (!isCollidable(neighbor.x, neighbor.y) && !visited.has(`${neighbor.x},${neighbor.y}`)) {
                    visited.add(`${neighbor.x},${neighbor.y}`);
                    queue.push([...currentPath, neighbor]);
                }
            }
        }
    }
}

function processAutoWalk() {
    if (player.isMoving || player.path.length === 0) return;
    const nextStep = player.path.shift();
    if (nextStep.y < player.y) player.dir = 'up';
    else if (nextStep.y > player.y) player.dir = 'down';
    else if (nextStep.x < player.x) player.dir = 'left';
    else if (nextStep.x > player.x) player.dir = 'right';
    movePlayer(nextStep.x - player.x, nextStep.y - player.y);
}

function getOppositeDirection(dir) {
    if (dir === 'up') return 'down';
    if (dir === 'down') return 'up';
    if (dir === 'left') return 'right';
    if (dir === 'right') return 'left';
    return 'down';
}

function update() {
    frameCount++;
    if (gameState === 'play') {
        processAutoWalk();
        
        // Continuous keyboard and D-pad walking:
        if (!player.isMoving && player.path.length === 0) {
            let dx = 0;
            let dy = 0;
            
            if (activeKeys.up) { dy = -1; player.dir = 'up'; }
            else if (activeKeys.down) { dy = 1; player.dir = 'down'; }
            else if (activeKeys.left) { dx = -1; player.dir = 'left'; }
            else if (activeKeys.right) { dx = 1; player.dir = 'right'; }
            
            if (dx !== 0 || dy !== 0) {
                movePlayer(dx, dy);
            }
        }
    }

    if (player.isMoving) {
        player.moveAnim += player.speed;
        if (player.moveAnim >= 1) {
            player.x = player.targetX;
            player.y = player.targetY;
            player.screenX = player.x * TILE_SIZE;
            player.screenY = player.y * TILE_SIZE;
            player.isMoving = false;
            player.moveAnim = 0;
        } else {
            const currentX = player.x * TILE_SIZE;
            const currentY = player.y * TILE_SIZE;
            const targetX = player.targetX * TILE_SIZE;
            const targetY = player.targetY * TILE_SIZE;
            player.screenX = currentX + (targetX - currentX) * player.moveAnim;
            player.screenY = currentY + (targetY - currentY) * player.moveAnim;
        }
    }

    if (gameState === 'finale') {
        heartParticles.forEach(p => {
            p.y += p.vy;
            p.sway += p.swaySpeed;
            p.x += Math.sin(p.sway) * 0.4;
            if (p.y < -10) {
                p.y = canvas.height + 10;
                p.x = Math.random() * canvas.width;
            }
        });
    }

    // Update burst particles
    burstParticles = burstParticles.filter(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.05; // gravity
        p.vx *= 0.98; // friction
        p.life--;
        return p.life > 0;
    });

    // Update fade transitions
    updateFade();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (gameState === 'title') {
        drawTitleScreen();
        drawFade();
        return;
    }

    // 1. Draw Map Tiles and Shading
    drawMap();

    // 2. Draw sparkles on active memory objects
    drawSparkles();

    // 3. Draw Characters with 3-frame animation
    drawCharacter(partner, false);
    drawCharacter(player, true);

    // 4. Draw burst particles
    drawBurstParticles();

    // 5. Draw interaction prompt
    drawInteractionPrompt();

    // 6. Draw HUD (memory counter)
    drawHUD();

    // 7. Draw Particles (Hearts in finale)
    if (gameState === 'finale') {
        drawHeartParticles();
    }

    // 8. Draw fade overlay (always last)
    drawFade();
}

function drawTitleScreen() {
    if (titleImgLoaded) {
        ctx.drawImage(titleImg, 0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'rgba(15, 5, 20, 0.45)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#d4a373';
        ctx.lineWidth = 4;
        ctx.strokeRect(6, 6, canvas.width - 12, canvas.height - 12);
        
        ctx.fillStyle = '#ff4d6d';
        ctx.textAlign = 'center';
        ctx.font = '8px "Press Start 2P"';
        ctx.fillText('SOFIA\'S ROMANTIC', canvas.width / 2, 40);
        
        ctx.font = '10px "Press Start 2P"';
        ctx.fillStyle = '#ffccd5';
        ctx.fillText('ADVENTURE', canvas.width / 2, 60);
    } else {
        ctx.fillStyle = '#1f1224';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#d4a373';
        ctx.lineWidth = 4;
        ctx.strokeRect(6, 6, canvas.width - 12, canvas.height - 12);

        ctx.fillStyle = '#ff4d6d';
        ctx.textAlign = 'center';
        ctx.font = '8px "Press Start 2P"';
        ctx.fillText('SOFIA\'S ROMANTIC', canvas.width / 2, 40);
        
        ctx.font = '10px "Press Start 2P"';
        ctx.fillStyle = '#ffccd5';
        ctx.fillText('ADVENTURE', canvas.width / 2, 60);

        const heartScale = 3 + Math.sin(frameCount * 0.08) * 0.3;
        ctx.fillStyle = '#ff4d6d';
        drawPixelHeart(ctx, canvas.width / 2, canvas.height / 2, heartScale);
    }

    if (Math.floor(frameCount / 30) % 2 === 0) {
        ctx.fillStyle = '#fff';
        ctx.font = '6px "Press Start 2P"';
        ctx.fillText('PREMI START / PULSANTE A', canvas.width / 2, 200);
    }

    ctx.fillStyle = '#d4a373';
    ctx.font = '5px "Press Start 2P"';
    ctx.fillText('© 2026 SPECIAL EDITION', canvas.width / 2, 235);
}

// Room Rendering Engine - Draws floors, walls, shadows, animated fireplace & objects
function drawMap() {
    for (let r = 0; r < MAP_HEIGHT; r++) {
        for (let c = 0; c < MAP_WIDTH; c++) {
            const tile = map[r][c];
            const px = c * TILE_SIZE;
            const py = r * TILE_SIZE;

            // Base floor drawing - Wood plank texture
            const plankTone = (r + c) % 3; // Alternate plank colors
            if (plankTone === 0) ctx.fillStyle = '#eed6c4';
            else if (plankTone === 1) ctx.fillStyle = '#e8ccb5';
            else ctx.fillStyle = '#f0dac8';
            ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
            
            // Plank lines (horizontal grain)
            ctx.fillStyle = 'rgba(139, 94, 60, 0.08)';
            ctx.fillRect(px, py + 4, TILE_SIZE, 1);
            ctx.fillRect(px, py + 10, TILE_SIZE, 1);
            
            // Subtle plank border
            ctx.strokeStyle = 'rgba(180, 150, 120, 0.3)';
            ctx.lineWidth = 0.5;
            ctx.strokeRect(px, py, TILE_SIZE, TILE_SIZE);
            
            // Tiny wood knot on some tiles (deterministic based on position)
            if ((c * 7 + r * 13) % 11 === 0) {
                ctx.fillStyle = 'rgba(139, 94, 60, 0.15)';
                ctx.fillRect(px + 6, py + 7, 3, 2);
            }

            // Floor drop shadow for upper walls
            if (r === 1 && ![6, 17, 18].includes(tile)) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
                ctx.fillRect(px, py, TILE_SIZE, 5);
            }

            // Wall Wood Paneling
            if (tile === 1) {
                ctx.fillStyle = '#8b5e3c';
                ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
                ctx.fillStyle = '#a06e4a';
                ctx.fillRect(px, py, TILE_SIZE, 3);
            } 
            // Windows
            else if (tile === 6) {
                ctx.fillStyle = '#8b5e3c';
                ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
                ctx.fillStyle = '#98f5e1'; // Glass
                ctx.fillRect(px + 3, py + 3, TILE_SIZE - 6, TILE_SIZE - 6);
                ctx.fillStyle = '#ffccd5'; // Curtains
                ctx.fillRect(px + 3, py + 3, 3, TILE_SIZE - 6);
                ctx.fillRect(px + TILE_SIZE - 6, py + 3, 3, TILE_SIZE - 6);
            }
            // Bed top (default)
            else if (tile === 2) {
                drawBedTop(px, py, false);
            }
            // Bed top (triggered/pillow tilted)
            else if (tile === 14) {
                drawBedTop(px, py, true);
            }
            // Bed bottom (default)
            else if (tile === 10) {
                drawBedBottom(px, py, false);
            }
            // Bed bottom (triggered/ duvet ruffled)
            else if (tile === 15) {
                drawBedBottom(px, py, true);
            }
            // TV (default / black screen)
            else if (tile === 3) {
                drawTV(px, py, false);
            }
            // TV (triggered / neon heart)
            else if (tile === 13) {
                drawTV(px, py, true);
            }
            else if (tile === 11) {
                // TV stand table side extension with shadow
                ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
                ctx.fillRect(px + 1, py + 5, TILE_SIZE, TILE_SIZE - 4);
                ctx.fillStyle = '#a06e4a';
                ctx.fillRect(px, py + 4, TILE_SIZE, TILE_SIZE - 4);
            }
            // Dresser (default)
            else if (tile === 4) {
                drawDresser(px, py, false);
            }
            // Dresser (triggered / open drawer with gold glow)
            else if (tile === 12) {
                drawDresser(px, py, true);
            }
            // Cozy Plant (default)
            else if (tile === 5) {
                drawPlant(px, py, false);
            }
            // Cozy Plant (triggered / flowered)
            else if (tile === 16) {
                drawPlant(px, py, true);
            }
            // Heart Rug (Center carpet) with embroidered border and heart pattern
            else if (tile === 9) {
                ctx.fillStyle = '#ffccd5';
                ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
                
                // Embroidered border pattern
                ctx.fillStyle = '#ffb3c1';
                ctx.fillRect(px + 2, py + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                
                // Decorative corner dots
                ctx.fillStyle = '#ff758f';
                ctx.fillRect(px + 1, py + 1, 2, 2);
                ctx.fillRect(px + TILE_SIZE - 3, py + 1, 2, 2);
                ctx.fillRect(px + 1, py + TILE_SIZE - 3, 2, 2);
                ctx.fillRect(px + TILE_SIZE - 3, py + TILE_SIZE - 3, 2, 2);
                
                // Small heart in center of rug tiles that are in the middle
                if (c >= 6 && c <= 8 && r >= 7 && r <= 8) {
                    ctx.fillStyle = '#ff4d6d';
                    ctx.fillRect(px + 5, py + 5, 2, 2);
                    ctx.fillRect(px + 9, py + 5, 2, 2);
                    ctx.fillRect(px + 4, py + 7, 8, 2);
                    ctx.fillRect(px + 5, py + 9, 6, 1);
                    ctx.fillRect(px + 6, py + 10, 4, 1);
                    ctx.fillRect(px + 7, py + 11, 2, 1);
                }
            }
            // Door mat
            else if (tile === 7) {
                ctx.fillStyle = '#d4a373';
                ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
                ctx.fillStyle = '#8b5e3c';
                ctx.fillRect(px + 2, py + 2, TILE_SIZE - 4, TILE_SIZE - 4);
            }
            // Fireplace top
            else if (tile === 17) {
                ctx.fillStyle = '#8b5e3c'; // Wall paneling
                ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
                // Chimney brick texture
                ctx.fillStyle = '#9b2226';
                ctx.fillRect(px + 1, py, TILE_SIZE - 2, TILE_SIZE);
                ctx.fillStyle = '#b7094c';
                ctx.fillRect(px + 3, py + 4, 4, 3);
                ctx.fillRect(px + 9, py + 8, 4, 3);
            }
            // Fireplace bottom (animated dancing flame)
            else if (tile === 18) {
                ctx.fillStyle = '#8b5e3c';
                ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
                
                // Fireplace hearth brick frame
                ctx.fillStyle = '#9b2226';
                ctx.fillRect(px + 1, py, TILE_SIZE - 2, TILE_SIZE);
                
                // Shadow underneath
                ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                ctx.fillRect(px + 1, py + TILE_SIZE - 2, TILE_SIZE - 2, 2);

                // Fire hearth opening (black cave)
                ctx.fillStyle = '#220901';
                ctx.fillRect(px + 3, py + 4, TILE_SIZE - 6, TILE_SIZE - 4);

                // Animated flames
                const fireFrame = Math.floor(frameCount / 10) % 3;
                if (fireFrame === 0) {
                    ctx.fillStyle = '#ae2012'; // Dark red
                    ctx.fillRect(px + 5, py + 7, 6, 6);
                    ctx.fillStyle = '#ca6702'; // Orange
                    ctx.fillRect(px + 6, py + 8, 4, 4);
                    ctx.fillStyle = '#e9d8a6'; // Yellow
                    ctx.fillRect(px + 7, py + 9, 2, 2);
                } else if (fireFrame === 1) {
                    ctx.fillStyle = '#ae2012';
                    ctx.fillRect(px + 4, py + 6, 8, 7);
                    ctx.fillStyle = '#ca6702';
                    ctx.fillRect(px + 5, py + 7, 6, 5);
                    ctx.fillStyle = '#e9d8a6';
                    ctx.fillRect(px + 7, py + 8, 2, 3);
                } else {
                    ctx.fillStyle = '#ae2012';
                    ctx.fillRect(px + 5, py + 7, 6, 6);
                    ctx.fillStyle = '#ca6702';
                    ctx.fillRect(px + 6, py + 6, 4, 5);
                    ctx.fillStyle = '#e9d8a6';
                    ctx.fillRect(px + 6, py + 8, 2, 2);
                }
            }
        }
    }
    
    // === Ambient Lighting Effects (drawn AFTER tiles) ===
    
    // Fireplace warm glow
    const fireCx = 10.5 * TILE_SIZE;
    const fireCy = 1.5 * TILE_SIZE;
    const fireGrad = ctx.createRadialGradient(fireCx, fireCy, 8, fireCx, fireCy, 80);
    fireGrad.addColorStop(0, 'rgba(255, 140, 40, 0.08)');
    fireGrad.addColorStop(0.5, 'rgba(255, 100, 30, 0.04)');
    fireGrad.addColorStop(1, 'rgba(255, 80, 20, 0)');
    ctx.fillStyle = fireGrad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Window light rays (subtle light cones from windows)
    for (let r = 0; r < MAP_HEIGHT; r++) {
        for (let c = 0; c < MAP_WIDTH; c++) {
            if (map[r][c] === 6) {
                const wx = c * TILE_SIZE + TILE_SIZE / 2;
                const wy = (r + 1) * TILE_SIZE;
                ctx.fillStyle = 'rgba(255, 248, 220, 0.035)';
                ctx.beginPath();
                ctx.moveTo(wx - 4, wy);
                ctx.lineTo(wx + TILE_SIZE + 4, wy);
                ctx.lineTo(wx + TILE_SIZE + 12, wy + TILE_SIZE * 3);
                ctx.lineTo(wx - 12, wy + TILE_SIZE * 3);
                ctx.closePath();
                ctx.fill();
            }
        }
    }
}

// Helpers for advanced tile rendering with shading and shadows
function drawBedTop(px, py, isTriggered) {
    // Bed drop shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.12)';
    ctx.fillRect(px + 2, py + 2, TILE_SIZE - 2, TILE_SIZE - 2);

    // Bed frame
    ctx.fillStyle = '#a06e4a';
    ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
    
    // Pillow (white)
    ctx.fillStyle = '#ffffff';
    if (isTriggered) {
        // Pillow indented/tilted
        ctx.fillRect(px + 3, py + 5, TILE_SIZE - 6, TILE_SIZE - 7);
        ctx.fillStyle = '#e5e5e5';
        ctx.fillRect(px + 6, py + 6, 4, 2); // Indentation line
    } else {
        ctx.fillRect(px + 2, py + 4, TILE_SIZE - 4, TILE_SIZE - 6);
    }
}

function drawBedBottom(px, py, isTriggered) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.12)';
    ctx.fillRect(px + 2, py, TILE_SIZE - 2, TILE_SIZE);

    ctx.fillStyle = '#a06e4a';
    ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
    
    // Pink duvet blanket
    ctx.fillStyle = '#ff4d6d';
    ctx.fillRect(px + 1, py, TILE_SIZE - 2, TILE_SIZE - 2);
    
    if (isTriggered) {
        // Messed up blanket sheets lines
        ctx.fillStyle = '#c9184a';
        ctx.fillRect(px + 2, py + 3, 6, 1);
        ctx.fillRect(px + 7, py + 6, 6, 1);
        ctx.fillRect(px + 4, py + 9, 8, 1);
    } else {
        // Neat border highlight
        ctx.fillStyle = '#ff758f';
        ctx.fillRect(px + 1, py, TILE_SIZE - 2, 2);
    }
}

function drawTV(px, py, isTriggered) {
    // Shadow under tv stand
    ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.fillRect(px + 2, py + 2, TILE_SIZE - 2, TILE_SIZE - 2);

    // TV bezel casing
    ctx.fillStyle = '#333533';
    ctx.fillRect(px + 2, py + 1, TILE_SIZE - 4, TILE_SIZE - 4);
    
    // Screen area
    if (isTriggered) {
        // Glowing cyan green screen
        ctx.fillStyle = '#98f5e1';
        ctx.fillRect(px + 4, py + 3, TILE_SIZE - 8, TILE_SIZE - 8);
        
        // Small beating heart inside screen
        const heartState = Math.floor(frameCount / 20) % 2;
        ctx.fillStyle = '#ff3366';
        if (heartState === 0) {
            // Heart shape 3x2 pixels
            ctx.fillRect(px + 7, py + 5, 2, 1);
            ctx.fillRect(px + 6, py + 6, 4, 1);
            ctx.fillRect(px + 7, py + 7, 2, 1);
        } else {
            // Heart shape slightly larger
            ctx.fillRect(px + 6, py + 4, 4, 1);
            ctx.fillRect(px + 5, py + 5, 6, 2);
            ctx.fillRect(px + 7, py + 7, 2, 1);
        }
    } else {
        // Black screen
        ctx.fillStyle = '#101115';
        ctx.fillRect(px + 4, py + 3, TILE_SIZE - 8, TILE_SIZE - 8);
    }

    // Wooden stand table
    ctx.fillStyle = '#a06e4a';
    ctx.fillRect(px, py + TILE_SIZE - 3, TILE_SIZE, 3);
}

function drawDresser(px, py, isTriggered) {
    // Shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.fillRect(px + 2, py + 2, TILE_SIZE - 2, TILE_SIZE - 2);

    // Dresser wood chest
    ctx.fillStyle = '#b76935';
    ctx.fillRect(px, py, TILE_SIZE, TILE_SIZE);
    
    if (isTriggered) {
        // Top drawer pulled open with gold glow
        ctx.fillStyle = '#8b5e3c'; // Dark open space
        ctx.fillRect(px + 2, py + 2, TILE_SIZE - 4, 5);
        ctx.fillStyle = '#ffd166'; // Gold glow inside drawer
        ctx.fillRect(px + 3, py + 3, TILE_SIZE - 6, 3);
        
        // Opened drawer front panel protruding out
        ctx.fillStyle = '#b76935';
        ctx.fillRect(px + 1, py + 5, TILE_SIZE - 2, 4);
        ctx.fillStyle = '#d4a373'; // Drawer handle
        ctx.fillRect(px + 4, py + 6, TILE_SIZE - 8, 1);

        // Bottom drawer closed
        ctx.fillStyle = '#d4a373';
        ctx.fillRect(px + 3, py + 11, TILE_SIZE - 6, 2);
    } else {
        // Drawers closed
        ctx.fillStyle = '#d4a373';
        ctx.fillRect(px + 3, py + 4, TILE_SIZE - 6, 2);
        ctx.fillRect(px + 3, py + 10, TILE_SIZE - 6, 2);
    }
}

function drawPlant(px, py, isTriggered) {
    // Drop shadow
    ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
    ctx.fillRect(px + 4, py + 8, 8, 8);

    // Terracotta Pot
    ctx.fillStyle = '#b76935';
    ctx.fillRect(px + 4, py + 8, 8, 8);
    
    // Green leaves
    ctx.fillStyle = '#52b788';
    ctx.fillRect(px + 2, py + 2, 12, 6);
    ctx.fillRect(px + 5, py, 6, 3);
    
    if (isTriggered) {
        // Draw blooming flower in the center (red rose)
        ctx.fillStyle = '#ff3366';
        ctx.fillRect(px + 6, py + 1, 4, 3);
        ctx.fillStyle = '#ff8fa3';
        ctx.fillRect(px + 7, py + 2, 2, 1);
    }
}

function drawSparkles() {
    sparkles.forEach(s => {
        if (!s.active) return;
        
        const px = s.x * TILE_SIZE + TILE_SIZE / 2;
        const py = s.y * TILE_SIZE + TILE_SIZE / 2;
        const pulse = Math.sin(frameCount * 0.15) * 0.5 + 0.5; // 0 to 1 pulsing
        const rot = frameCount * 0.04; // rotation
        
        // Main star center - bright white
        ctx.fillStyle = `rgba(255, 255, 255, ${0.6 + pulse * 0.4})`;
        ctx.fillRect(px - 1, py - 1, 2, 2);
        
        // Cross arms (4 cardinal directions), size pulses
        const armLen = 2 + Math.floor(pulse * 2);
        ctx.fillStyle = `rgba(247, 176, 91, ${0.5 + pulse * 0.3})`;
        ctx.fillRect(px - armLen, py, armLen, 1); // left
        ctx.fillRect(px + 1, py, armLen, 1);       // right
        ctx.fillRect(px, py - armLen, 1, armLen);   // up
        ctx.fillRect(px, py + 1, 1, armLen);        // down
        
        // Diagonal smaller arms
        const diagLen = 1 + Math.floor(pulse);
        ctx.fillStyle = `rgba(255, 204, 213, ${0.3 + pulse * 0.3})`;
        ctx.fillRect(px - diagLen, py - diagLen, 1, 1);
        ctx.fillRect(px + diagLen, py - diagLen, 1, 1);
        ctx.fillRect(px - diagLen, py + diagLen, 1, 1);
        ctx.fillRect(px + diagLen, py + diagLen, 1, 1);
        
        // Orbiting secondary sparkle
        const orbitR = 5;
        const ox = px + Math.cos(rot) * orbitR;
        const oy = py + Math.sin(rot) * orbitR;
        ctx.fillStyle = `rgba(255, 255, 255, ${0.3 + pulse * 0.3})`;
        ctx.fillRect(Math.floor(ox), Math.floor(oy), 1, 1);
    });
}

// Draw pixel characters with a complete 3-frame walking animation loop
function drawCharacter(char, isPlayer) {
    let px, py;
    
    if (isPlayer && player.isMoving) {
        px = player.screenX;
        py = player.screenY;
    } else {
        px = char.x * TILE_SIZE;
        py = char.y * TILE_SIZE;
    }

    py -= 6; // Offset up for 24px height sprite on 16px tile
    
    // Shadow under character feet
    ctx.fillStyle = 'rgba(0, 0, 0, 0.18)';
    ctx.fillRect(px + 2, py + 18, 12, 4);

    let hairColor, clothingColor, trouserColor, skinColor;
    skinColor = '#ffd3b6';

    if (isPlayer) {
        // Sofia: Brunette, Green Dress
        hairColor = '#4a2c11';
        clothingColor = '#3a8630';
        trouserColor = '#3a8630';
    } else {
        // Partner: Brown hair, Azure shirt
        hairColor = '#7f5539';
        clothingColor = '#2a9d8f';
        trouserColor = '#264653';
    }

    // --- Determine walking frame (3 frames: 0: standing, 1: left step, 2: right step) ---
    let animFrame = 0;
    if (isPlayer && player.isMoving) {
        // Divide movement animation (0 to 1) into 4 sections
        const stage = Math.floor(player.moveAnim * 4); // 0, 1, 2, 3
        if (stage === 0) animFrame = 1;      // Left foot
        else if (stage === 1) animFrame = 0; // Standing
        else if (stage === 2) animFrame = 2; // Right foot
        else animFrame = 0;                  // Standing
    }

    // Walking body vertical bounce
    let bounce = 0;
    if (isPlayer && player.isMoving && animFrame !== 0) {
        bounce = 1;
    }
    
    // Idle breathing animation (subtle 1px oscillation when standing)
    let breathOffset = 0;
    if (animFrame === 0) {
        breathOffset = Math.floor(Math.sin(frameCount * 0.05) * 0.6 + 0.5); // 0 or 1
    }
    
    // Eye blinking (every ~3 seconds, blink for 6 frames)
    const isBlinking = (frameCount % 180) < 6;

    // 1. Head & Hair
    ctx.fillStyle = hairColor;
    ctx.fillRect(px + 4, py + 1 - bounce, 8, 8);
    ctx.fillRect(px + 3, py + 2 - bounce, 10, 5);

    ctx.fillStyle = skinColor;
    ctx.fillRect(px + 4, py + 4 - bounce, 8, 5);
    
    ctx.fillStyle = hairColor;
    ctx.fillRect(px + 4, py + 3 - bounce, 8, 1);
    ctx.fillRect(px + 3, py + 4 - bounce, 2, 2);
    ctx.fillRect(px + 11, py + 4 - bounce, 2, 2);

    // Eyes direction (with blinking support)
    ctx.fillStyle = '#000000';
    if (isBlinking) {
        // Closed eyes: horizontal line
        ctx.fillRect(px + 5, py + 7 - bounce, 2, 1);
        ctx.fillRect(px + 9, py + 7 - bounce, 2, 1);
    } else if (char.dir === 'down') {
        ctx.fillRect(px + 5, py + 6 - bounce, 1, 2);
        ctx.fillRect(px + 10, py + 6 - bounce, 1, 2);
        // Blushing cheeks
        ctx.fillStyle = 'rgba(255, 77, 109, 0.4)';
        ctx.fillRect(px + 4, py + 7 - bounce, 1, 1);
        ctx.fillRect(px + 11, py + 7 - bounce, 1, 1);
    } 
    else if (char.dir === 'left') {
        ctx.fillRect(px + 4, py + 6 - bounce, 1, 2);
        ctx.fillRect(px + 7, py + 6 - bounce, 1, 2);
    } 
    else if (char.dir === 'right') {
        ctx.fillRect(px + 8, py + 6 - bounce, 1, 2);
        ctx.fillRect(px + 11, py + 6 - bounce, 1, 2);
    }
    else if (char.dir === 'up') {
        // Eyes not visible from behind, draw back of head
        ctx.fillStyle = hairColor;
        ctx.fillRect(px + 5, py + 6 - bounce, 6, 2);
    }

    // 2. Body / Shirt / Dress (with breathing offset)
    ctx.fillStyle = clothingColor;
    ctx.fillRect(px + 4, py + 9 - bounce + breathOffset, 8, 7);

    // Arms drawing based on walking animation frames (swinging)
    ctx.fillStyle = clothingColor;
    if (animFrame === 0) {
        // Idle: flat arms
        ctx.fillRect(px + 3, py + 10 - bounce, 1, 4);
        ctx.fillRect(px + 12, py + 10 - bounce, 1, 4);
    } else if (animFrame === 1) {
        // Left foot active: swing left arm up, right arm down
        ctx.fillRect(px + 3, py + 9 - bounce, 1, 4);
        ctx.fillRect(px + 12, py + 11 - bounce, 1, 4);
    } else {
        // Right foot active: swing right arm up, left arm down
        ctx.fillRect(px + 3, py + 11 - bounce, 1, 4);
        ctx.fillRect(px + 12, py + 9 - bounce, 1, 4);
    }

    // 3. Legs / Feet drawing (animates foot lifts)
    ctx.fillStyle = trouserColor;
    if (animFrame === 0) {
        // Both legs down
        ctx.fillRect(px + 5, py + 16, 2, 3);
        ctx.fillRect(px + 9, py + 16, 2, 3);
    } else if (animFrame === 1) {
        // Left foot lifted (1px shorter), right foot flat
        ctx.fillRect(px + 5, py + 16, 2, 2);
        ctx.fillRect(px + 9, py + 16, 2, 3);
    } else {
        // Right foot lifted (1px shorter), left foot flat
        ctx.fillRect(px + 5, py + 16, 2, 3);
        ctx.fillRect(px + 9, py + 16, 2, 2);
    }
}

function drawHeartParticles() {
    heartParticles.forEach(p => {
        ctx.fillStyle = p.color;
        drawPixelHeart(ctx, p.x, p.y, p.size / 6);
    });
}

// Draw burst particles from memory discoveries
function drawBurstParticles() {
    burstParticles.forEach(p => {
        const alpha = p.life / p.maxLife;
        ctx.globalAlpha = alpha;
        ctx.fillStyle = p.color;
        ctx.fillRect(Math.floor(p.x), Math.floor(p.y), Math.ceil(p.size), Math.ceil(p.size));
    });
    ctx.globalAlpha = 1;
}

// Draw interaction prompt when facing an interactive object
function drawInteractionPrompt() {
    if (gameState !== 'play' || player.isMoving) return;
    
    let checkX = player.x;
    let checkY = player.y;
    if (player.dir === 'up') checkY--;
    else if (player.dir === 'down') checkY++;
    else if (player.dir === 'left') checkX--;
    else if (player.dir === 'right') checkX++;
    
    if (checkX < 0 || checkX >= MAP_WIDTH || checkY < 0 || checkY >= MAP_HEIGHT) return;
    
    const tile = map[checkY]?.[checkX];
    const interactiveTiles = [2, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16];
    const isPartner = checkX === partner.x && checkY === partner.y;
    
    if (interactiveTiles.includes(tile) || isPartner) {
        const promptX = checkX * TILE_SIZE + TILE_SIZE / 2;
        const promptY = checkY * TILE_SIZE - 4 + Math.sin(frameCount * 0.1) * 2;
        
        // Dark rounded background
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(promptX - 6, promptY - 5, 12, 10);
        
        // White A text
        ctx.fillStyle = '#ffffff';
        ctx.font = '6px "Press Start 2P"';
        ctx.textAlign = 'center';
        ctx.fillText('A', promptX, promptY + 3);
    }
}

// Draw in-game HUD with memory counter
function drawHUD() {
    if (gameState !== 'play' && gameState !== 'finale') return;
    
    // Semi-transparent background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
    ctx.fillRect(2, 2, 36, 10);
    
    // Draw 4 small hearts
    const memoryOrder = ['bed', 'tv', 'dresser', 'plant'];
    for (let i = 0; i < 4; i++) {
        const hx = 5 + i * 8;
        const hy = 5;
        
        if (memories[memoryOrder[i]].triggered) {
            // Filled heart
            ctx.fillStyle = '#ff4d6d';
            ctx.fillRect(hx, hy - 1, 2, 1);
            ctx.fillRect(hx + 3, hy - 1, 2, 1);
            ctx.fillRect(hx - 1, hy, 7, 2);
            ctx.fillRect(hx, hy + 2, 5, 1);
            ctx.fillRect(hx + 1, hy + 3, 3, 1);
            ctx.fillRect(hx + 2, hy + 4, 1, 1);
        } else {
            // Outline heart
            ctx.fillStyle = 'rgba(255, 77, 109, 0.3)';
            ctx.fillRect(hx, hy - 1, 2, 1);
            ctx.fillRect(hx + 3, hy - 1, 2, 1);
            ctx.fillRect(hx - 1, hy, 1, 1);
            ctx.fillRect(hx + 5, hy, 1, 1);
            ctx.fillRect(hx - 1, hy + 1, 1, 1);
            ctx.fillRect(hx + 5, hy + 1, 1, 1);
            ctx.fillRect(hx, hy + 2, 1, 1);
            ctx.fillRect(hx + 4, hy + 2, 1, 1);
            ctx.fillRect(hx + 1, hy + 3, 1, 1);
            ctx.fillRect(hx + 3, hy + 3, 1, 1);
            ctx.fillRect(hx + 2, hy + 4, 1, 1);
        }
    }
}

function gameLoop(time = 0) {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

init();
