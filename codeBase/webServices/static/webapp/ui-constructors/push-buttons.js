// ... existing code ...

class PushButtonController {
    constructor(eventBus, mqttClient) {
        this.eventBus = eventBus;
        this.mqttClient = mqttClient;
        this.pushButtons = [];
        this.initEventListeners();
    }

    initEventListeners() {
        // Add any global event listeners if needed
    }

    addPushButton(pushButton) {
        this.pushButtons.push(pushButton);
    }

    createPushButtonCard(pushButton) {
        const correspond_zone_content_element = document.querySelector(`.content[data-menu-content-zone="${pushButton.zone_uuid}"]`);
        const card_section = document.createElement('div');
        card_section.className = 'col-6';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.setAttribute('data-ui-element-uuid', pushButton.uuid);
        card.setAttribute('data-ui-element-type', pushButton.button_type);
        card.innerHTML = `
            <div class="icon-section d-flex align-items-end">
                ${pushButton.off_icon}
            </div>
            <div class="text-section d-flex flex-column align-items-start">
                <div class="big-text animation-text-container" id="overflow-text"><span id="card-name">${pushButton.button_name}</span></div>
                <div class="little-text"><span id="card-status">${pushButton.off_text}</span></div>
            </div>
        `;
        card.addEventListener('click', () => this.pressPushButton(pushButton));
        card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card_section);
    }

    pressPushButton(pushButton) {
        this.updatePushButton(pushButton, 'ON');
    }

    updatePushButton(pushButton, newState) {
        const datapoint = pushButton.datapoint_functions[0]; // Assuming only one datapoint for a push button
        if (datapoint) {
            const topic = `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/set`;
            this.mqttClient.publish(topic, newState);
            this.updatePushButtonCard(pushButton, newState);
            console.log(`Pressed ${pushButton.button_name}`);
        }
    }

    updatePushButtonCard(pushButton, state) {
        const card = document.querySelector(`.custom-card[data-ui-element-uuid="${pushButton.uuid}"]`);
        if (card) {
            const isOn = state === 'ON';
            card.querySelector('#card-status').textContent = isOn ? pushButton.on_text : pushButton.off_text;
            // card.querySelector('.icon-section').innerHTML = isOn ? pushButton.on_icon : pushButton.off_icon;
            // card.style.backgroundColor = isOn ? pushButton.on_color : pushButton.off_color;
            card.classList.toggle("active", state === "ON");
        }
    }

    setupSubscriptions(pushButton) {
        const datapoint = pushButton.datapoint_functions[0];
        const topic = `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/get`;
        this.eventBus.updateCategory(`pushbutton-ui-element-${pushButton.uuid}`, [topic], (topic) => {
            return (message) => {
                this.updatePushButtonCard(pushButton, message);
            }
        });
    }
}

// // Initialize PushButtonController
// const pushButtonController = new PushButtonController(eventBus, mqttClient);

// // Example usage: Add push buttons from UI elements
// all_home_ui_elements.forEach(uiElement => {
//     if (uiElement.button_type === 'pushbutton') {
//         const pushButton = {
//             ...uiElement,
//             state: 'OFF' // Initial state
//         };
//         pushButtonController.addPushButton(pushButton);
//         pushButtonController.createPushButtonCard(pushButton);
//         pushButtonController.setupSubscriptions(pushButton);
//     }
// });

// ... existing code ...