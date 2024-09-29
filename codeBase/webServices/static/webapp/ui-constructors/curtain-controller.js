
class CurtainAnimation {
    constructor({
        curtainLeftSelector,
        curtainRightSelector,
        animationDuration = 5000,
    }) {
        this.curtainLeft = document.querySelector(curtainLeftSelector);
        this.curtainRight = document.querySelector(curtainRightSelector);
        this.animationDuration = animationDuration;

        this.isAnimating = false;
        this.isOpening = false;
        this.openProgress = 0; // 0 = fully closed, 1 = fully open
        this.animationFrameId = null;
        this.onCurtainPositionChange = () => {};
    }

    setTransform(element, progress) {
        const maxTranslate = 70;
        const translate = maxTranslate * progress;
        const direction = element === this.curtainLeft ? -1 : 1;
        element.style.transform = `translate(${direction * translate}%, 0%)`;
    }

    updateCurtainPosition() {
        this.setTransform(this.curtainLeft, this.openProgress);
        this.setTransform(this.curtainRight, this.openProgress);
        this.onCurtainPositionChange(this.openProgress);
    }


    animateCurtains(targetProgress) {
        const startProgress = this.openProgress;
        const startTime = performance.now();
        const animationDurationAdjusted = this.animationDuration * Math.abs(targetProgress - startProgress);

        const animate = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const animationProgress = Math.min(elapsedTime / animationDurationAdjusted, 1);

            this.openProgress = startProgress + (targetProgress - startProgress) * animationProgress;
            this.updateCurtainPosition();

            if (animationProgress < 1 && this.isAnimating) {
                this.animationFrameId = requestAnimationFrame(animate);
            } else {
                this.isAnimating = false;
                this.openProgress = targetProgress;
                this.updateCurtainPosition();
            }
        };

        this.isAnimating = true;
        this.animationFrameId = requestAnimationFrame(animate);
    }

    startAnimation(opening) {
        this.stopAnimation(); // Stop any ongoing animation
        this.isOpening = opening;
        const targetProgress = this.isOpening ? 1 : 0;
        this.animateCurtains(targetProgress);
    }

    stopAnimation() {
        this.isAnimating = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }

    // Add a method to set the open progress directly
    setOpenProgress(progress) {
        this.openProgress = progress;
        this.updateCurtainPosition();
    }
}




// Example usage:
// Create an instance of the CurtainAnimation class
// const curtainAnimation = new CurtainAnimation({
//     curtainLeftSelector: '.curtain-left',
//     curtainRightSelector: '.curtain-right',
//     openButtonSelector: '#openButton',
//     closeButtonSelector: '#closeButton',
//     animationDuration: 5000, // 5 seconds
// });



class CurtainController {
    constructor(eventBus, mqttClient) {
        this.eventBus = eventBus;
        this.mqttClient = mqttClient;
        this.curtains = [];
        this.currentCurtain = null;
        this.curtainAnimation = new CurtainAnimation({
            curtainLeftSelector: '.curtain-left',
            curtainRightSelector: '.curtain-right',
            animationDuration: 5000
        });
        this.curtainAnimation.onCurtainPositionChange = (progress) => {
            if (this.currentCurtain) {
                this.currentCurtain.position = progress;
                if (progress == 0){
                    // if user open the curtain and forget to press again stop button, we send 'OFF' to both open and close datapoint after animation will be end to stop curtain motor.
                    // but we have a problem, if we automatically send 'OFF' command, we can't use this feature that when curtain animation will be end, we can send 'OFF' command
                    // when ever we want. for example. if animation duration was not sufficient and curtain not open or close for our desire position, in previous implementation 
                    // user can press open or close button whenever he wants to stop the motor but if we implement this feature, user can't do this and be ending the animation
                    // duration, program send 'OFF' command automatically and make curtian motor off.

                    //  set off both datapoints cause to turn off aech correspond 'curtain-card' in all home user app pages
                    this.updateCurtainCard(this.currentCurtain, false);
                    const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                    this.updateCurtain(datapoint.function_name, 'OFF');
                    const datapoint2 = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                    this.updateCurtain(datapoint2.function_name, 'OFF');
                }
                else if (progress > 0){
                    this.updateCurtainCard(this.currentCurtain, true);
                }
                else if (progress == 1){
                    // if user open the curtain and forget to press again stop button, we send 'OFF' to both open and close datapoint after animation will be end to stop curtain motor.
                    // but we have a problem, if we automatically send 'OFF' command, we can't use this feature that when curtain animation will be end, we can send 'OFF' command
                    // when ever we want. for example. if animation duration was not sufficient and curtain not open or close for our desire position, in previous implementation 
                    // user can press open or close button whenever he wants to stop the motor but if we implement this feature, user can't do this and be ending the animation
                    // duration, program send 'OFF' command automatically and make curtian motor off.

                    // const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                    // this.updateCurtain(datapoint.function_name, 'OFF');
                    // const datapoint2 = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                    // this.updateCurtain(datapoint2.function_name, 'OFF');
                }
            }
        };
        this.initEventListeners();
    }

    initEventListeners() {
        document.getElementById('openButton').addEventListener('click', () => this.handleButtonClick('open'));
        document.getElementById('closeButton').addEventListener('click', () => this.handleButtonClick('close'));
    }

    handleButtonClick(action) {
        if (this.currentCurtain) {
            if (this.curtainAnimation.isAnimating) {
                if ((action === 'open' && this.curtainAnimation.isOpening) || (action === 'close' && !this.curtainAnimation.isOpening)) {
                    // Cancel the current animation if the same button is pressed again
                    this.curtainAnimation.stopAnimation();
                    if (action === 'open') {
                        // find currentCurtain datapoint_functions that have curtain_function open
                        const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                        // in this situation becuase we are already animating, we need to send the opposite command to stop the animation
                        this.updateCurtain(datapoint.function_name, 'OFF');
                    }
                    else if (action === 'close') {
                        const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                        this.updateCurtain(datapoint.function_name, 'OFF');
                    }
                } else {
                    // Reverse the animation if the opposite button is pressed
                    this.curtainAnimation.stopAnimation();
                    this.curtainAnimation.startAnimation(!this.curtainAnimation.isOpening);
                    if (action === 'open') {
                        const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                        this.updateCurtain(datapoint.function_name, 'ON');
                        const datapoint2 = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                        this.updateCurtain(datapoint2.function_name, 'OFF');
                    }
                    else if (action === 'close') {
                        const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                        this.updateCurtain(datapoint.function_name, 'ON');
                        const datapoint2 = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                        this.updateCurtain(datapoint2.function_name, 'OFF');
                    }
                }
            } else {
                if (action === 'open' && this.curtainAnimation.openProgress < 1) {
                    this.curtainAnimation.startAnimation(true);
                    const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                    this.updateCurtain(datapoint.function_name, 'ON');
                    // const datapoint2 = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                    // this.updateCurtain(datapoint2.function_name, 'OFF');
                } else if (action === 'close' && this.curtainAnimation.openProgress > 0) {
                    this.curtainAnimation.startAnimation(false);
                    const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                    this.updateCurtain(datapoint.function_name, 'ON');
                    // const datapoint2 = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                    // this.updateCurtain(datapoint2.function_name, 'OFF');
                }
                else if (action === 'open' && this.curtainAnimation.openProgress == 1){
                    const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'open');
                    this.updateCurtain(datapoint.function_name, 'OFF');
                }
                else if (action === 'close' && this.curtainAnimation.openProgress == 0){

                    const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.curtain_function === 'close');
                    this.updateCurtain(datapoint.function_name, 'OFF');
                }
            }

        }
    }

    addCurtain(curtain) {
        this.curtains.push(curtain);
        // this.createCurtainCard(curtain);
    }

    createCurtainCard(curtain) {
        const correspond_zone_content_element = document.querySelector(`.content[data-menu-content-zone="${curtain.zone_uuid}"]`);
        const card_section = document.createElement('div');
        card_section.className = 'col-6';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.setAttribute('data-ui-element-uuid', curtain.uuid);
        card.setAttribute('data-ui-element-type', curtain.button_type);
        card.innerHTML = `
            <div class="icon-section d-flex align-items-end">
                ${curtain.off_icon}
            </div>
            <div class="text-section d-flex flex-column align-items-start">
                <div class="big-text animation-text-container" id="overflow-text"><span id="card-name">${curtain.button_name}</span></div>
                <div class="little-text"><span id="card-status">${curtain.off_text}</span></div>
            </div>
        `;
        card.addEventListener('click', () => this.openCurtainModal(curtain));
        card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card_section);
    }
    









    setupCurtainSidebarsection() {
        const sidebarSection = document.createElement('div');
        sidebarSection.className = 'curtain-sidebar-section';

        this.curtains.forEach(curtain => {
            const curtainElement = document.createElement('div');
            curtainElement.className = 'curtain-sidebar-item';
            curtainElement.textContent = curtain.button_name;
            curtainElement.addEventListener('click', () => this.changeCurtainFocus(curtain));
            sidebarSection.appendChild(curtainElement);
        });

        const controlsSection = document.createElement('div');
        controlsSection.className = 'curtain-controls-section';

        const openButton = document.createElement('button');
        openButton.textContent = 'Open';
        openButton.addEventListener('click', () => this.handleButtonClick('open'));

        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.addEventListener('click', () => this.handleButtonClick('close'));

        controlsSection.appendChild(openButton);
        controlsSection.appendChild(closeButton);

        sidebarSection.appendChild(controlsSection);

        document.querySelector('.sidebar').appendChild(sidebarSection);
    }

    changeCurtainFocus(curtain) {
        this.currentCurtain = curtain;
        this.curtainAnimation.animationDuration = curtain.animation_duration;
        this.curtainAnimation.setOpenProgress(curtain.position);
        // Update the curtain animation display here
    }













    openCurtainModal(curtain) {
        this.currentCurtain = curtain;
        document.getElementById('curtain-modal-title').textContent = curtain.button_name.toLowerCase();
        
        // Set the initial state of the curtain animation
        this.curtainAnimation.setOpenProgress(curtain.position);
        this.curtainAnimation.animationDuration = this.currentCurtain.animation_duration;
        bootstrap.Modal.getOrCreateInstance(document.getElementById('curtain-modal')).show();
    }

    updateCurtainModal(curtain) {
        if (this.currentCurtain == curtain) {
            // for mitigating race condition in 'onCurtainPositionChange' progress === 0 and progress === 1, we set constraint on this function
            if (this.currentCurtain.position > 0 && this.currentCurtain.position < 1){
                this.curtainAnimation.setOpenProgress(this.currentCurtain.position);
            }
        }
    }

    updateCurtain(action, value) {
        const datapoint = this.currentCurtain.datapoint_functions.find(dp => dp.function_name === action);
        if (datapoint) {
            const topic = `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/set`;
            this.mqttClient.publish(topic, value);
            this.updateCurtainCard(this.currentCurtain, this.currentCurtain.position > 0? true : false);
            this.updateCurtainModal(this.currentCurtain);
            console.log(topic);
            console.log(`Updated ${action} to ${value}`);
        }
    }

    updateCurtainCard(curtain, isOpen) {
        const card = document.querySelector(`.custom-card[data-ui-element-uuid="${curtain.uuid}"]`);
        if (card) {
            card.querySelector('#card-status').textContent = isOpen ? curtain.on_text : curtain.off_text;
            // card.querySelector('.icon-section').innerHTML = isOpen ? curtain.on_icon : curtain.off_icon;
            // card.style.backgroundColor = isOpen ? curtain.on_color : curtain.off_color;
            card.classList.toggle("active", isOpen);
        }
    }

    setupSubscriptions(curtain) {
        const topics = curtain.datapoint_functions.flatMap(datapoint => 
            `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/get`
        );
        this.eventBus.updateCategory(`curtain-ui-element-${curtain.uuid}`, topics, (topic) => {
            return (message) => {
                const datapoint = curtain.datapoint_functions.find(dpf => dpf.function_name === topic.split('/')[6] && dpf.device_uuid === topic.split('/')[4]);
                if (datapoint) {
                    const isOpen = message === 'ON';
                    // this.updateCurtainCard(curtain, isOpen);
                    // if (this.currentCurtain && this.currentCurtain.uuid === curtain.uuid) {
                    //     // because we have not sent position over mqtt and have'nt any datapoint for this feature, so setting position every time not applicable
                    //     // this.curtainAnimation.setOpenProgress(this.currentCurtain.position);
                        
                    // }
                }
            }
        });
    }
}


// // Initialize CurtainController
// const curtainController = new CurtainController(eventBus, mqttClient);

// // Example usage: Add curtains from UI elements
// const curtainElements = [
    
//     {
//         "uuid": "eb30a807-fe0a-47d0-85ae-e1bce3568287",
//         "name": "curtain",
//         "descriptions": null,
//         "button_name": "kitchen curtain",
//         "on_text": "ON",
//         "off_text": "OFF",
//         "on_color": "#45aaf2",
//         "off_color": "#45aaf2",
//         "on_icon": "<i class=\"fa-thin fa-lightbulb-cfl-on\"></i>",
//         "off_icon": "<i class=\"fa-thin fa-lightbulb-cfl\"></i>",
//         "add_to_home": false,
//         "button_type": "curtain",
//         "zone_uuid": "4ee3f099-0efc-4161-8722-ecc4710bf860",
//         "ui_type": "curtainui",
//         "animation_duration": 5000,
//         "datapoint_functions": [
//             {
//                 "curtain_function": "open",
//                 "display_name": "Switch 1",
//                 "function_name": "switch_1",
//                 "value_type": "BOOLEAN",
//                 "device_uuid": "f1d31a3d-5aba-4405-b795-aa08a2a9cc20"
//             },
//             {
//                 "curtain_function": "close",
//                 "display_name": "Switch 2",
//                 "function_name": "switch_2",
//                 "value_type": "BOOLEAN",
//                 "device_uuid": "f1d31a3d-5aba-4405-b795-aa08a2a9cc20"
//             }
//         ]
//     }
    
//     // Add more curtains here
// ];


// // Set up subscriptions for each curtain
// all_home_ui_elements.forEach(curtain => {
//     const curtain = {
//         ...curtain,
//         position: 0
//     }
//     curtainController.addCurtain(curtain);
//     curtainController.createCurtainCard(curtain);
//     curtainController.setupSubscriptions(curtain);
// });

// curtainController.setupCurtainSidebarsection();
