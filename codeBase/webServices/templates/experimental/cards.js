// Global variables
let linkage_rules = []; // Assume this is populated with your rules data
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
        } else if (rule.type === 'scene') {
            tapToRunSection.appendChild(card);
        }
    });

    // Reestablish event listeners
    setupEventListeners();

    // Subscribe to MQTT topics for rule actions
    subscribeToRuleActionTopics();
}

function createRuleCard(rule) {
    const card = document.createElement('div');
    card.className = 'col-12';
    card.innerHTML = `
        <div class="row scene-rule-card" data-scene-${rule.type}-rule-id="${rule.index}" style="background-color: ${rule.style.color}">
            <div class="col-9 scene-rule-card-detail-section">
                <div class="icon-section d-flex align-items-end">
                    ${rule.style.icon ? `<i class="${rule.style.icon}"></i>` : ''}
                </div>
                <div class="text-section">
                    <div class="big-text">${rule.name}</div>
                    <div class="little-text"><span id="status">${getConditionsSummary(rule)}</span></div>
                </div>
            </div>
            <div class="col-3 d-flex justify-content-end scene-rule-card-action-section">
                <div class="d-flex flex-column">
                    <div class="edit-icon" data-rule-index="${rule.index}" data-rule-type="${rule.type}">
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

function getConditionsSummary(rule) {
    // Implement logic to summarize conditions and actions
    return "Conditions and actions summary";
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
    document.querySelectorAll('.scene-tap-to-run-rules-section .scene-rule-card').forEach(card => {
        card.addEventListener('click', handleTapToRunClick);
    });
}

function removeAllEventListeners() {
    // Implement logic to remove all event listeners
    // This might involve cloning and replacing elements
}

function handleEditClick(event) {
    const ruleIndex = event.currentTarget.dataset.ruleIndex;
    const ruleType = event.currentTarget.dataset.ruleType;
    // Implement edit functionality
    console.log(`Edit ${ruleType} rule with index ${ruleIndex}`);
}

function handleAutomationStatusChange(event) {
    const ruleIndex = event.target.id.split('-')[1];
    const newStatus = event.target.checked;
    // Update rule status in linkage_rules
    const rule = linkage_rules.find(r => r.index == ruleIndex && r.type === 'automation');
    if (rule) {
        rule.status = newStatus;
        // Send MQTT message
        sendMqttMessage(`automation/${rule.rule_uuid}/status`, newStatus ? 'on' : 'off');
    }
}

function handleTapToRunClick(event) {
    const ruleIndex = event.currentTarget.dataset.sceneTapToRunRuleId;
    const rule = linkage_rules.find(r => r.index == ruleIndex && r.type === 'scene');
    if (rule) {
        showActionsModal(rule);
    }
}

function showActionsModal(rule) {
    // Create and show modal with actions list
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>${rule.name} Actions</h2>
            <ul class="actions-list">
                ${rule.actions.map(action => `
                    <li data-action-code="${action.code}">
                        ${action.executor_property.function_code}: ${action.executor_property.function_value}
                        <span class="status-icon">⏳</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;
    document.body.appendChild(modal);

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
        modal.remove();
        activeModalRuleUuid = null;
        clearInterval(updateInterval);
    };

    // Add event listener to close the modal when clicking outside
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Add event listener to close button
    const closeButton = modal.querySelector('.close-button');
    closeButton.addEventListener('click', closeModal);


    // Send MQTT message to execute the scene
    sendMqttMessage(`scene/${rule.rule_uuid}/execute`, 'true');
}


function subscribeToRuleActionTopics() {
    linkage_rules.forEach(rule => {
        rule.actions.forEach(action => {
            const topic = `${rule.type}/${rule.rule_uuid}/action/${action.code}/status`;
            subscribeMqttTopic(topic, (message) => {
                updateActionStatus(rule.rule_uuid, action.code, message);
            });
        });
    });
}

function updateActionStatus(ruleUuid, actionCode, status) {
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
    const modal = document.querySelector('.modal');
    if (modal && activeModalRuleUuid === ruleUuid) {
        const actionStatuses = ruleActionsStatus[ruleUuid] || {};
        Object.entries(actionStatuses).forEach(([actionCode, status]) => {
            const actionItem = modal.querySelector(`[data-action-code="${actionCode}"]`);
            if (actionItem) {
                const statusIcon = actionItem.querySelector('.status-icon');
                statusIcon.textContent = status === 'done' ? '✅' : '⏳';
            }
        });
    }
}

// Placeholder functions for MQTT operations
function sendMqttMessage(topic, message) {
    console.log(`Sending MQTT message to ${topic}: ${message}`);
    // Implement actual MQTT sending logic
}

function subscribeMqttTopic(topic, callback) {
    console.log(`Subscribing to MQTT topic: ${topic}`);
    // Implement actual MQTT subscription logic
}

// Initial generation of rule cards
generateRuleCards();