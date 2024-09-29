// ... existing code ...

class SwitchButtonController {
    constructor(eventBus, mqttClient) {
        this.eventBus = eventBus;
        this.mqttClient = mqttClient;
        this.switches = [];
        this.initEventListeners();
    }

    initEventListeners() {
        // Add any global event listeners if needed
    }

    addSwitch(switchButton) {
        this.switches.push(switchButton);
    }

    createSwitchCard(switchButton) {
        const correspond_zone_content_element = document.querySelector(`.content[data-menu-content-zone="${switchButton.zone_uuid}"]`);
        const card_section = document.createElement('div');
        card_section.className = 'col-6';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.setAttribute('data-ui-element-uuid', switchButton.uuid);
        card.setAttribute('data-ui-element-type', switchButton.button_type);
        card.innerHTML = `
            <div class="icon-section d-flex align-items-end">
                ${switchButton.off_icon}
            </div>
            <div class="text-section d-flex flex-column align-items-start">
                <div class="big-text animation-text-container" id="overflow-text"><span id="card-name">${switchButton.button_name}</span></div>
                <div class="little-text"><span id="card-status">${switchButton.off_text}</span></div>
            </div>
        `;
        card.addEventListener('click', () => this.toggleSwitch(switchButton));
        card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card_section);
    }

    toggleSwitch(switchButton) {
        const newState = switchButton.state === 'ON' ? 'OFF' : 'ON';
        this.switches.find(sw => sw.uuid === switchButton.uuid).state = newState;
        this.updateSwitch(switchButton, newState);
    }

    updateSwitch(switchButton, newState) {
        const datapoint = switchButton.datapoint_functions[0]; // Assuming only one datapoint for a switch
        if (datapoint) {
            const topic = `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/set`;
            this.mqttClient.publish(topic, newState);
            this.updateSwitchCard(switchButton, newState);
            console.log(`Updated ${switchButton.button_name} to ${newState}`);
        }
    }

    updateSwitchCard(switchButton, state) {
        const card = document.querySelector(`.custom-card[data-ui-element-uuid="${switchButton.uuid}"]`);
        if (card) {
            const isOn = state === 'ON';
            card.querySelector('#card-status').textContent = isOn ? switchButton.on_text : switchButton.off_text;
            // card.querySelector('.icon-section').innerHTML = isOn ? switchButton.on_icon : switchButton.off_icon;
            // card.style.backgroundColor = isOn ? switchButton.on_color : switchButton.off_color;
            card.classList.toggle("active", state === "ON");
        }
    }

    setupSubscriptions(switchButton) {
        const datapoint = switchButton.datapoint_functions[0];
        const topic = `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/get`;
        this.eventBus.updateCategory(`switch-ui-element-${switchButton.uuid}`, [topic], (topic) => {
            return (message) => {
                this.updateSwitchCard(switchButton, message);
            }
        });
    }
}

// // Initialize SwitchButtonController
// const switchButtonController = new SwitchButtonController(eventBus, mqttClient);

// // Example usage: Add switches from UI elements
// all_home_ui_elements.forEach(uiElement => {
//     if (uiElement.button_type === 'switch') {
//         const switchButton = {
//             ...uiElement,
//             state: 'OFF' // Initial state
//         };
//         switchButtonController.addSwitch(switchButton);
//         switchButtonController.createSwitchCard(switchButton);
//         switchButtonController.setupSubscriptions(switchButton);
//     }
// });

// ... existing code ...