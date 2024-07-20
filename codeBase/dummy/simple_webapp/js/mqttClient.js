export class MQTTClient {
    constructor() {
        this.client = this.connect();
        this.messageHandlers = {};
    }

    connect() {
        // Connect to MQTT broker
        const client = new Paho.MQTT.Client('broker.hivemq.com', 8000, 'clientId');
        client.onMessageArrived = this.onMessageArrived.bind(this);
        client.connect({ onSuccess: this.onConnect.bind(this) });
        return client;
    }

    onConnect() {
        console.log('Connected to MQTT broker');
    }

    subscribe(topic) {
        this.client.subscribe(topic);
    }

    publish(topic, message) {
        const mqttMessage = new Paho.MQTT.Message(message);
        mqttMessage.destinationName = topic;
        this.client.send(mqttMessage);
    }

    onMessageArrived(message) {
        const topic = message.destinationName;
        const payload = message.payloadString;

        if (this.messageHandlers[topic]) {
            this.messageHandlers[topic](payload);
        }
    }

    registerMessageHandler(topic, handler) {
        this.messageHandlers[topic] = handler;
    }
}



// answer two

// export class MQTTClient {
//     constructor() {
//         // Replace with your MQTT broker information
//         this.client = new Paho.MQTT.Client('broker.example.com', 8883, 'clientId');
//         this.client.onConnectionLost = this.onConnectionLost.bind(this);
//         this.client.onMessageArrived = this.onMessageArrived.bind(this);
//         this.connect();
//     }

//     connect() {
//         const options = {
//             useSSL: true,
//             onSuccess: this.onConnect.bind(this),
//             onFailure: this.onFailure.bind(this)
//         };
//         this.client.connect(options);
//     }

//     onConnect() {
//         console.log('Connected to MQTT broker');
//         // Subscribe to topics or perform other actions upon connection
//     }

//     onFailure(message) {
//         console.error('Failed to connect to MQTT broker:', message.errorMessage);
//     }

//     onConnectionLost(responseObject) {
//         if (responseObject.errorCode !== 0) {
//             console.error('Connection lost:', responseObject.errorMessage);
//             this.connect(); // Attempt to reconnect
//         }
//     }

//     onMessageArrived(message) {
//         console.log('Message arrived:', message.payloadString);
//         // Handle incoming messages from subscribed topics
//     }

//     subscribe(topic) {
//         this.client.subscribe(topic);
//     }

//     unsubscribe(topic) {
//         this.client.unsubscribe(topic);
//     }

//     sendMessage(topic, payload) {
//         const message = new Paho.MQTT.Message(payload);
//         message.destinationName = topic;
//         this.client.send(message);
//     }
// }