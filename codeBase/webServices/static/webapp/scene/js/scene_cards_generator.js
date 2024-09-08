// Global variables
// let linkage_rules = []; // Assume this is populated with your rules data
let ruleActionsStatus = {}; // To store the status of rule actions
let activeModalRuleUuid = null; // To keep track of which rule's modal is currently open

// Function to generate rule cards
function generateRuleCards() {
    const automationSection = document.querySelector('.scene-automation-rules-section .row');
    const tapToRunSection = document.querySelector('.scene-tap-to-run-rules-section .row');

    // Clear existing cards
    automationSection.innerHTML = '';
    tapToRunSection.innerHTML = '';

    // Remove all existing event listeners
    removeAllEventListeners();

    // Sort rules by index
    linkage_rules.sort((a, b) => a.index - b.index);

    linkage_rules.forEach(rule => {
        const card = createRuleCard(rule);
        if (rule.type === 'automation') {
            automationSection.appendChild(card);
            set_switch_color(rule, rule.status);
        } else if (rule.type === 'scene') {
            tapToRunSection.appendChild(card);
        }
    });

    // Reestablish event listeners
    setupEventListeners();

    // Subscribe to MQTT topics for rule actions and rules status
    // subscribeToRuleActionTopics();
    setupRuleActionsSubscriptions(project_uuid ,home_uuid);


    add_home_page_enabled_tap_to_run_rules_to_home_page();
    console.log('end of generateRuleCards')
}

function createRuleCard(rule) {
    const card = document.createElement('div');
    card.className = 'col-12';
    card.innerHTML = `
        <div class="row scene-rule-card" data-scene-${rule.type}-rule-id="${rule.index}" style="background-color: ${rule.style.color}">
            <div class="col-9 scene-rule-card-detail-section">
                <div class="icon-section d-flex align-items-end">
                    ${rule.style.icon ? `<i class="${rule.style.icon}"></i>` : '<i class="fa-solid fa-wand-magic-sparkles fa-2xl"></i>'}
                </div>
                <div class="text-section">
                    <div class="title-text">${rule.name}</div>
                    <div class="summary-text"><span id="status">${getConditionsSummary(rule)}</span></div>
                </div>
            </div>
            <div class="col-3 d-flex justify-content-end scene-rule-card-action-section">
                <div class="d-flex flex-column">
                    <div class="edit-icon" data-rule-index="${rule.index}" data-rule-type="${rule.type}" data-rule-uuid="${rule.rule_uuid}">
                        <i class="fa-solid fa-ellipsis-vertical fa-xl"></i>
                    </div>
                    ${rule.type === 'automation' ? `
                    <div class="rule-status-switch-container">
                        <div class="rule-status-switch">
                            <input type="checkbox" class="checkbox" id="checkbox-${rule.index}" ${rule.status ? 'checked' : ''}>
                            <label class="switch" for="checkbox-${rule.index}">
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;

    return card;
}

function add_home_page_enabled_tap_to_run_rules_to_home_page(){
    const home_page_scene_container = document.querySelector('.main-page.home-page .top-container .scene-container div');
    home_page_scene_container.innerHTML = '';
    const all_tap_to_run_rules_with_add_to_home_flag = linkage_rules.filter(rule => rule.add_to_home_status === "true" && rule.type === "scene");
    if(all_tap_to_run_rules_with_add_to_home_flag){
        all_tap_to_run_rules_with_add_to_home_flag.forEach(rule => {
            const button = document.createElement('button');
            button.className = "btn btn-lg me-2 main_page_favorite_scene_shortcut";
            button.dataset.sceneSceneRuleId = rule.index;
            button.textContent = rule.name;
            button.style.backgroundColor = rule.style.color;
            const inputColor = rule.style.color;
            const hsl = tinycolor(inputColor).toHsl(); // convert to HSL
            // Calculate the brightness of the input color
            const brightness = hsl.l * 255; // convert lightness to brightness (0-255)
            // Adjust the lightness based on brightness
            let newLightness;
            if (brightness < 128) { // dark color
              newLightness = Math.min(1, hsl.l + 0.6); // increase lightness for dark colors
            } else { // light color
              newLightness = Math.max(0, hsl.l - 0.6); // decrease lightness for light colors
            }
            const moreSaturatedHsl = {
              h: hsl.h,
              s: hsl.s,
              l: newLightness
            };
            button.style.color = tinycolor(moreSaturatedHsl).toHexString();
            home_page_scene_container.appendChild(button);
            button.addEventListener('click', handleMainPageTapToRunButtonClick);
        })
    }
}

function getConditionsSummary(rule) {
    const conditionIcons = {
        'tap-to-run': '<i class="fa-regular fa-hand-pointer"></i>',
        'timer': '<i class="fa-regular fa-clock"></i>',
        'device_report': '<i class="fa-regular fa-microchip"></i>'
    };

    const actionIcons = {
        'delay': '<i class="fa-regular fa-hourglass-half"></i>',
        'device_issue': '<i class="fa-regular fa-microchip"></i>'
    };

    function getIconsForList(list, iconMap, maxIcons = 3) {
        const iconCounts = {};
        list.forEach(item => {
            const type = item.entity_type || item.action_executor;
            iconCounts[type] = (iconCounts[type] || 0) + 1;
        });

        let icons = [];
        Object.entries(iconCounts).forEach(([type, count]) => {
            const icon = iconMap[type];
            const iconCount = Math.min(count, Math.ceil(maxIcons / Object.keys(iconCounts).length));
            icons = icons.concat(Array(iconCount).fill(icon));
        });

        icons = icons.slice(0, maxIcons);
        return icons.length > 2 ? [...icons.slice(0, 2), '...', icons[icons.length - 1]] : icons;
    }

    const generatedConditionIcons = getIconsForList(rule.conditions, conditionIcons);
    const generatedActionIcons = getIconsForList(rule.actions, actionIcons);

    return `<span>${generatedConditionIcons.join('   ')} &nbsp; <i class="fa-regular fa-arrow-right"></i> &nbsp; ${generatedActionIcons.join('   ')}</span>`;
}

function setupEventListeners() {
    // Setup event listeners for edit icons
    document.querySelectorAll('.edit-icon').forEach(icon => {
        icon.addEventListener('click', handleEditClick);
    });

    // Setup event listeners for automation switches
    document.querySelectorAll('.checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleAutomationStatusChange);
    });

    // Setup event listeners for tap-to-run cards
    document.querySelectorAll('.scene-tap-to-run-rules-section .scene-rule-card .scene-rule-card-detail-section').forEach(card => {
        card.addEventListener('click', handleTapToRunClick);
    });
}

function removeAllEventListeners() {
    // Implement logic to remove all event listeners
    // This might involve cloning and replacing elements
    document.querySelectorAll('.edit-icon').forEach(icon => {
        icon.removeEventListener('click', handleEditClick);
    });

    // Setup event listeners for automation switches
    document.querySelectorAll('.checkbox').forEach(checkbox => {
        checkbox.removeEventListener('change', handleAutomationStatusChange);
    });

    // Setup event listeners for tap-to-run cards
    document.querySelectorAll('.scene-tap-to-run-rules-section .scene-rule-card').forEach(card => {
        card.removeEventListener('click', handleTapToRunClick);
    });

    document.querySelectorAll('.main-page.home-page .top-container .scene-container div button').forEach(button => {
        button.removeEventListener('click', handleMainPageTapToRunButtonClick);
    })
}

function handleEditClick(event) {
    const ruleIndex = event.currentTarget.dataset.ruleIndex;
    const ruleType = event.currentTarget.dataset.ruleType;
    const ruleUuid = event.currentTarget.dataset.ruleUuid;
    if (scene_wizard_instance !== null) {
        scene_wizard_instance.destroy();
    }
    scene_wizard_instance = null;
    scene_wizard_instance = new SceneWizardPageClass();
    scene_wizard_instance.render_scene_wizard_page(rule_id=ruleUuid);
    scene_wizard_instance.showPage('#scene-wizard-page');


    console.log(`Edit ${ruleType} rule with index ${ruleIndex}`);
}

function set_switch_color(rule, status) {
    const switch_label = document.querySelector(`.scene-rule-card[data-scene-${rule.type}-rule-id="${rule.index}"] .rule-status-switch .switch`);
    if(status){

        const inputColor = rule.style.color;
        const hsl = tinycolor(inputColor).toHsl(); // convert to HSL
        const lightnessAdjustment = 0.4; // adjust lightness by 20%
        const newLightness = Math.min(1, Math.max(0, hsl.l - lightnessAdjustment));
        // clamp newLightness to [0, 1] range

        const moreSaturatedHsl = {
          h: hsl.h,
          s: hsl.s,
          l: newLightness
        };
        switch_label.style.backgroundColor = tinycolor(moreSaturatedHsl).toHexString();
    }
    else{
        switch_label.style.backgroundColor = "#e9e9eb";
    }
}

function handleAutomationStatusChange(event) {
    const ruleIndex = event.target.id.split('-')[1];
    const newStatus = event.target.checked;

    // Update rule status in linkage_rules
    const rule = linkage_rules.find(r => r.index == ruleIndex && r.type === 'automation');
    if (rule) {
        rule.status = newStatus;
        // Send MQTT message
         mqttClient.publish(`v1/projects/${project_uuid}/homes/${home_uuid}/linkage-rules/${rule.rule_uuid}/status/set`, newStatus ? 'enable' : 'disable');
    }

    set_switch_color(rule, newStatus);

}

function handleTapToRunClick(event) {
    const card = event.currentTarget.closest('.scene-rule-card');
    const ruleIndex = card.dataset.sceneSceneRuleId;
    const rule = linkage_rules.find(r => r.index == ruleIndex && r.type === 'scene');
    if (rule) {
        showActionsModal(rule);
    }
}

function handleMainPageTapToRunButtonClick(event){
    const ruleIndex = event.currentTarget.dataset.sceneSceneRuleId;
    const rule = linkage_rules.find(r => r.index == ruleIndex && r.type === 'scene');
    if (rule) {
        showActionsModal(rule);
    }
}

function create_device_item(device_name, zone_name, data_point_name, comparator, data_point_value) {
    const item_dom = document.createElement('div');
    item_dom.className = 'item-card';
    item_dom.innerHTML = `
                  <div class="item-icon-section">
                    <i class="fa-sharp fa-regular fa-microchip fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">${device_name}(${zone_name})</div>
                    <div class="detail-sub-title truncate-responsive">${data_point_name}: ${comparator} ${data_point_value}</div>
                  </div>
                  <div class="status-section">
                    <div class="status-icon">
                      <i class="fa-solid fa-loader fa-lg" style="color: #FFD43B;"></i>
                    </div>
                  </div>`;

    return item_dom
}

function create_delay_action_item(delay_string) {
    let item_dom = document.createElement('div');
    item_dom.className = 'item-card';
    item_dom.innerHTML = `
                  <div class="item-icon-section">
                    <i class="fa-regular fa-clock fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">Delay the action</div>
                    <div class="detail-sub-title truncate-responsive">${delay_string} Seconds</div>
                  </div>
                  <div class="status-section">
                    <div class="status-icon">
                      <i class="fa-solid fa-loader fa-lg" style="color: #FFD43B;"></i>
                    </div>
                  </div>`;
    return item_dom
}

function showActionsModal(rule) {
    // Create and show modal with actions list
    let modal = document.querySelector('#tap-to-run-actions-status-modal');
    let modal_body = document.querySelector('#tap-to-run-actions-status-modal .modal-body');
    const bootstrap_tap_to_run_modal_instance = bootstrap.Modal.getOrCreateInstance(modal);
    modal_body.innerHTML = `
            <div class="text-center fw-bold fs-6 pt-3">${rule.name} Actions</div>
            <ul class="actions-list">
                ${rule.actions.map(action =>{
                    if(action.action_executor === "device_issue"){
                        const device = all_home_devices.find(device => device.device_uuid === action.device_uuid);
                        if (device){
                            const zone = all_home_zones.find(zone => zone.zone_uuid === device.zone_uuid);
                            const dataPoint= device.dataPointFunctions.find(dataPoint => dataPoint.function_name === action.executor_property.function_code);
                            const device_action_card_el = create_device_item(device.name, zone.zone_name, dataPoint.display_name, " ", action.executor_property.function_value).outerHTML;
                            return `
                                <li data-action-code="${action.code}">
                                    ${device_action_card_el}
                                </li>`
                        }
                    }
                    else if (action.action_executor === "delay"){ 
                       
                            const delay_action_card_el = create_delay_action_item(action.executor_property.delay_seconds).outerHTML;
                            return `
                                <li data-action-code="${action.code}">
                                    ${delay_action_card_el}
                                </li>`
                        }
                    
                    }).join('')}
            </ul>
        `;

    // Set the active modal rule UUID
    activeModalRuleUuid = rule.rule_uuid;

    // Initial update of action statuses
    updateModalActionStatuses(rule.rule_uuid);

    // Set up an interval to periodically update the modal
    const updateInterval = setInterval(() => {
        if (activeModalRuleUuid === rule.rule_uuid) {
            updateModalActionStatuses(rule.rule_uuid);
        } else {
            clearInterval(updateInterval);
        }
    }, 1000); // Update every second

    // Function to close the modal
    const closeModal = () => {
        bootstrap_tap_to_run_modal_instance.hide();
        activeModalRuleUuid = null;
        clearInterval(updateInterval);
    };

    // Add event listener to close the modal when clicking outside
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    modal.addEventListener('hidden.bs.modal', ()=>{
         closeModal();
    })
    // Add event listener to close button
    // const closeButton = modal.querySelector('.close-button');
    // closeButton.addEventListener('click', closeModal);

    bootstrap_tap_to_run_modal_instance.show();

    // Send MQTT message to execute the scene
    mqttClient.publish(`v1/projects/${project_uuid}/homes/${home_uuid}/linkage-rules/${rule.rule_uuid}/actions/trigger/`, 'True');
}


// function subscribeToRuleActionTopics() {
//     linkage_rules.forEach(rule => {
//         rule.actions.forEach(action => {
//             const topic = `${rule.type}/${rule.rule_uuid}/action/${action.code}/status`;
//             eventBus.subscribe('ruleActions', topic, (message) => {
//                 updateActionStatus(rule.rule_uuid, action.code, message);
//             });
//         });
//     });
// }


function updateRuleStatus(ruleUuid, status) {
    const rule = linkage_rules.find(rule => rule.rule_uuid === ruleUuid);
    if (rule) {
        const card = document.querySelector(`.scene-rule-card[data-scene-automation-rule-id="${rule.index}"]`);
        if (card) {
            // const statusElement = card.querySelector('.little-text #status');
            // if (statusElement) {
            //     statusElement.textContent = status;
            // }

            const checkbox = card.querySelector('.checkbox');
            if (checkbox) {
                checkbox.checked = status === 'enable' || status === true;
            }

            // Update the switch label for visual feedback
            // const switchLabel = card.querySelector('.switch');
            // if (switchLabel) {
            //     if (status === 'on' || status === true) {
            //         switchLabel.classList.add('active');
            //     } else {
            //         switchLabel.classList.remove('active');
            //     }
            // }
        }
        if(status === "enable") {
            set_switch_color(rule, true);
        }
        else{
            set_switch_color(rule, false);
        }
    }
}

function updateActionStatus(ruleUuid, actionCode, status) {
    console.log(ruleUuid, actionCode, status)
    if (!ruleActionsStatus[ruleUuid]) {
        ruleActionsStatus[ruleUuid] = {};
    }
    ruleActionsStatus[ruleUuid][actionCode] = status;

    // If the modal for this rule is currently open, update it
    if (activeModalRuleUuid === ruleUuid) {
        updateModalActionStatuses(ruleUuid);
    }
}

function updateModalActionStatuses(ruleUuid) {
    const modal = document.querySelector('#tap-to-run-actions-status-modal');
    if (modal && activeModalRuleUuid === ruleUuid) {
        const actionStatuses = ruleActionsStatus[ruleUuid] || {};
        Object.entries(actionStatuses).forEach(([actionCode, status]) => {
            const actionItem = modal.querySelector(`[data-action-code="${actionCode}"]`);
            if (actionItem) {
                const statusIcon = actionItem.querySelector('.status-icon');
                if(status === "Pending"){
                    statusIcon.innerHTML = '<i class="fa-solid fa-loader fa-lg" style="color: #FFD43B;"></i>';
                }
                else if(status === "In Progress"){
                    statusIcon.innerHTML = '<i class="fa-solid fa-loader fa-spin fa-lg" style="color: #FFD43B;"></i>';
                }
                else if(status === "Completed"){
                    statusIcon.innerHTML = '<i class="fa-regular fa-circle-check fa-lg" style="color: #63E6BE;"></i>';
                }
            }
        });
    }
}

// Placeholder functions for MQTT operations
function sendMqttMessage(topic, message) {
    console.log(`Sending MQTT message to ${topic}: ${message}`);
    mqttClient.publish(topic, message);
}

function subscribeMqttTopic(topic, callback) {
    console.log(`Subscribing to MQTT topic: ${topic}`);
    eventBus.subscribe('ruleActions', topic, callback);
}




function setupRuleActionsSubscriptions(projectUuid, homeUuid) {
    const category = 'ruleActions';
    const topics = linkage_rules.flatMap(rule => [
        `v1/projects/${projectUuid}/homes/${homeUuid}/linkage-rules/${rule.rule_uuid}/status/set`,
        // `v1/projects/${projectUuid}/homes/${homeUuid}/linkage-rules/+/actions/create-new-rule-event`,
        ...rule.actions.map(action =>
            `v1/projects/${projectUuid}/homes/${homeUuid}/linkage-rules/${rule.rule_uuid}/actions/actions-status/${action.code}`
        )
    ]);

    eventBus.updateCategory(category, topics, (topic) => {
        return (message) => {
            console.log("in callback");
            const parts = topic.split('/');
            const ruleUuid = parts[6];
            if (parts[7] === 'status') {
                updateRuleStatus(ruleUuid, message);
            } else if (parts[7] === 'actions' && parts[8] === 'actions-status') {
                const actionCode = parts[9];
                updateActionStatus(ruleUuid, actionCode, message);
            }else if (parts[7] === 'actions' && parts[8] === 'create-new-rule-event') {
                // // Each home user only receives related rules topics because we set their authZ access to allow access
                // // to these topics. Therefore, if each user gets these messages, it's likely correct, but we're
                // // double-checking to ensure accuracy.
                // const matched_rule = linkage_rules.find(rule=> rule.rule_uuid === ruleUuid);
                // if (matched_rule){
                //
                //     generateRuleCards();
                // }

                console.log('Received change in linkage rules message:', message);
                get_linkage_rules().then(() => {
                    generateRuleCards();
                })
            }
        };
    });

    // Subscribe to MQTT topics
    // topics.forEach(topic => eventBus.subscribe(topic));
}


// Initial generation of rule cards
// document.addEventListener('DOMContentLoaded', () => {
//     generateRuleCards();
// });




