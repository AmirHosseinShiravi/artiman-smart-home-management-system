//
// class MQTTClient {
//     constructor(brokerUrl, options = {}) {
//         this.brokerUrl = brokerUrl;
//         this.options = {
//             clientId: `mqttjs_${Math.random().toString(16).substr(2, 8)}`,
//             username: '',
//             password: '',
//             keepalive: 60,
//             clean: false,
//             reconnectPeriod: 1000,
//             connectTimeout: 30 * 1000,
//             path: '/mqtt',
//             ...options
//         };
//         this.client = null;
//         this.eventBus = null;
//         this.isConnected = false;
//         this.reconnectTimer = null;
//         this.publishQueue = [];
//         this.processQueueInterval = null;
//     }
//
//     connect() {
//         this.client = mqtt.connect(this.brokerUrl, this.options);
//
//         this.client.on('connect', () => {
//             console.log('Connected to MQTT broker');
//             this.isConnected = true;
//             clearTimeout(this.reconnectTimer);
//             this.processQueueInterval = setInterval(() => this.processPublishQueue(), 100);
//         });
//
//         this.client.on('error', (error) => {
//             console.error('MQTT connection error:', error);
//         });
//
//         this.client.on('close', () => {
//             console.log('MQTT connection closed');
//             this.isConnected = false;
//             this.scheduleReconnect();
//             if (this.processQueueInterval) {
//                 clearInterval(this.processQueueInterval);
//                 this.processQueueInterval = null;
//             }
//         });
//
//         this.client.on('message', (topic, message) => {
//             if (this.eventBus) {
//                 this.eventBus.publish(topic, message.toString());
//             }
//         });
//     }
//
//     scheduleReconnect() {
//         if (!this.reconnectTimer) {
//             this.reconnectTimer = setTimeout(() => {
//                 console.log('Attempting to reconnect...');
//                 this.connect();
//             }, this.options.reconnectPeriod);
//         }
//     }
//
//     setEventBus(eventBus) {
//         this.eventBus = eventBus;
//     }
//
//     subscribe(topic) {
//         if (!this.isConnected) {
//             console.warn(`Not connected to MQTT broker. Subscription to ${topic} queued.`);
//             this.publishQueue.push({ type: 'subscribe', topic });
//             return;
//         }
//         this.client.subscribe(topic, (err) => {
//             if (err) {
//                 console.error(`Failed to subscribe to ${topic}:`, err);
//             } else {
//                 console.log(`Subscribed to ${topic}`);
//             }
//         });
//     }
//
//     unsubscribe(topic) {
//         if (!this.isConnected) {
//             console.warn(`Not connected to MQTT broker. Unsubscription from ${topic} queued.`);
//             this.publishQueue.push({ type: 'unsubscribe', topic });
//             return;
//         }
//         this.client.unsubscribe(topic, (err) => {
//             if (err) {
//                 console.error(`Failed to unsubscribe from ${topic}:`, err);
//             } else {
//                 console.log(`Unsubscribed from ${topic}`);
//             }
//         });
//     }
//
//     publish(topic, message, options = {}) {
//         if (!this.isConnected) {
//             console.warn('Not connected to MQTT broker. Message queued.');
//             this.publishQueue.push({ type: 'publish', topic, message, options });
//             return;
//         }
//         this.client.publish(topic, message, options, (err) => {
//             if (err) {
//                 console.error('Failed to publish message:', err);
//             }
//         });
//     }
//
//     processPublishQueue() {
//         while (this.publishQueue.length > 0 && this.isConnected) {
//             const item = this.publishQueue.shift();
//             switch (item.type) {
//                 case 'publish':
//                     this.publish(item.topic, item.message, item.options);
//                     break;
//                 case 'subscribe':
//                     this.subscribe(item.topic);
//                     break;
//                 case 'unsubscribe':
//                     this.unsubscribe(item.topic);
//                     break;
//             }
//         }
//     }
//
//     disconnect() {
//         if (this.client) {
//             this.client.end(false, () => {
//                 this.isConnected = false;
//                 clearTimeout(this.reconnectTimer);
//                 this.reconnectTimer = null;
//                 if (this.processQueueInterval) {
//                     clearInterval(this.processQueueInterval);
//                     this.processQueueInterval = null;
//                 }
//                 console.log('Disconnected from MQTT broker');
//             });
//         }
//     }
// }







class MQTTClient {
    constructor(brokerUrl, options = {}) {
        this.brokerUrl = brokerUrl;
        this.options = {
            clientId: `mqttjs_${Math.random().toString(16).substr(2, 8)}`,
            username: '',
            password: '',
            keepalive: 60,
            clean: false, // Changed to true for clean session
            reconnectPeriod: 5000, // Increased reconnect period
            connectTimeout: 30 * 1000,
            path: '/mqtt',
            resubscribe: false, // Prevent automatic resubscriptions
            ...options
        };
        this.client = null;
        this.eventBus = null;
        this.isConnected = false;
        this.reconnectTimer = null;
        this.publishQueue = [];
        this.processQueueInterval = null;
        this.subscriptions = new Set(); // Track subscriptions
    }

    connect() {
        if (this.client) {
            this.client.end(true);
        }

        this.client = mqtt.connect(this.brokerUrl, this.options);

        this.client.on('connect', () => {
            console.log('Connected to MQTT broker');
            this.isConnected = true;
            clearTimeout(this.reconnectTimer);
            this.resubscribe(); // Resubscribe to topics
            this.processQueueInterval = setInterval(() => this.processPublishQueue(), 100);
        });

        this.client.on('error', (error) => {
            console.error('MQTT connection error:', error);
        });

        this.client.on('close', () => {
            console.log('MQTT connection closed');
            this.isConnected = false;
            if (this.processQueueInterval) {
                clearInterval(this.processQueueInterval);
                this.processQueueInterval = null;
            }
        });

        this.client.on('offline', () => {
            console.log('MQTT client is offline');
            this.isConnected = false;
        });

        this.client.on('message', (topic, message) => {
            if (this.eventBus) {
                this.eventBus.publish(topic, message.toString());
            }
        });
    }

    resubscribe() {
        for (const topic of this.subscriptions) {
            this.client.subscribe(topic, (err) => {
                if (err) {
                    console.error(`Failed to resubscribe to ${topic}:`, err);
                } else {
                    console.log(`Resubscribed to ${topic}`);
                }
            });
        }
    }

    setEventBus(eventBus) {
        this.eventBus = eventBus;
    }

    subscribe(topic) {
        if (!this.isConnected) {
            console.warn(`Not connected to MQTT broker. Subscription to ${topic} queued.`);
            this.publishQueue.push({ type: 'subscribe', topic });
            return;
        }
        this.client.subscribe(topic, (err) => {
            if (err) {
                console.error(`Failed to subscribe to ${topic}:`, err);
            } else {
                console.log(`Subscribed to ${topic}`);
                this.subscriptions.add(topic);
            }
        });
    }

    unsubscribe(topic) {
        if (!this.isConnected) {
            console.warn(`Not connected to MQTT broker. Unsubscription from ${topic} queued.`);
            this.publishQueue.push({ type: 'unsubscribe', topic });
            return;
        }
        this.client.unsubscribe(topic, (err) => {
            if (err) {
                console.error(`Failed to unsubscribe from ${topic}:`, err);
            } else {
                console.log(`Unsubscribed from ${topic}`);
                this.subscriptions.delete(topic);
            }
        });
    }

    publish(topic, message, options = {}) {
        if (!this.isConnected) {
            console.warn('Not connected to MQTT broker. Message queued.');
            this.publishQueue.push({ type: 'publish', topic, message, options });
            return;
        }
        this.client.publish(topic, message, options, (err) => {
            if (err) {
                console.error('Failed to publish message:', err);
            }
        });
    }

    processPublishQueue() {
        while (this.publishQueue.length > 0 && this.isConnected) {
            const item = this.publishQueue.shift();
            switch (item.type) {
                case 'publish':
                    this.publish(item.topic, item.message, item.options);
                    break;
                case 'subscribe':
                    this.subscribe(item.topic);
                    break;
                case 'unsubscribe':
                    this.unsubscribe(item.topic);
                    break;
            }
        }
    }

    disconnect() {
        if (this.client) {
            this.client.end(true, () => {
                this.isConnected = false;
                clearTimeout(this.reconnectTimer);
                this.reconnectTimer = null;
                if (this.processQueueInterval) {
                    clearInterval(this.processQueueInterval);
                    this.processQueueInterval = null;
                }
                console.log('Disconnected from MQTT broker');
            });
        }
    }
}