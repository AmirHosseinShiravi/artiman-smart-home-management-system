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
})

zoneMenu();

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
        thermostatController.setupSubscriptions(thermostat);
    }
    if (uiElement.button_type === 'curtain') {
        const curtain = {
            ...uiElement,
            position: 0,
        };
        curtainController.addCurtain(curtain);
        curtainController.createCurtainCard(curtain);
        curtainController.setupSubscriptions(curtain);
    }
    if (uiElement.button_type === 'switch') {
        const switchButton = {
            ...uiElement,
            state: 'OFF',
        };
        switchButtonController.addSwitch(switchButton);
        switchButtonController.createSwitchCard(switchButton);
        switchButtonController.setupSubscriptions(switchButton);
    }
    if (uiElement.button_type === 'push_button') {
        const pushButton = {
            ...uiElement,
            state: 'OFF',
        };
        pushButtonController.addPushButton(pushButton);
        pushButtonController.createPushButtonCard(pushButton);
        pushButtonController.setupSubscriptions(pushButton);
    }
});


// function set_ui_card_texts_color(card) {
    
//         const card_color = card.style.color;
//         const hsl = tinycolor(card_color).toHsl(); // convert to HSL
//         // Calculate the brightness of the input color
//         const brightness = hsl.l * 255; // convert lightness to brightness (0-255)
//         // Adjust the lightness based on brightness
//         let newLightness;
//         if (brightness < 128) { // dark color
//           newLightness = Math.min(1, hsl.l + 0.6); // increase lightness for dark colors
//         } else { // light color
//           newLightness = Math.max(0, hsl.l - 0.9); // decrease lightness for light colors
//         }
//         const moreSaturatedHsl = {
//           h: hsl.h,
//           s: hsl.s,
//           l: newLightness
//         };
//         const new_color = tinycolor(moreSaturatedHsl).toHexString();

//         let card_element;

//         if(rule.type === "scene"){
//             card_element  = document.querySelector(`.scene-rule-card[data-scene-scene-rule-id="${rule.index}"]`);
//             card_element.querySelector('.icon-section i').style.color = new_color;
//             card_element.querySelector('.title-text').style.color = new_color;
//             card_element.querySelector('.edit-icon i').style.color = new_color;
//         }
//         else if (rule.type === "automation"){
//             card_element  = document.querySelector(`.scene-rule-card[data-scene-automation-rule-id="${rule.index}"]`);
//             card_element.querySelector('.icon-section i').style.color = new_color;
//             card_element.querySelector('.title-text').style.color = new_color;
//             card_element.querySelector('.edit-icon i').style.color = new_color;
//         }


// }
// function set_switch_color(rule, status) {
//     const switch_label = document.querySelector(`.scene-rule-card[data-scene-${rule.type}-rule-id="${rule.index}"] .rule-status-switch .switch`);
//     if(status){

//         const inputColor = rule.style.color;
//         const hsl = tinycolor(inputColor).toHsl(); // convert to HSL
//         const lightnessAdjustment = 0.4; // adjust lightness by 20%
//         const newLightness = Math.min(1, Math.max(0, hsl.l - lightnessAdjustment));
//         // clamp newLightness to [0, 1] range

//         const moreSaturatedHsl = {
//           h: hsl.h,
//           s: hsl.s,
//           l: newLightness
//         };
//         switch_label.style.backgroundColor = tinycolor(moreSaturatedHsl).toHexString();
//     }
//     else{
//         switch_label.style.backgroundColor = "#e9e9eb";
//     }
// }





// http: 192.168.65.150:8000 widget undefined


(function (d, s, id) {
    if (d.getElementById(id)) {
        if (window.__TOMORROW__) {
            window.__TOMORROW__.renderWidget();
        }
        return;
    }
    const fjs = d.getElementsByTagName(s)[0];
    const js = d.createElement(s);
    js.id = id;
    js.src = "https://www.tomorrow.io/v1/widget/sdk/sdk.bundle.min.js";

    fjs.parentNode.insertBefore(js, fjs);
})(document, 'script', 'tomorrow-sdk');


var remove_tomorrow_link_interval;

function remove_tomorrow_link() {
    var link = document.querySelector('.tomorrow a');
    if (link) {
        link.remove();
        clearInterval(remove_tomorrow_link_interval);
        remove_tomorrow_link_interval = setInterval(remove_tomorrow_link, 500);
    }
}

remove_tomorrow_link_interval = setInterval(remove_tomorrow_link, 100);


var remove_tomorrow_link_interval_2;

function remove_tomorrow_internal_link() {
    let iframe = document.querySelector(".tomorrow iframe");
    if (iframe) {

        let elmnt = iframe.contentWindow.document.getElementsByTagName("a");

        if (elmnt) {
            elmnt[0].href = "#";
            elmnt[0].target = "_top";
        }
    }
}

remove_tomorrow_link_interval_2 = setInterval(remove_tomorrow_internal_link, 1000);


let remove_tomorrow_boundary_color_interval;
let counter = 0;
function set_iframe_boundary_color() {

    let iframe = document.querySelector(".tomorrow iframe");
    if (iframe) {
        const html = iframe.contentWindow.document.querySelector('html');
        if(html) {
            const card = iframe.contentWindow.document.querySelector('.aqi-mini-widget__root--mIPT');
            const preferred_theme = localStorage.getItem('theme');
            console.log(preferred_theme)
            if (preferred_theme === 'dark') {
                html.style.backgroundColor = "#040a11";
                card.style.backgroundColor = "#0e1722";
            } else {
                html.style.backgroundColor = "#f6f8fb";
                card.style.backgroundColor = "#0e1722";

            }
            html.style.transition = "0.17s";
            counter = counter + 1;
            if(counter === 1000){
                clearInterval(remove_tomorrow_boundary_color_interval);
            }
        }
    }
}

remove_tomorrow_boundary_color_interval = setInterval(set_iframe_boundary_color, 10);





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