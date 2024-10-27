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
        const statusSpan = document.createElement('span');
        statusSpan.classList.add('status-text');
        statusSpan.textContent = 'off';
        
        // Subscribe to MQTT topic for this switch
        const topic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
        this.eventBus.subscribe('switches', topic, (message) => {
            const isOn = message === 'ON';
            statusSpan.textContent = isOn ? 'on' : 'off';
            card.classList.toggle('on', isOn);
        });

        card.addEventListener('click', () => {
            const newState = statusSpan.textContent === 'off' ? 'ON' : 'OFF';
            this.eventBus.publish(topic, newState);
        });

        card.querySelector('.little-text').appendChild(statusSpan);
        return card;
    }

    createPushButtonUI(element) {
        const card = this.createBaseCard(element);
        card.classList.add('push-button');

        const topic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
        card.addEventListener('click', () => {
            this.eventBus.publish(topic, 'PUSH');
        });

        return card;
    }

    createCurtainUI(element) {
        const card = this.createBaseCard(element);
        card.classList.add('curtain-card');
        card.dataset.isCurtainButton = 'true';
    
        const statusSpan = document.createElement('span');
        statusSpan.classList.add('status-text');
        statusSpan.textContent = 'Closed';
    
        // Subscribe to MQTT topic for curtain state
        const stateTopic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
        this.eventBus.subscribe('curtains', stateTopic, (message) => {
            const isOpen = message === 'OPEN';
            statusSpan.textContent = isOpen ? 'Open' : 'Closed';
            card.classList.toggle('open', isOpen);
        });
    
        // Add click event to open the modal
        card.addEventListener('click', () => {
            const modal = document.getElementById('curtain-modal');
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
    
            // Update modal content with curtain data
            modal.querySelector('h1').textContent = element.name;
            modal.querySelector('.text-center.mb-4').textContent = element.name.toLowerCase();
    
            // Set up open button
            const openButton = modal.querySelector('#openButton');
            const openTopic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
            openButton.addEventListener('click', () => {
                this.eventBus.publish(openTopic, 'OPEN');
                modal.querySelector('.curtain-container').classList.add('open');
            });
    
            // Set up close button
            const closeButton = modal.querySelector('#closeButton');
            const closeTopic = `v1/devices/${element.datapoint_functions[1].device_uuid}/datapoints/${element.datapoint_functions[1].function_name}/state`;
            closeButton.addEventListener('click', () => {
                this.eventBus.publish(closeTopic, 'CLOSE');
                modal.querySelector('.curtain-container').classList.remove('open');
            });
        });
    
        card.querySelector('.little-text').appendChild(statusSpan);
        return card;
    }

    createThermostatUI(element) {
        const card = this.createBaseCard(element);
        card.classList.add('thermostat-card');
        card.dataset.isThermostatButton = 'true';
    
        const temperatureDisplay = document.createElement('div');
        temperatureDisplay.classList.add('temperature-display');
    
        // Subscribe to current temperature updates
        const currentTempTopic = `v1/devices/${element.datapoint_functions[1].device_uuid}/datapoints/${element.datapoint_functions[1].function_name}/state`;
        this.eventBus.subscribe('thermostats', currentTempTopic, (message) => {
            temperatureDisplay.textContent = `${message}°C`;
        });
    
        // Add click event to open the modal
        card.addEventListener('click', () => {
            const modal = document.getElementById('modaler');
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
    
            // Update modal content with thermostat data
            modal.querySelector('h1').textContent = element.name;
            modal.querySelector('#temp-display').textContent = temperatureDisplay.textContent.replace('°C', '');
            modal.querySelector('.text-center.text-muted.fw-bold span').textContent = temperatureDisplay.textContent.replace('°C', '');
    
            // Set up heat/cool control
            const heatCoolRadios = modal.querySelectorAll('input[name="heat_cool"]');
            const heatCoolTopic = `v1/devices/${element.datapoint_functions[2].device_uuid}/datapoints/${element.datapoint_functions[2].function_name}/state`;
            
            heatCoolRadios.forEach(radio => {
                radio.addEventListener('change', (event) => {
                    const value = event.target.id === 'radio-heat' ? 'heat' : 'cool';
                    this.eventBus.publish(heatCoolTopic, value);
                });
            });
    
            // Subscribe to heat/cool state updates
            this.eventBus.subscribe('thermostats', heatCoolTopic, (message) => {
                const radioId = message === 'heat' ? 'radio-heat' : 'radio-cool';
                modal.querySelector(`#${radioId}`).checked = true;
            });
    
            // Set up fan speed control
            const fanSpeedRadios = modal.querySelectorAll('input[name="fan_speed"]');
            const fanSpeedTopic = `v1/devices/${element.datapoint_functions[3].device_uuid}/datapoints/${element.datapoint_functions[3].function_name}/state`;
            
            fanSpeedRadios.forEach(radio => {
                radio.addEventListener('change', (event) => {
                    const value = event.target.id.replace('radio-', '');
                    this.eventBus.publish(fanSpeedTopic, value);
                });
            });
    
            // Subscribe to fan speed state updates
            this.eventBus.subscribe('thermostats', fanSpeedTopic, (message) => {
                const radioId = `radio-${message}`;
                modal.querySelector(`#${radioId}`).checked = true;
            });
        });
    
        card.querySelector('.little-text').appendChild(temperatureDisplay);
        return card;
    }

    createBaseCard(element) {
        const card = document.createElement('div');
        card.classList.add('custom-card');
        card.dataset.uuid = element.uuid;

        const iconSection = document.createElement('div');
        iconSection.classList.add('icon-section', 'd-flex', 'align-items-end');
        // Add appropriate icon based on element type
        iconSection.innerHTML = this.getIconForElement(element);

        const textSection = document.createElement('div');
        textSection.classList.add('text-section', 'd-flex', 'flex-column', 'align-items-start');

        const bigText = document.createElement('div');
        bigText.classList.add('big-text', 'animation-text-container');
        bigText.id = 'overflow-text';
        bigText.innerHTML = `<span>${element.name}</span>`;

        const littleText = document.createElement('div');
        littleText.classList.add('little-text');

        textSection.appendChild(bigText);
        textSection.appendChild(littleText);

        card.appendChild(iconSection);
        card.appendChild(textSection);

        return card;
    }

    getIconForElement(element) {
        // Add logic to return appropriate icon HTML based on element type
        switch (element.ui_type) {
            case 'switchui':
                return '<i class="fa fa-lightbulb-o" style="font-size: 48px;"></i>';
            case 'thermostatui':
                return '<svg width="48" height="48" viewBox="0 0 1024 1024" fill="none" class="icon" version="1.1"><!-- Add thermostat SVG path here --></svg>';
            // Add cases for other element types
            default:
                return '<i class="fa fa-question" style="font-size: 48px;"></i>';
        }
    }
}

// Usage:
// const eventBus = new EventBus(mqttClient);
// const generator = new UIElementGenerator(eventBus);
// generator.generateUIElements(uiElementsDict);













// class UIElementGenerator {
//     constructor(eventBus) {
//         this.eventBus = eventBus;
//         this.elementTypes = {
//             'switchui': this.createSwitchUI,
//             'pushbuttonui': this.createPushButtonUI,
//             'curtainui': this.createCurtainUI,
//             'thermostatui': this.createThermostatUI
//         };
//     }

//     generateUIElements(uiElementsDict) {
//         const container = document.getElementById('ui-elements-container');
//         for (const [uuid, element] of Object.entries(uiElementsDict)) {
//             const createFunction = this.elementTypes[element.ui_type];
//             if (createFunction) {
//                 const uiElement = createFunction.call(this, element);
//                 container.appendChild(uiElement);
//             } else {
//                 console.warn(`Unknown UI type: ${element.ui_type}`);
//             }
//         }
//     }

//     createSwitchUI(element) {
//         const card = this.createBaseCard(element);
//         const toggle = document.createElement('input');
//         toggle.type = 'checkbox';
//         toggle.classList.add('toggle-switch');
        
//         // Subscribe to MQTT topic for this switch
//         const topic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
//         this.eventBus.subscribe('switches', topic, (message) => {
//             toggle.checked = message === 'ON';
//         });

//         toggle.addEventListener('change', () => {
//             const value = toggle.checked ? 'ON' : 'OFF';
//             this.eventBus.publish(topic, value);
//         });

//         card.appendChild(toggle);
//         return card;
//     }

//     createPushButtonUI(element) {
//         const card = this.createBaseCard(element);
//         const button = document.createElement('button');
//         button.textContent = element.button_name;
//         button.classList.add('push-button');

//         const topic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
//         button.addEventListener('click', () => {
//             this.eventBus.publish(topic, 'PUSH');
//         });

//         card.appendChild(button);
//         return card;
//     }

//     createCurtainUI(element) {
//         const card = this.createBaseCard(element);
//         const openButton = document.createElement('button');
//         openButton.textContent = 'Open';
//         const closeButton = document.createElement('button');
//         closeButton.textContent = 'Close';

//         const openTopic = `v1/devices/${element.datapoint_functions[0].device_uuid}/datapoints/${element.datapoint_functions[0].function_name}/state`;
//         const closeTopic = `v1/devices/${element.datapoint_functions[1].device_uuid}/datapoints/${element.datapoint_functions[1].function_name}/state`;

//         openButton.addEventListener('click', () => this.eventBus.publish(openTopic, 'OPEN'));
//         closeButton.addEventListener('click', () => this.eventBus.publish(closeTopic, 'CLOSE'));

//         card.appendChild(openButton);
//         card.appendChild(closeButton);
//         return card;
//     }

//     createThermostatUI(element) {
//         const card = this.createBaseCard(element);
//         const temperatureDisplay = document.createElement('div');
//         const setPointInput = document.createElement('input');
//         setPointInput.type = 'number';

//         // Subscribe to current temperature updates
//         const currentTempTopic = `v1/devices/${element.datapoint_functions[1].device_uuid}/datapoints/${element.datapoint_functions[1].function_name}/state`;
//         this.eventBus.subscribe('thermostats', currentTempTopic, (message) => {
//             temperatureDisplay.textContent = `Current: ${message}°C`;
//         });

//         // Handle set point changes
//         const setPointTopic = `v1/devices/${element.datapoint_functions[2].device_uuid}/datapoints/${element.datapoint_functions[2].function_name}/state`;
//         setPointInput.addEventListener('change', () => {
//             this.eventBus.publish(setPointTopic, setPointInput.value);
//         });

//         card.appendChild(temperatureDisplay);
//         card.appendChild(setPointInput);
//         return card;
//     }

//     createBaseCard(element) {
//         const card = document.createElement('div');
//         card.classList.add('custom-card');
//         card.dataset.uuid = element.uuid;

//         const nameElement = document.createElement('h3');
//         nameElement.textContent = element.name;
//         card.appendChild(nameElement);

//         return card;
//     }
// }

// // Usage:
// // const eventBus = new EventBus(mqttClient);
// // const generator = new UIElementGenerator(eventBus);
// // generator.generateUIElements(uiElementsDict);