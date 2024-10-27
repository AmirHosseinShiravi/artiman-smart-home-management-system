
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






function updateDateTime() {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

    const now = new Date();
    const day = days[now.getDay()];
    const date = now.getDate();
    const month = months[now.getMonth()];
    const time = now.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
    const isWeekend = now.getDay() === 0 || now.getDay() === 6;

    // document.getElementById('weekend').textContent = isWeekend ? 'Weekend' : '';
    document.getElementById('day').textContent = `${day}, ${date} ${month}`;
    document.getElementById('time').textContent = time;
}
    
// Update every second
setInterval(updateDateTime, 1000);

// Initial update
updateDateTime();






// Example usage in a synchronous context
function setupSubscribe_to_new_rule_event_topic() {
    // Setup rule actions subscriptions
    const topic = `v1/projects/${project_uuid}/homes/${home_uuid}/linkage-rules/+/actions/create-new-rule-event`;
    eventBus.subscribe('change_in_home_linkage_rules', topic, (message) => {
        console.log('Received change in linkage rules message:', message);
        get_linkage_rules().then(() => {
            generateRuleCards();
            add_tap_to_run_rules_to_selected_zones();
        })
    });

    // Add more subscription setups as needed
}


function subscribe_to_controller_will_topic() {
    all_home_controllers.forEach(controller => {
        const topic = `v1/controllers/${controller.controller_uuid}/status`;
        eventBus.subscribe('home_controller_status_topics', topic, (message) => {
            console.log('Received controller will topic message :: controller_uuid : ', controller.controller_uuid, ' :: message:  ', message);
            if(message === "enable"){
                controller.status = "enable";
                const controller_status_icon = document.getElementById(`controller-status-icon-${controller.controller_uuid}`);
                controller_status_icon.classList.remove('fa-solid', 'fa-signal-bars-slash');
                controller_status_icon.classList.add('fa-solid', 'fa-signal-bars');
                controller_status_icon.style.color = "#63E6BE";
            }
            else if(message === "disable"){
                controller.status = "disable";
                const controller_status_icon = document.getElementById(`controller-status-icon-${controller.controller_uuid}`);
                controller_status_icon.classList.remove('fa-solid', 'fa-signal-bars');
                controller_status_icon.classList.add('fa-solid', 'fa-signal-bars-slash');
                controller_status_icon.style.color = "#FF6B6B";
            }

        });
    });

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
    add_tap_to_run_rules_to_selected_zones();
    // I want the rule cards to be generated first and then generate ui elements. rule card should be placed in first grid cell.
    generateUiElementCards();
})

zoneMenu();

function add_tap_to_run_rules_to_selected_zones(){

    const all_tap_to_run_rules_with_add_to_zones = linkage_rules.filter(rule => rule.hasOwnProperty("show_scene_rule_in_zones") && rule.show_scene_rule_in_zones.length != 0 && rule.type === "scene");
    if(all_tap_to_run_rules_with_add_to_zones){
        all_home_zones.forEach(zone=>{
            const rule_linkage_rule_container = document.querySelector(`.content[data-menu-content-zone="${zone.zone_uuid}"] .zone-linkage-rule-container`);
            if (rule_linkage_rule_container){
                rule_linkage_rule_container.remove();
            }
            let atleast_one_rule_card_added_to_this_zone = false;
            const correspond_zone_content_element = document.querySelector(`.content[data-menu-content-zone="${zone.zone_uuid}"]`);
            const rule_cointainer = document.createElement("div");
            rule_cointainer.classList.add("zone-linkage-rule-container");
            rule_cointainer.style.gridRow = "span 1";
            rule_cointainer.style.overflowY = "scroll";
            rule_cointainer.style.overflowX = "hidden";
            rule_cointainer.style.maxHeight = "260px";
            rule_cointainer.style.marginRight = "-4px";
        
            const row_element = document.createElement("div");
            row_element.classList.add("row");

            all_tap_to_run_rules_with_add_to_zones.forEach(rule => {
                rule.show_scene_rule_in_zones.forEach(selected_zone=>{
                    
                    // check if selected zone is available or not
                    if (zone.zone_uuid === selected_zone) {
                        atleast_one_rule_card_added_to_this_zone = true;                    
                        const tap_to_run_card_element = document.createElement("div");
                        tap_to_run_card_element.classList.add("col-12");
                        tap_to_run_card_element.dataset.sceneSceneRuleId = rule.index;
                        // tap_to_run_card_element.style.paddingBottom = "8px";
                        const inputColor = rule.style.color;
                        const hsl = tinycolor(inputColor).toHsl(); // convert to HSL
                        // Calculate the brightness of the input color
                        const brightness = hsl.l * 255; // convert lightness to brightness (0-255)
                        // Adjust the lightness based on brightness
                        let newLightness;
                        if (brightness < 128) { // dark color
                        newLightness = Math.min(1, hsl.l + 0.6); // increase lightness for dark colors
                        } else { // light color
                        newLightness = Math.max(0, hsl.l - 0.9); // decrease lightness for light colors
                        }
                        const moreSaturatedHsl = {
                        h: hsl.h,
                        s: hsl.s,
                        l: newLightness
                        };
                        tap_to_run_card_element.innerHTML = `<div class="row zone-scene-rule-card" style="background-color: ${rule.style.color};height:120px;">
                                                                <div class="col-6" style="display: flex;justify-content: start;align-items: center;margin-top: 9px;">
                                                                    <div class="text-section">
                                                                        <div class="title-text" style="color: ${tinycolor(moreSaturatedHsl).toHexString()};">${rule.name}</div>
                                                                    </div>
                                                                </div>
                                                                <div class="col-6" style="display: flex;justify-content: flex-end;padding-right:20px;">
                                                                        <div class="icon-section" style="width:70px!important">
                                                                            <i class="fa-solid fa-wand-magic-sparkles" style="color: ${tinycolor(moreSaturatedHsl).toHexString()};"></i>
                                                                        </div>
                                                                </div>
                        </div>`;
    
                        tap_to_run_card_element.addEventListener('click', handleMainPageTapToRunButtonClick);
                        row_element.appendChild(tap_to_run_card_element);   
                    }
    
                })
            })
            rule_cointainer.appendChild(row_element);
            if(atleast_one_rule_card_added_to_this_zone){
            correspond_zone_content_element.prepend(rule_cointainer);
            }
            
        })
        
    }
    
}




setupSubscribe_to_new_rule_event_topic();

subscribe_to_controller_will_topic();



function showPage(page_query) {

    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active-page');
    });

    // Show the selected page
    const page = document.querySelector(page_query);
    if (page) {
        page.classList.add('active-page');
    }
    return false;
}


// page.base("/web_app/v1");
page('/web_app/v1/home', () => {
    showPage('.home-page');
    activateNavButton('home-page');
});
page('/web_app/v1/devices', () => {
    showPage('.devices-page');
    activateNavButton('devices-page');
});
page('/web_app/v1/scene', () => {
    showPage('.scene-page');
    activateNavButton('scene-page');
});
page('/web_app/v1/setting', () => {
    showPage('.setting-page');
    activateNavButton('setting-page');
});

page('/web_app/v1/edit-profile', () => {
    get_edit_profile_page();
    showPage('.edit-profile-page');
    activateNavButton('setting-page');
});

page({
    click: true, // intercepts clicks on <a> tags
    popstate: true, // handles browser back/forward buttons
});




let scene_wizard_instance = SceneWizardPageClass.getInstance();

page('/web_app/v1/new-scene-wizard', () => {

    scene_wizard_instance.render_scene_wizard_page();
    scene_wizard_instance.showPage('#scene-wizard-page');
});


page('/web_app/v1/scene-wizard', () => {
    scene_wizard_instance.showPage('#scene-wizard-page');
});

page('/web_app/v1/scene-wizard-device-selection-page', () => {
    scene_wizard_instance.showDeviceSelectionPage();
});


console.log("after page")


// Get all elements with the class 'menu-button'
function activateNavButton(nav_button_data_page) {
    var navButtons = document.querySelectorAll('.nav-button');
    
    // Remove 'active' class from all nav buttons
    navButtons.forEach(button => {
        button.classList.remove('active');
    });

    // Get the data-page value of the clicked button
    var pageToShow = document.querySelector('[data-page="'+nav_button_data_page+'"]');
    pageToShow.classList.add('active');

}





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


// document.addEventListener('DOMContentLoaded', () => {
//     const myCurtainAnimation = new CurtainAnimation({
//         curtainLeftSelector: '.curtain-left',
//         curtainRightSelector: '.curtain-right',
//         openButtonSelector: '#openButton',
//         closeButtonSelector: '#closeButton',
//         animationDuration: 5000, // 5 seconds
//     });
//     myCurtainAnimation.openProgress = 0.5;
//     myCurtainAnimation.updateCurtainPosition();
// });


// document.addEventListener('DOMContentLoaded', () => {


//     const thermostat_modla_themperature_knob = new TemperatureDial("#temp-display", "#temp-handle", "#dial-center", "#thermostat_modal_button");
// });


function generateUiElementCards(){

    const thermostatController = new ThermostatController(eventBus, mqttClient);
    const curtainController = new CurtainController(eventBus, mqttClient);
    const switchButtonController = new SwitchButtonController(eventBus, mqttClient);
    const pushButtonController = new PushButtonController(eventBus, mqttClient);


    all_home_ui_elements.forEach(uiElement => {
        if (uiElement.button_type === 'thermostat') {
            const thermostat = {
                ...uiElement,
                currentTemp: 25,
                targetTemp: 22,
                status: "OFF",
                operationMode: 'Heat',
                fanSpeed: 'Auto',
                fanControlMode: 'Auto',
            };
            thermostatController.addThermostat(thermostat);
            thermostatController.createThermostatCardForHomePage(thermostat);
            thermostatController.setupSubscriptions(thermostat);
        }
        if (uiElement.button_type === 'curtain') {
            const curtain = {
                ...uiElement,
                position: 0,
            };
            curtainController.addCurtain(curtain);
            curtainController.createCurtainCard(curtain);
            curtainController.createCurtainCardForHomePage(curtain);
            curtainController.setupSubscriptions(curtain);
        }
        if (uiElement.button_type === 'switch') {
            const switchButton = {
                ...uiElement,
                state: 'OFF',
            };
            switchButtonController.addSwitch(switchButton);
            switchButtonController.createSwitchCard(switchButton);
            switchButtonController.createSwitchCardForHomePage(switchButton);
            switchButtonController.setupSubscriptions(switchButton);
        }
        if (uiElement.button_type === 'push_button') {
            const pushButton = {
                ...uiElement,
                state: 'OFF',
            };
            pushButtonController.addPushButton(pushButton);
            pushButtonController.createPushButtonCard(pushButton);
            pushButtonController.createPushButtonCardForHomePage(pushButton);
            pushButtonController.setupSubscriptions(pushButton);
        }
    });

}








document.getElementById('logout-link').addEventListener('click', function(e) {
    e.preventDefault();
    
    // Close MQTT connection
    if (mqttClient && mqttClient.isConnected) {
      mqttClient.disconnect();
      console.log('MQTT connection closed');
      // Proceed with logout
      window.location.href = logout_url;
    } else {
      // If MQTT is not connected, proceed with logout directly
      window.location.href = logout_url;
    }
  });


function get_edit_profile_page() {
    fetch(edit_profile_url)
    .then(response => response.json())
    .then(data => {
      const editProfilePage = document.getElementById("edit-profile-page");
      editProfilePage.innerHTML = data.html;
      initializeAvatarPreview();
    });
}

get_edit_profile_page();

function save_profile() {
  const form_element = document.getElementById("edit-profile-form");
  const formData = new FormData(form_element);
  

  fetch(edit_profile_url, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie('csrftoken')
    },
    body: formData,
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === "success") {
      window.location.href = "/web_app/v1/setting";
    } else {
      console.error('Error:', data.message);
      const errorMessage = document.getElementById("error-message");
      errorMessage.innerHTML = data.message;
    }
  });
}


function initializeAvatarPreview() {
    const avatarInput = document.getElementById("id_avatar");
    if (avatarInput) {

      avatarInput.addEventListener("change", function(event) {
        console.log("change");
        var image = document.getElementById('avatar_preview');
        if (image) {
          image.style.backgroundImage = "url(" + URL.createObjectURL(event.target.files[0]) + ")";
        }
      });
    }
  }
