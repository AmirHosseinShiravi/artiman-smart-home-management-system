class TemperatureDial {
    constructor(tempDisplaySelector, tempHandleSelector, dialCenterSelector) {
        this.tempDisplay = document.querySelector(tempDisplaySelector);
        this.tempHandle = document.querySelector(tempHandleSelector);
        this.dialCenter = document.querySelector(dialCenterSelector);

        this.minTemp = 16.0;
        this.maxTemp = 32.0;
        this.tempRange = this.maxTemp - this.minTemp;
        
        this.onTemperatureChange = null;

        this.origin = this.calculateRotationOrigin();
        this.rotating = false;
        this.initEventListeners();
    }

    calculateRotationOrigin() {
        const { width, height, x, y } = this.dialCenter.getBoundingClientRect();
        return {
            x: x + width / 2,
            y: y + height / 2,
        };
    }

    handleMouseDown = (event) => {
        this.rotating = true;
    }

    handleMouseMove = (event) => {
        if (this.rotating) {
            const { clientX, clientY } = event;
            this.rotate(clientX, clientY);
        }
    }

    handleTouchMove = (event) => {
        if (this.rotating) {
            event.preventDefault();
            const { clientX, clientY } = event.touches[0];
            this.rotate(clientX, clientY);
        }
    }

    handleMouseUp = (event) => {
        this.rotating = false;
        if (this.onTemperatureChange) {
            this.onTemperatureChange(parseFloat(this.tempDisplay.textContent));
        }
    }

    rotate(x, y) {
        const angle = Math.atan2(y - this.origin.y, x - this.origin.x);
        const angleDegrees = 180 + angle * 180 / Math.PI;
        this.updateDial(angleDegrees);
    }

    updateDial(angle) {
        const percentageOfFullRange = ((360 + (angle - 90)) % 360) / 360;
        const newTemp = (this.minTemp + this.tempRange * percentageOfFullRange).toFixed(1);
        const hue = percentageOfFullRange < 0.5 ? 200 : 5;
        const alpha = 40 + 2 * 45 * Math.abs(percentageOfFullRange - 0.5);

        this.tempDisplay.textContent = newTemp;
        document.documentElement.style.setProperty("--temp-rotation", `${angle}deg`);
        document.documentElement.style.setProperty("--temp-hue", hue);
        document.documentElement.style.setProperty("--temp-alpha", `${alpha}%`);
    }

    initEventListeners() {
        this.tempHandle.addEventListener("mousedown", this.handleMouseDown);
        this.tempHandle.addEventListener("touchstart", this.handleMouseDown);

        this.tempHandle.addEventListener("mousemove", this.handleMouseMove);
        this.tempHandle.addEventListener("touchmove", this.handleTouchMove, { passive: false });

        this.tempHandle.addEventListener("mouseup", this.handleMouseUp);
        this.tempHandle.addEventListener("touchend", this.handleMouseUp);

        window.addEventListener("resize", () => {
            this.origin = this.calculateRotationOrigin();
        });

    }

    setTemperature(temp) {
        const percentageOfFullRange = (temp - this.minTemp) / this.tempRange;
        const angle = percentageOfFullRange * 360 + 90;
        this.updateDial(angle);
    }
}

class ThermostatController {
    constructor(eventBus, mqttClient) {
        this.eventBus = eventBus;
        this.mqttClient = mqttClient;
        this.thermostats = [];
        this.currentThermostat = null;
        this.temperatureDial = new TemperatureDial("#temp-display", "#temp-handle", "#dial-center");
        this.temperatureDial.onTemperatureChange = this.handleTemperatureChange.bind(this);
        this.initEventListeners();
    }

    initEventListeners() {
        document.querySelector('.thermostat-power-switch .bbb').addEventListener('click', this.togglePower.bind(this));
        document.querySelectorAll('input[name="heat_cool"]').forEach(radio => {
            radio.addEventListener('change', this.handleOperationModeChange.bind(this));
        });
        document.querySelectorAll('input[name="fan_speed"]').forEach(radio => {
            radio.addEventListener('change', this.handleFanSpeedChange.bind(this));
        });
    }

    addThermostat(thermostat) {
        this.thermostats.push(thermostat);
        this.createThermostatCard(thermostat);
    }

    createThermostatCard(thermostat) {
        const correspond_zone_content_element = document.querySelector(`.content[data-menu-content-zone="${thermostat.zone_uuid}"]`);
        // const card_section = document.createElement('div');
        // card_section.className = 'col-4';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.style.overflow= 'hidden';
        // card.style.gridColumn = 'span 2';
        card.setAttribute('data-ui-element-uuid', thermostat.uuid);
        card.setAttribute('data-ui-element-type', thermostat.button_type);
        card.innerHTML = `
            <div style="display: flex;flex-direction: row;justify-content: space-between;align-items: center;">
                <div class="" style="display: flex;height: 250px;align-items: flex-end;">
                    <div class="text-section d-flex flex-column align-items-start">
                        <div class="big-text animation-text-container overflow-text"><span id="card-name">${thermostat.button_name}</span></div>
                        <div class="little-text"><span id="card-status">${thermostat.off_text}</span></div>
                    </div>
                </div>
                <div class="">
                    <div class="icon-section d-flex align-items-end" style="${thermostat.background_image_style};background-image: url('${thermostat.background_image}')">
                    </div>
                </div>
            </div>
        `;

        card.addEventListener('click', () => this.openThermostatModal(thermostat));
        // card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card);
    }

    createThermostatCardForHomePage(thermostat) {
        const correspond_zone_content_element = document.querySelector(`.home-favorite-ui-elements-container`);
        // const card_section = document.createElement('div');
        // card_section.className = 'col-4';
        const card = document.createElement('div');
        card.className = 'custom-card';
        card.style.overflow= 'hidden';
        // card.style.gridColumn = 'span 2';
        card.setAttribute('data-ui-element-uuid', thermostat.uuid);
        card.setAttribute('data-ui-element-type', thermostat.button_type);
        card.innerHTML = `
            <div style="display: flex;flex-direction: row;justify-content: space-between;align-items: center;">
                <div class="" style="display: flex;height: 250px;align-items: flex-end;">
                    <div class="text-section d-flex flex-column align-items-start">
                        <div class="big-text animation-text-container overflow-text"><span id="card-name">${thermostat.button_name}</span></div>
                        <div class="little-text"><span id="card-status">${thermostat.off_text}</span></div>
                    </div>
                </div>
                <div class="">
                    <div class="icon-section d-flex align-items-end" style="${thermostat.background_image_style};background-image: url('${thermostat.background_image}')">
                    </div>
                </div>
            </div>
        `;

        card.addEventListener('click', () => this.openThermostatModal(thermostat));
        // card_section.appendChild(card);
        correspond_zone_content_element.appendChild(card);
    }

    openThermostatModal(thermostat) {
        this.currentThermostat = thermostat;
        document.getElementById('current-temp').textContent = thermostat.currentTemp;
        this.temperatureDial.setTemperature(thermostat.targetTemp);
        document.getElementById('thermostat-power-button-text').textContent = thermostat.status === "ON" ? 'Turn Off' : 'Turn On';
        document.querySelector('.thermostat-power-switch .bbb').classList.toggle("active", thermostat.status === "ON");
        document.getElementById(`radio-${thermostat.operationMode.toLowerCase()}`).checked = true;
        if (thermostat.fanControlMode === 'Auto') {
            document.getElementById('radio-auto').checked = true;
        } else {
            document.getElementById(`radio-${thermostat.fanSpeed.toLowerCase()}`).checked = true;
        }
        
        bootstrap.Modal.getOrCreateInstance(document.getElementById('modaler')).show();
        setTimeout(()=>{
            this.temperatureDial.origin = this.temperatureDial.calculateRotationOrigin();
          }, 500);
    }

    handleTemperatureChange(newTemp) {
        if (this.currentThermostat) {
            this.currentThermostat.targetTemp = newTemp;
            this.updateThermostat('spt', newTemp);
        }
    }

    togglePower() {
        if (this.currentThermostat) {
            this.currentThermostat.status = this.check_values_validity(this.currentThermostat.status, "status") == "ON" ? "OFF" : "ON";
            const powerButton = document.querySelector('.thermostat-power-switch .bbb');
            powerButton.querySelector('span').textContent = this.currentThermostat.status === "ON" ? 'Turn Off' : 'Turn On';
            if (this.currentThermostat.status === "ON") {
                powerButton.classList.add("active");
            } else {
                powerButton.classList.remove("active");
            }
            this.updateThermostatCard(this.currentThermostat);
            this.updateThermostat('status', this.currentThermostat.status);
        }
    }

    handleOperationModeChange(event) {
        if (this.currentThermostat) {
            this.currentThermostat.operationMode = event.target.id === 'radio-heat' ? 'Heat' : 'Cool';
            this.updateThermostat('hc', this.currentThermostat.operationMode);
        }
    }

    handleFanSpeedChange(event) {
        if (this.currentThermostat) {
            const targetId = event.target.id.replace('radio-', '');
            this.currentThermostat.fanSpeed = targetId.replace(/^(low|medium|high)/i, match => match.charAt(0).toUpperCase() + match.slice(1).toLowerCase());
            
            if (targetId === 'auto') {
                this.currentThermostat.fanControlMode = 'Auto';
            } else {
                this.currentThermostat.fanControlMode = 'Manual';
            }
            
            this.updateThermostat('fms', this.currentThermostat.fanSpeed);
            this.updateThermostat('fct', this.currentThermostat.fanControlMode);
        }
    }

    updateThermostat(functionName, value) {
        const datapoint = this.currentThermostat.datapoint_functions.find(dp => dp.function_name === functionName);
        if (datapoint) {
            const topic = `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/set`;
            this.mqttClient.publish(topic, value.toString());
            this.updateThermostatCard(this.currentThermostat);
            this.updateThermostatModal(this.currentThermostat);
        }
    }

    updateThermostatCard(thermostat) {
        const cards = document.querySelectorAll(`.custom-card[data-ui-element-uuid="${thermostat.uuid}"]`);
        if (cards) {
            cards.forEach(card=>{
                card.querySelector('#card-status').textContent = thermostat.status == "ON" ? thermostat.on_text : thermostat.off_text;
                // Update card color based on status and color variables
                // if (thermostat.status == "ON") {
                //     card.style.backgroundColor = thermostat.on_color || '#45aaf2';
                //     card.querySelector('.icon-section').innerHTML = thermostat.on_icon;
                // } else {
                //     card.style.backgroundColor = thermostat.off_color || '#45aaf2';
                //     card.querySelector('.icon-section').innerHTML = thermostat.off_icon;
                // }

                card.querySelector('#card-status').textContent = thermostat.status == "ON" ? thermostat.on_text : thermostat.off_text;
                // card.querySelector('.icon-section').innerHTML = thermostat.status == "ON" ? thermostat.on_icon : thermostat.off_icon;
                // card.style.backgroundColor = thermostat.status == "ON" ? thermostat.on_color : thermostat.off_color;
                card.classList.toggle("active", thermostat.status == "ON");
            })
        }
    }

    updateThermostatModal(thermostat) {
        if (this.currentThermostat == null) {
            return;
        }
        if (this.currentThermostat.uuid == thermostat.uuid) {
            document.getElementById('current-temp').textContent = thermostat.currentTemp;
            this.temperatureDial.setTemperature(thermostat.targetTemp);
            document.getElementById('thermostat-power-button-text').textContent = thermostat.status == "ON" ? "Turn Off" : "Turn On";
            document.querySelector('.thermostat-power-switch .bbb').classList.toggle("active", thermostat.status == "ON");
            document.getElementById(`radio-${thermostat.operationMode.toLowerCase()}`).checked = true;
            if (thermostat.fanControlMode == "Auto") {
                document.querySelector('input[name="fan_speed"]').checked = false;
                document.getElementById('radio-auto').checked = true;
            } else {
                document.getElementById(`radio-${thermostat.fanSpeed.toLowerCase()}`).checked = true;
            }
        }
    }

















    // setupThermostatSidebarsection() {
    //     // add a inline element to the sidebar top with the name of the thermostat
    //     // when clicked, below thermostat show corresponding thermostat
    //     // thermostat controls:
    //     // power button to turn on or off the thermostat
    //     // temperature dial to control the temperature
    //     // operation mode button to control the operation mode
    //     // fan speed button to control the fan speed
    //     // fan control mode button to control the fan control mode  
    //     // send each change over mqtt
    //     // show thermostat controls change based on received mqtt messages
    //     const sidebarSection = document.createElement('div');
    //     sidebarSection.className = 'thermostat-sidebar-section';

    //     this.thermostats.forEach(thermostat => {
    //         const thermostatElement = document.createElement('div');
    //         thermostatElement.className = 'thermostat-sidebar-item';
    //         thermostatElement.textContent = thermostat.button_name;
    //         thermostatElement.addEventListener('click', () => this.showThermostatControls(thermostat));
    //         sidebarSection.appendChild(thermostatElement);
    //     });

    //     const controlsSection = document.createElement('div');
    //     controlsSection.className = 'thermostat-controls-section';
    //     controlsSection.style.display = 'none';

    //     // Assuming the thermostat controls are already designed and present in the HTML
    //     // We'll just move them to the sidebar and show/hide as needed
    //     const thermostatControls = document.querySelector('.thermostat-controls');
    //     if (thermostatControls) {
    //         controlsSection.appendChild(thermostatControls);
    //     }

    //     sidebarSection.appendChild(controlsSection);
    //     document.querySelector('.sidebar').appendChild(sidebarSection);

    //     // Helper methods
    //     showThermostatControls(thermostat) {
    //         this.currentThermostat = thermostat;
    //         controlsSection.style.display = 'block';
    //         this.updateThermostatControls();
    //     }

    //     updateThermostatControls() {
    //         // Update UI elements based on current thermostat state
    //         const powerButton = document.getElementById('thermostat-power-button');
    //         if (powerButton) {
    //             powerButton.textContent = this.currentThermostat.status === "ON" ? "Turn Off" : "Turn On";
    //         }

    //         const heatCoolRadios = document.querySelectorAll('input[name="heat-cool"]');
    //         heatCoolRadios.forEach(radio => {
    //             radio.checked = radio.value === this.currentThermostat.operationMode;
    //         });

    //         const fanSpeedRadios = document.querySelectorAll('input[name="fan-speed"]');
    //         fanSpeedRadios.forEach(radio => {
    //             radio.checked = radio.value === this.currentThermostat.fanSpeed;
    //         });

    //         const tempDial = document.querySelector('.temperature-dial');
    //         if (tempDial) {
    //             // Assuming there's a method to set the temperature on the dial
    //             tempDial.setTemperature(this.currentThermostat.targetTemp);
    //         }
    //     }

    //     // Event listeners for the controls
    //     document.getElementById('thermostat-power-button').addEventListener('click', () => {
    //         const newStatus = this.currentThermostat.status === "ON" ? "OFF" : "ON";
    //         this.updateThermostat("status", newStatus);
    //     });

    //     document.querySelectorAll('input[name="heat-cool"]').forEach(radio => {
    //         radio.addEventListener('change', (event) => {
    //             this.updateThermostat("hc", event.target.value);
    //         });
    //     });

    //     document.querySelectorAll('input[name="fan-speed"]').forEach(radio => {
    //         radio.addEventListener('change', (event) => {
    //             this.updateThermostat("fms", event.target.value);
    //         });
    //     });

    //     // Assuming there's an event or method to detect temperature dial changes
    //     document.querySelector('.temperature-dial').addEventListener('change', (event) => {
    //         this.updateThermostat("spt", event.target.value);
    //     });

    //     updateThermostat(property, value) {
    //         const datapoint = this.currentThermostat.datapoint_functions.find(dp => dp.function_name === property);
    //         if (datapoint) {
    //             const topic = `v1/controllers/${all_home_devices.find(device => device.uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/set`;
    //             this.mqttClient.publish(topic, value);
    //             this.updateThermostatCard(this.currentThermostat);
    //             this.updateThermostatControls();
    //         }
    //     }
    // }


















    check_values_validity(value, function_name) {
        
        if (function_name == "status") {
            if (value !== "ON" && value !== "OFF") {
                value = "OFF";
            }
            
        }

        if (function_name == "tmp") {
            
            if (typeof value == "string") {
                value = parseFloat(value);
            }
            if (value < 16.0) {
                value = 16.0;
            } else if (value > 32.0) {
                value = 32.0;
            }

        }


        if (function_name == "spt") {
            
            if (typeof value == "string") {
                value = parseFloat(value);
            }
            if (value < 16.0) {
                value = 16.0;
            } else if (value > 32.0) {
                value = 32.0;
            }
            
        }

        if (function_name == "fms") {
            if(value !== "Low" && value !== "Medium" && value !== "High") {
                value = "Low";
            }
        }

        if (function_name == "hc") {
            if (value != "Heat" && value != "Cool") {
                value = "Heat";
            }
        }

        if (function_name == "fct") {
            if (value !== "Auto" && value !== "Manual") {
                value = "Auto";
            }
        }
        return value;
    }

    setupSubscriptions(thermostat) {
        const topics = thermostat.datapoint_functions.flatMap(datapoint => 
            `v1/controllers/${all_home_devices.find(device => device.device_uuid === datapoint.device_uuid)?.controller_uuid}/devices/${datapoint.device_uuid}/functions/${datapoint.function_name}/get`,
        );
        this.eventBus.updateCategory(`thermostat-ui-element-${thermostat.uuid}`, topics, (topic) => {
            return (message) => {
                const datapoint = thermostat.datapoint_functions.find(dpf => dpf.function_name === topic.split('/')[6] && dpf.device_uuid === topic.split('/')[4]);
                console.log(datapoint);
                console.log(message);
                console.log(topic);
                if (datapoint) {
                    const validValue = this.check_values_validity(message, datapoint.function_name);
                    switch (datapoint.function_name) {
                        case 'status':
                            thermostat.status = validValue;
                            break;
                        case 'tmp':
                            thermostat.currentTemp = validValue;
                            break;
                        case 'spt':
                            thermostat.targetTemp = validValue;
                            break;
                        case 'fms':
                            thermostat.fanSpeed = validValue;
                            break;
                        case 'fct':
                            thermostat.fanControlMode = validValue;
                            break;
                        case 'hc':
                            thermostat.operationMode = validValue;
                            break;
                    }
                    this.updateThermostatCard(thermostat);
                    this.updateThermostatModal(thermostat);
                }
            }
        });
    }


}
