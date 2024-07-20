import { MQTTClient } from './mqttClient.js';
import { SmartHomeCore } from './smartHomeCore.js';
import { LightControl } from './components/lightControl.js';

document.addEventListener('DOMContentLoaded', () => {
    const mqttClient = new MQTTClient();
    const smartHomeCore = new SmartHomeCore(mqttClient);
    
    const lightControlsContainer = document.getElementById('light-controls');

    // Define lights and their positions
    const lights = [
        { id: 'light1', position: '1 / 1' },
        { id: 'light2', position: '1 / 2' },
        { id: 'light3', position: '2 / 1' },
        { id: 'light4', position: '2 / 2' }
    ];

    lights.forEach(light => {
        const lightControl = new LightControl(light.id, smartHomeCore, light.position);
        lightControlsContainer.appendChild(lightControl.render());
    });
});
