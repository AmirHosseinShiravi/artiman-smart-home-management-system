class EventBus {
    constructor(mqttClient) {
        this.categories = new Map();
        this.mqttClient = mqttClient;
    }

    subscribe(category, topic, callback) {
        if (!this.categories.has(category)) {
            this.categories.set(category, new Map());
        }
        const categoryMap = this.categories.get(category);
        if (!categoryMap.has(topic)) {
            categoryMap.set(topic, new Set());
            // Subscribe to MQTT topic
            this.mqttClient.subscribe(topic);
        }
        categoryMap.get(topic).add(callback);
        return () => this.unsubscribe(category, topic, callback);
    }

    unsubscribe(category, topic, callback) {
        if (this.categories.has(category)) {
            const categoryMap = this.categories.get(category);
            if (categoryMap.has(topic)) {
                const callbacks = categoryMap.get(topic);
                callbacks.delete(callback);
                if (callbacks.size === 0) {
                    categoryMap.delete(topic);
                    // Unsubscribe from MQTT topic
                    this.mqttClient.unsubscribe(topic);
                }
            }
            if (categoryMap.size === 0) {
                this.categories.delete(category);
            }
        }
    }

    publish(topic, message) {
        for (const [, categoryMap] of this.categories) {
            for (const [subscribedTopic, callbacks] of categoryMap) {
                if (this.topicMatches(subscribedTopic, topic)) {
                    callbacks.forEach(callback => callback(message));
                }
            }
        }
    }

    topicMatches(subscribedTopic, publishedTopic) {
        const subParts = subscribedTopic.split('/');
        const pubParts = publishedTopic.split('/');

        // If the subscribed topic ends with '#', it matches the rest of the published topic
        if (subParts[subParts.length - 1] === '#') {
            return pubParts.length >= subParts.length - 1 &&
                subParts.slice(0, -1).every((part, i) => part === '+' || part === pubParts[i]);
        }

        // Otherwise, the number of parts should be the same
        if (subParts.length !== pubParts.length) {
            return false;
        }

        // Check each part
        return subParts.every((subPart, i) => {
            const pubPart = pubParts[i];
            return subPart === '+' || subPart === pubPart;
        });
    }

    clearCategory(category) {
        if (this.categories.has(category)) {
            const categoryMap = this.categories.get(category);
            for (const topic of categoryMap.keys()) {
                // Unsubscribe from MQTT for each topic in the category
                this.mqttClient.unsubscribe(topic);
            }
            this.categories.delete(category);
        }
    }

    clearAllCategories() {
        for (const [, categoryMap] of this.categories) {
            for (const topic of categoryMap.keys()) {
                // Unsubscribe from MQTT for each topic
                this.mqttClient.unsubscribe(topic);
            }
        }
        this.categories.clear();
    }

    getTopicsInCategory(category) {
        return this.categories.has(category)
            ? Array.from(this.categories.get(category).keys())
            : [];
    }

    updateCategory(category, newTopics, callbackGenerator) {
        // Unsubscribe from old topics
        if (this.categories.has(category)) {
            const oldTopics = this.getTopicsInCategory(category);
            oldTopics.forEach(topic => {
                if (!newTopics.includes(topic)) {
                    this.mqttClient.unsubscribe(topic);
                }
            });
        }

        this.clearCategory(category);
        newTopics.forEach(topic => {
            this.subscribe(category, topic, callbackGenerator(topic));
        });
    }
}

