const canvas = document.createElement('canvas');
canvas.id = 'star-canvas';
document.body.appendChild(canvas);

const ctx = canvas.getContext('2d');
let width, height;
let stars = [];
const numStars = 800;
const speed = 0.1;

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
}

class Star {
    constructor() {
        this.x = Math.random() * width - width / 2;
        this.y = Math.random() * height - height / 2;
        this.z = Math.random() * width;
    }

    update() {
        this.z -= speed * 20; // Move closer
        if (this.z <= 0) {
            this.z = width;
            this.x = Math.random() * width - width / 2;
            this.y = Math.random() * height - height / 2;
        }
    }

    draw() {
        let x = (this.x / this.z) * width + width / 2;
        let y = (this.y / this.z) * height + height / 2;
        let radius = (1 - this.z / width) * 2;

        if (x < 0 || x > width || y < 0 || y > height) return;

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
    }
}

function init() {
    resize();
    for (let i = 0; i < numStars; i++) {
        stars.push(new Star());
    }
    animate();
}

function animate() {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, width, height);

    stars.forEach(star => {
        star.update();
        star.draw();
    });

    requestAnimationFrame(animate);
}

window.addEventListener('resize', resize);
init();
