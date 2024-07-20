export class SmartHomeCore {
    constructor(mqttClient) {
        this.mqttClient = mqttClient;
        this.lightStatus = {}; // Maintain the status of each light
        this.init();
    }

    init() {
        // Subscribe to necessary topics
        this.mqttClient.subscribe('home/lights/#');
        this.mqttClient.registerMessageHandler('home/lights/#', this.handleLightMessage.bind(this));
    }

    handleLightMessage(message) {
        const [topic, lightId] = message.destinationName.split('/').slice(-2);
        const state = message.payloadString === 'ON';
        this.lightStatus[lightId] = state;

        // Notify the relevant component
        document.dispatchEvent(new CustomEvent(`lightStatusUpdate-${lightId}`, { detail: { state } }));
    }

    toggleLight(lightId, state) {
        const topic = `home/lights/${lightId}`;
        this.mqttClient.publish(topic, state ? 'ON' : 'OFF');
    }

    getLightStatus(lightId) {
        return this.lightStatus[lightId] || false;
    }
}
