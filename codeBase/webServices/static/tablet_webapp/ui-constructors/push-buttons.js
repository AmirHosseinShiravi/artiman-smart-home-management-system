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
        // const card_section = document.createElement('div');
        // card_section.className = 'col-4';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.style.overflow= 'hidden';
        // card.style.gridColumn = 'span 2';
        // card.style.backgroundSize= 'cover';
        // card.style.backgroundPosition= '80px -2vh';
        // card.style.width = "200px";
        // card.style.backgroundColor= "white";
        // card.style.backgroundImage= "url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/3d-elevator-icon-vertical-transport-floors-illustration-logo_762678-70574-removebg-preview.png)";
        // card.style.backgroundImage= "url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/chandelier2.png)";
        card.setAttribute('data-ui-element-uuid', pushButton.uuid);
        card.setAttribute('data-ui-element-type', pushButton.button_type);
        card.innerHTML = `
            <div style="display: flex;flex-direction: row;justify-content: space-between;align-items: center;">
                <div class="" style="display: flex;height: 250px;align-items: flex-end;">
                    <div class="text-section d-flex flex-column align-items-start">
                        <div class="big-text animation-text-container overflow-text"><span id="card-name">${pushButton.button_name}</span></div>
                        <div class="little-text"><span id="card-status">${pushButton.off_text}</span></div>
                    </div>
                </div>
                <div class="">
                    <div class="icon-section d-flex align-items-end" style="${pushButton.background_image_style};background-image: url('${pushButton.background_image}')">
                    </div>
                </div>
            </div>
        `;

        // <div class="icon-section d-flex align-items-end" style="margin-right: -50px;
        //                                                                     margin-top: -50px;
        //                                                                     width: 300px;
        //                                                                     height: 300px;
        //                                                                     background-image: url('https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/chandelier2.png')">
        card.addEventListener('click', () => this.pressPushButton(pushButton));
        // card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card);
    }


    createPushButtonCardForHomePage(pushButton) {
        const correspond_zone_content_element = document.querySelector(`.home-favorite-ui-elements-container`);
        // const card_section = document.createElement('div');
        // card_section.className = 'col-4';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.style.overflow= 'hidden';
        // card.style.gridColumn = 'span 2';
        // card.style.backgroundSize= 'cover';
        // card.style.backgroundPosition= '80px -2vh';
        // card.style.width = "200px";
        // card.style.backgroundColor= "white";
        // card.style.backgroundImage= "url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/3d-elevator-icon-vertical-transport-floors-illustration-logo_762678-70574-removebg-preview.png)";
        // card.style.backgroundImage= "url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/chandelier2.png)";
        card.setAttribute('data-ui-element-uuid', pushButton.uuid);
        card.setAttribute('data-ui-element-type', pushButton.button_type);
        card.innerHTML = `
            <div style="display: flex;flex-direction: row;justify-content: space-between;align-items: center;">
                <div class="" style="display: flex;height: 250px;align-items: flex-end;">
                    <div class="text-section d-flex flex-column align-items-start">
                        <div class="big-text animation-text-container overflow-text"><span id="card-name">${pushButton.button_name}</span></div>
                        <div class="little-text"><span id="card-status">${pushButton.off_text}</span></div>
                    </div>
                </div>
                <div class="">
                    <div class="icon-section d-flex align-items-end" style="${pushButton.background_image_style};background-image: url('${pushButton.background_image}')">
                    </div>
                </div>
            </div>
        `;

        // <div class="icon-section d-flex align-items-end" style="margin-right: -50px;
        //                                                                     margin-top: -50px;
        //                                                                     width: 300px;
        //                                                                     height: 300px;
        //                                                                     background-image: url('https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/chandelier2.png')">
        card.addEventListener('click', () => this.pressPushButton(pushButton));
        // card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card);
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
        const cards = document.querySelectorAll(`.custom-card[data-ui-element-uuid="${pushButton.uuid}"]`);
        if (cards) {
            cards.forEach(card=>{
                const isOn = state === 'ON';
                card.querySelector('#card-status').textContent = isOn ? pushButton.on_text : pushButton.off_text;
                // card.querySelector('.icon-section').innerHTML = isOn ? pushButton.on_icon : pushButton.off_icon;
                // card.style.backgroundColor = isOn ? pushButton.on_color : pushButton.off_color;
                card.classList.toggle("active", state === "ON");
            })
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