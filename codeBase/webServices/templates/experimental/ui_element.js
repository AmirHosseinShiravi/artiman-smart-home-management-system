class UIElementGenerator {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.elementTypes = {
            'switchui': this.createSwitchUI,
            'pushbuttonui': this.createPushButtonUI,
            'curtainui': this.createCurtainUI,
            'thermostatui': this.createThermostatUI
        };
    }

    generateUIElements(uiElementsDict) {
        const container = document.getElementById('ui-elements-container');
        for (const [uuid, element] of Object.entries(uiElementsDict)) {
            const createFunction = this.elementTypes[element.ui_type];
            if (createFunction) {
                const uiElement = createFunction.call(this, element);
                container.appendChild(uiElement);
            } else {
                console.warn(`Unknown UI type: ${element.ui_type}`);
            }
        }
    }

    createSwitchUI(element) {
        const card = this.createBaseCard(element);
        const toggle = document.createElement('input');
        toggle.type = 'checkbox';
        toggle.classList.add('toggle-switch');
        
        // Subscribe to MQTT topic for this switch
        const topic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
        this.eventBus.subscribe('switches', topic, (message) => {
            toggle.checked = message === 'ON';
        });

        toggle.addEventListener('change', () => {
            const value = toggle.checked ? 'ON' : 'OFF';
            this.eventBus.publish(topic, value);
        });

        card.appendChild(toggle);
        return card;
    }

    createPushButtonUI(element) {
        const card = this.createBaseCard(element);
        const button = document.createElement('button');
        button.textContent = element.button_name;
        button.classList.add('push-button');

        const topic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
        button.addEventListener('click', () => {
            this.eventBus.publish(topic, 'PUSH');
        });

        card.appendChild(button);
        return card;
    }

    createCurtainUI(element) {
        const card = this.createBaseCard(element);
        const openButton = document.createElement('button');
        openButton.textContent = 'Open';
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';

        const openTopic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
        const closeTopic = `v1/devices/${element.datapoint_functions[1].device_uuid}/datapoints/${element.datapoint_functions[1].function_name}/state`;

        openButton.addEventListener('click', () => this.eventBus.publish(openTopic, 'OPEN'));
        closeButton.addEventListener('click', () => this.eventBus.publish(closeTopic, 'CLOSE'));

        card.appendChild(openButton);
        card.appendChild(closeButton);
        return card;
    }

    createThermostatUI(element) {
        const card = this.createBaseCard(element);
        const temperatureDisplay = document.createElement('div');
        const setPointInput = document.createElement('input');
        setPointInput.type = 'number';

        // Subscribe to current temperature updates
        const currentTempTopic = `v1/devices/${element.datapoint_functions[1].device_uuid}/datapoints/${element.datapoint_functions[1].function_name}/state`;
        this.eventBus.subscribe('thermostats', currentTempTopic, (message) => {
            temperatureDisplay.textContent = `Current: ${message}°C`;
        });

        // Handle set point changes
        const setPointTopic = `v1/devices/${element.datapoint_functions[2].device_uuid}/datapoints/${element.datapoint_functions[2].function_name}/state`;
        setPointInput.addEventListener('change', () => {
            this.eventBus.publish(setPointTopic, setPointInput.value);
        });

        card.appendChild(temperatureDisplay);
        card.appendChild(setPointInput);
        return card;
    }

    createBaseCard(element) {
        const card = document.createElement('div');
        card.classList.add('custom-card');
        card.dataset.uuid = element.uuid;

        const nameElement = document.createElement('h3');
        nameElement.textContent = element.name;
        card.appendChild(nameElement);

        return card;
    }
}

// Usage:
// const eventBus = new EventBus(mqttClient);
// const generator = new UIElementGenerator(eventBus);
// generator.generateUIElements(uiElementsDict);