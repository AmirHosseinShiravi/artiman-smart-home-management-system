export class LightControl {
    constructor(lightId, smartHomeCore, position) {
        this.lightId = lightId;
        this.smartHomeCore = smartHomeCore;
        this.position = position;
        this.state = this.smartHomeCore.getLightStatus(lightId); // Initial state
        
        this.render();
        this.setupEventListeners();
    }

    render() {
        this.button = document.createElement('button');
        this.updateButton();
        this.button.onclick = () => this.toggleLight();
        this.button.style.gridArea = this.position; // Position the button using CSS Grid
        return this.button;
    }

    setupEventListeners() {
        document.addEventListener(`lightStatusUpdate-${this.lightId}`, (event) => {
            this.state = event.detail.state;
            this.updateButton();
        });
    }

    toggleLight() {
        this.state = !this.state;
        this.smartHomeCore.toggleLight(this.lightId, this.state);
        this.updateButton();
    }

    updateButton() {
        this.button.className = `button ${this.state ? 'light-on' : 'light-off'}`;
        this.button.innerText = this.state ? `Turn off ${this.lightId}` : `Turn on ${this.lightId}`;
    }
}
