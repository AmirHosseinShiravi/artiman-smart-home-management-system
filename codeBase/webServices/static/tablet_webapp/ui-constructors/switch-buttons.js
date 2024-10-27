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
        // const card_section = document.createElement('div');
        // card_section.className = 'col-4';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.style.overflow= 'hidden';
        // card.style.gridColumn = 'span 2';
        // card.style.backgroundSize= 'cover';
        // card.style.backgroundPosition= '85px -15vh';
        // // card.style.backgroundColor= "white";
        // card.style.backgroundImage= "url(https://05d9-5-126-179-153.ngrok-free.app/static/tablet_webapp/images/img-Npe8IriTAzURNTvRZkgSV-removebg-preview.png)";

        card.setAttribute('data-ui-element-uuid', switchButton.uuid);
        card.setAttribute('data-ui-element-type', switchButton.button_type);
        card.innerHTML = `
            <div style="display: flex;flex-direction: row;justify-content: space-between;align-items: center;">
                <div class="" style="display: flex;height: 250px;align-items: flex-end;">
                    <div class="text-section d-flex flex-column align-items-start">
                        <div class="big-text animation-text-container overflow-text"><span id="card-name">${switchButton.button_name}</span></div>
                        <div class="little-text"><span id="card-status">${switchButton.off_text}</span></div>
                    </div>
                </div>
                <div class="">
                    <div class="icon-section d-flex align-items-end" style="${switchButton.background_image_style};background-image: url('${switchButton.background_image}')">
                    </div>
                </div>
            </div>
        `;

        

        // <div class="icon-section d-flex align-items-end" style="margin-right: -20px;
        //                                                                     margin-top: -45px;
        //                                                                     width: 200px;
        //                                                                     height: 300px;background-image: url('https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/plant.png')">
        //             </div>

        card.addEventListener('click', () => this.toggleSwitch(switchButton));
        // card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card);
    }



    createSwitchCardForHomePage(switchButton) {
        const correspond_zone_content_element = document.querySelector(`.home-favorite-ui-elements-container`);
        // const card_section = document.createElement('div');
        // card_section.className = 'col-4';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.style.overflow= 'hidden';
        // card.style.gridColumn = 'span 2';
        // card.style.backgroundSize= 'cover';
        // card.style.backgroundPosition= '85px -15vh';
        // // card.style.backgroundColor= "white";
        // card.style.backgroundImage= "url(https://05d9-5-126-179-153.ngrok-free.app/static/tablet_webapp/images/img-Npe8IriTAzURNTvRZkgSV-removebg-preview.png)";

        card.setAttribute('data-ui-element-uuid', switchButton.uuid);
        card.setAttribute('data-ui-element-type', switchButton.button_type);
        card.innerHTML = `
            <div style="display: flex;flex-direction: row;justify-content: space-between;align-items: center;">
                <div class="" style="display: flex;height: 250px;align-items: flex-end;">
                    <div class="text-section d-flex flex-column align-items-start">
                        <div class="big-text animation-text-container overflow-text"><span id="card-name">${switchButton.button_name}</span></div>
                        <div class="little-text"><span id="card-status">${switchButton.off_text}</span></div>
                    </div>
                </div>
                <div class="">
                    <div class="icon-section d-flex align-items-end" style="${switchButton.background_image_style};background-image: url('${switchButton.background_image}')">
                    </div>
                </div>
            </div>
        `;

        card.addEventListener('click', () => this.toggleSwitch(switchButton));
        // card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card);
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
        const cards = document.querySelectorAll(`.custom-card[data-ui-element-uuid="${switchButton.uuid}"]`);
        if (cards) {
            cards.forEach(card=>{
                const isOn = state === 'ON';
                card.querySelector('#card-status').textContent = isOn ? switchButton.on_text : switchButton.off_text;
                // card.querySelector('.icon-section').innerHTML = isOn ? switchButton.on_icon : switchButton.off_icon;
                // card.style.backgroundColor = isOn ? switchButton.on_color : switchButton.off_color;
                card.classList.toggle("active", state === "ON");
            })
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