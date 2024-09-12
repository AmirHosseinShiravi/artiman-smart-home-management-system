// Usage example
const brokerUrl = `${mqtt_transport}://${mqtt_broker_host}:${mqtt_port}`;
const mqttClient = new MQTTClient(brokerUrl, {
    clientId: mqtt_client,
    username: mqtt_username,
    password: mqtt_password,
    path: mqtt_ws_path,
});


const eventBus = new EventBus(mqttClient);
mqttClient.setEventBus(eventBus);

// Connect to MQTT broker
mqttClient.connect();

// Example usage in a synchronous context
function setupSubscribe_to_new_rule_event_topic() {
    // Setup rule actions subscriptions
    const topic = `v1/projects/${project_uuid}/homes/${home_uuid}/linkage-rules/+/actions/create-new-rule-event`;
    eventBus.subscribe('change_in_home_linkage_rules', topic, (message) => {
        console.log('Received change in linkage rules message:', message);
        get_linkage_rules().then(() => {
            generateRuleCards();
        })
    });

    // Add more subscription setups as needed
}

function publishMessage() {
    mqttClient.publish('test/topic', 'Hello, MQTT!');
    console.log('Message published (or queued if not connected)');
}


// Call these functions as needed
//setupSubscriptions();
//publishMessage();

// When you're done, you can disconnect
// mqttClient.disconnect();
function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

async function get_linkage_rules() {
    try {
        const response = await fetch(`${linkage_rule_base_url}all/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCookie('csrftoken')  // Include CSRF token
            },
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Success:', result);
            if (result.status === "success") {
                linkage_rules = result.linkage_rules;
            }

        } else {
            console.error('Error:', response.status);
            // Handle error
        }
    } catch (error) {
        console.error('Error:', error);
        // Handle network error or other unexpected errors
    }
}

get_linkage_rules().then(() => {
    generateRuleCards();
})


setupSubscribe_to_new_rule_event_topic();


let scene_wizard_instance = null;

page('/web_app/v1/new-scene-wizard', () => {
    if (scene_wizard_instance !== null) {
        scene_wizard_instance.destroy();
    }
    scene_wizard_instance = null;
    scene_wizard_instance = new SceneWizardPageClass();
    scene_wizard_instance.render_scene_wizard_page();
    scene_wizard_instance.showPage('#scene-wizard-page');
});


page('/web_app/v1/scene-wizard', () => {
    scene_wizard_instance.showPage('#scene-wizard-page');
});

page('/web_app/v1/scene-wizard-device-selection-page', () => {
    scene_wizard_instance.showDeviceSelectionPage();
});


function dpf_comarasion_buttons_action(operator) {
    const selected_button = document.querySelector(`.comparison-buttons button[data-operator="${operator}"]`)
    const comparisonButtons = document.querySelectorAll('.comparison-buttons button');


    comparisonButtons.forEach(btn => {
        btn.classList.remove('active');
        btn.dataset.selectedStatus = "false";
    });
    selected_button.classList.add('active');
    selected_button.dataset.selectedStatus = "true";
    // You can add additional logic here to handle the comparison selection
    console.log('Selected operator:', this.dataset.operator);


}

function dpf_modal_range_input_show_value() {
    const rangeInput = document.getElementById('customRange');
    let currentValueDisplay = rangeInput.parentElement.querySelector('.current-value-display');
    currentValueDisplay.textContent = rangeInput.value;
}


document.addEventListener('DOMContentLoaded', () => {
    const myCurtainAnimation = new CurtainAnimation({
        curtainLeftSelector: '.curtain-left',
        curtainRightSelector: '.curtain-right',
        openButtonSelector: '#openButton',
        closeButtonSelector: '#closeButton',
        animationDuration: 5000, // 5 seconds
    });
    myCurtainAnimation.openProgress = 0.5;
    myCurtainAnimation.updateCurtainPosition();
});


document.addEventListener('DOMContentLoaded', () => {


    const thermostat_modla_themperature_knob = new TemperatureDial("#temp-display", "#temp-handle", "#dial-center", "#thermostat_modal_button");
});