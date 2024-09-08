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
    var iframe = document.querySelector(".tomorrow iframe");
    var elmnt = iframe.contentWindow.document.getElementsByTagName("a");

    if (elmnt) {
        elmnt[0].href = "#";
        elmnt[0].target = "_top";
    }
}

remove_tomorrow_link_interval_2 = setInterval(remove_tomorrow_internal_link, 10000);


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
// setInterval(updateDateTime, 1000);

// Initial update
// updateDateTime();


// document.addEventListener('DOMContentLoaded', function () {
//            var header_container_height = document.getElementsByClassName('header-container')[0].offsetHeight;
//            var menu_container_height = document.getElementsByClassName('zones-menu-container')[0].offsetHeight;
//            var scene_container_height = document.getElementsByClassName('scene-container')[0].offsetHeight;
//            var bottom_navbar_container_height = document.getElementsByClassName('bottom-navbar-container')[0].offsetHeight;
//
//            var content_container_element = document.getElementsByClassName('zone-content-container')[0];
//
//            // Calculate the height of the adjusted div
//            var windowHeight = window.innerHeight;
//            // sub 20px to separate zone-content-container from bottom-navbar-container
//            var content_container_height = windowHeight - header_container_height - menu_container_height - bottom_navbar_container_height - scene_container_height - 35;
//
//            // Set the height of the adjusted div
//            content_container_element.style.maxHeight = content_container_height + 'px';
//
//            var bottom_navbar_container_height = document.getElementsByClassName('bottom-navbar-container')[0].offsetHeight;
//            var header_container_height = document.getElementsByClassName('container-fluid')[0];
//            var aaaa = header_container_height.offsetHeight + bottom_navbar_container_height
//            header_container_height.style.marginBottom = bottom_navbar_container_height.toString() + 'px'
//            // Calculate the height of the adjusted div
//            var windowHeight = window.innerHeight;
//
//
//        });



// Capture console messages
//         var consoleLogContainer = document.getElementById('consoleLog');
//
//         function captureConsoleLog() {
//             var originalConsoleLog = console.log;
//             var originalConsoleError = console.error;
//
//             console.log = function (message) {
//                 // Call the original console.log
//                 originalConsoleLog.apply(console, arguments);
//
//                 // Append the message to the container
//                 var logMessage = document.createElement('div');
//                 logMessage.textContent = message;
//                 consoleLogContainer.appendChild(logMessage);
//             };
//
//             // console.error = function (message) {
//             //     // Call the original console.log
//             //     originalConsoleError.apply(console, arguments);
//
//             //     // Append the message to the container
//             //     var logMessage = document.createElement('div');
//             //     logMessage.textContent = message;
//             //     consoleLogContainer.appendChild(logMessage);
//             // };
//         };
//
//         // Call the function to capture console.log
//         captureConsoleLog();
//
//         // Example console.log statements
//         console.log('This is a console log message.');
//         console.log('Another console log message.');
//



// document.addEventListener('DOMContentLoaded', function () {
//
//       const fanButton = document.getElementById('fanButton');
//       const autoButton = document.getElementById('autoButton');
//       const typeButton = document.getElementById('typeButton');
//       // const fanBadge = document.getElementById('fanBadge');
//       const fanStateElement = document.getElementById('fanState');
//       const autoStateElement = document.getElementById('autoState');
//       const typeStateElement = document.getElementById('typeState');
//
//       const fanStates = ['سرعت کم', 'سرعت متوسط', 'سرعت زیاد'];
//       const autoStates = ['اتوماتیک', 'دستی'];
//       const typeStates = ['سرمایش', 'گرمایش'];
//
//       var fancurrentState = 0;
//       var autocurrentState = 0;
//       var typecurrentState = 0;
//
//       fanButton.addEventListener('click', function () {
//         fancurrentState = (fancurrentState + 1) % fanStates.length;
//         fanStateElement.textContent = fanStates[fancurrentState];
//         //   fanBadge.textContent = fanStates[fancurrentState];
//
//         // Update button class for 'Fan Off' state
//         // if (fancurrentState === 0) {
//         //   fanButton.classList.add('fan-off');
//         // } else {
//         //   fanButton.classList.remove('fan-off');
//         // }
//       });
//
//
//       const autoIconElement = document.getElementById('auto-icon');
//       const manualIconElement = document.getElementById('manual-icon');
//       autoButton.addEventListener('click', function () {
//         autocurrentState = (autocurrentState + 1) % autoStates.length;
//         autoStateElement.textContent = autoStates[autocurrentState];
//         //   fanBadge.textContent = fanStates[autocurrentState];
//
//         // Update button class for 'Fan Off' state
//         // if (autocurrentState === 0) {
//         //   autoButton.classList.add('fan-off');
//         // } else {
//         //   autoButton.classList.remove('fan-off');
//         // }
//         if (autocurrentState === 0) {
//           autoIconElement.style.display = 'block';
//           manualIconElement.style.display = 'none';
//         } else {
//           autoIconElement.style.display = 'none';
//           manualIconElement.style.display = 'block';
//         }
//       });
//
//       const heatIconElement = document.getElementById('heat-icon');
//       const coolIconElement = document.getElementById('cool-icon');
//       typeButton.addEventListener('click', function () {
//         typecurrentState = (typecurrentState + 1) % typeStates.length;
//         typeStateElement.textContent = typeStates[typecurrentState];
//         //   fanBadge.textContent = fanStates[typecurrentState];
//
//         // Update button class for 'Fan Off' state
//         if (typecurrentState === 0) {
//           heatIconElement.style.display = 'none';
//           coolIconElement.style.display = 'block';
//
//         } else {
//           heatIconElement.style.display = 'block';
//           coolIconElement.style.display = 'none';
//         }
//       });
//
//     });




// document.addEventListener('DOMContentLoaded', function () {
//
//         // Get all elements with the class 'custom-card'
//         const customCards = document.querySelectorAll('.custom-card');
//
//         // Add a click event listener to each custom-card element
//         customCards.forEach(card => {
//             card.addEventListener('click', () => {
//                 // Toggle the 'active' class for the clicked custom-card element
//                 card.classList.toggle('active');
//                 // document.getElementById('amir').innerHTML= 'fdfdff';
//                 // alert('gfgfgfg');
//             });
//         });
//
//         // Get all elements with the class 'custom-card'
//         const menu_buttons = document.querySelectorAll('.menu-button');
//
//         // Add a click event listener to each custom-card element
//         menu_buttons.forEach(button => {
//             button.addEventListener('click', () => {
//                 menu_buttons.forEach(c => c.classList.remove('active'));
//                 // Toggle the 'active' class for the clicked custom-button element
//                 button.classList.toggle('active');
//
//                 var clicked_menu_button_index = button.getAttribute("data-menu-button");
//                 var all_content = document.querySelectorAll(".content");
//                 all_content.forEach(content_block =>{
//                     content_block.style.display = "none";
//                 })
//                 var relevant_content = document.querySelector('[data-menu-content="' + clicked_menu_button_index.toString() + '"]');
//                 relevant_content.style.display = "flex";
//
//
//                 console.log(button);
//             });
//         });
//
//     });


var global_lock_acquired = 0
document.addEventListener('DOMContentLoaded', function () {

    // const BASE_URL = "http://127.0.0.1:8080";

    // const BASE_URL = "http://192.168.50.232:8080";
    const BASE_URL = "http://192.168.18.232:9000/controller";

    // const BASE_URL = "http://192.168.1.3:8080";
    var get_switchs_state_interval;
    var garden_valve_get_interval;
    var get_interval_ms = 500;


    var start_get_command;

    var menu_switch_ids = {
        '1': ['13'],
        '2': ['10', '36'],
        '3': ['11'],
        '4': ['34', '12'],
        '5': ['33', '22'],
        '6': ['31', '21'],
        '7': ['30', '20'],
        '8': ['35'],
        '9': ['xxx'],
        '10': [''],
    }


    var switchs_data = {
        '13': {
            '5': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
            '8': {'created_by': '', 'created_at': new Date().getTime()},
            '9': {'created_by': '', 'created_at': new Date().getTime()},
            '10': {'created_by': '', 'created_at': new Date().getTime()}
        },
        '10': {
            '5': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
            '8': {'created_by': '', 'created_at': new Date().getTime()},
            '9': {'created_by': '', 'created_at': new Date().getTime()},
            '10': {'created_by': '', 'created_at': new Date().getTime()}
        },
        '36': {
            '1': {'created_by': '', 'created_at': new Date().getTime()},
            '2': {'created_by': '', 'created_at': new Date().getTime()},
            '4': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()}
        },
        '11': {
            '5': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
            '8': {'created_by': '', 'created_at': new Date().getTime()},
            '9': {'created_by': '', 'created_at': new Date().getTime()},
            '10': {'created_by': '', 'created_at': new Date().getTime()}
        },
        '12': {
            '5': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
            '8': {'created_by': '', 'created_at': new Date().getTime()},
            '9': {'created_by': '', 'created_at': new Date().getTime()},
            '10': {'created_by': '', 'created_at': new Date().getTime()}
        },
        '33': {
            '1': {'created_by': '', 'created_at': new Date().getTime()},
            '2': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
        },
        '31': {
            '1': {'created_by': '', 'created_at': new Date().getTime()},
            '2': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
        },
        '30': {
            '1': {'created_by': '', 'created_at': new Date().getTime()},
            '2': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
        },
        '35': {
            '1': {'created_by': '', 'created_at': new Date().getTime()},
            '2': {'created_by': '', 'created_at': new Date().getTime()},
            '6': {'created_by': '', 'created_at': new Date().getTime()},
            '7': {'created_by': '', 'created_at': new Date().getTime()},
        }
    }


    thermostats_data = {
        '13': {
            'currentTemperature': 0,
            'targetTemperature': 0,
            'fanManualSpeed': 0,
            'fanControlMode': 0,
            'heat_cool_mode': 0
        },
        '10': {
            'currentTemperature': 0,
            'targetTemperature': 0,
            'fanManualSpeed': 0,
            'fanControlMode': 0,
            'heat_cool_mode': 0
        },
        '11': {
            'currentTemperature': 0,
            'targetTemperature': 0,
            'fanManualSpeed': 0,
            'fanControlMode': 0,
            'heat_cool_mode': 0
        },
        '12': {
            'currentTemperature': 0,
            'targetTemperature': 0,
            'fanManualSpeed': 0,
            'fanControlMode': 0,
            'heat_cool_mode': 0
        },


        '22': {
            'currentTemperature': 0,
            'targetTemperature': 0,
            'fanManualSpeed': 0,
            'fanControlMode': 0,
            'heat_cool_mode': 0
        },
        '21': {
            'currentTemperature': 0,
            'targetTemperature': 0,
            'fanManualSpeed': 0,
            'fanControlMode': 0,
            'heat_cool_mode': 0
        },
        '20': {
            'currentTemperature': 0,
            'targetTemperature': 0,
            'fanManualSpeed': 0,
            'fanControlMode': 0,
            'heat_cool_mode': 0
        }
    }


    function createRequestQueue(maxQueueSize) {
        const queue = [];
        var isProcessing = false;

        function processQueue() {
            if (!isProcessing && queue.length > 0) {
                isProcessing = true;
                //   const { method, url, data, callback, retries, timeout, extraVariables } = queue.shift();
                const queuedItem = queue.shift();
                const method = queuedItem.method;
                const url = queuedItem.url;
                const data = queuedItem.data;
                const callback = queuedItem.callback;
                const retries = queuedItem.retries;
                const timeout = queuedItem.timeout;
                const extraVariables = queuedItem.extraVariables;

                const xhr = new XMLHttpRequest();
                xhr.open(method, url, true);
                xhr.timeout = timeout;

                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4) {
                        // Request completed
                        isProcessing = false;
                        processQueue(); // Process the next request in the queue
                    }
                };

                xhr.onload = function () {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        callback(null, xhr.responseText, extraVariables);
                    } else {
                        if (retries > 0) {
                            // Retry the request
                            console.warn(`Retrying request to ${url}. Remaining retries: ${retries}`);
                            queue.unshift({method, url, data, callback, retries: retries - 1, timeout, extraVariables});
                        } else {
                            callback(new Error(`Request failed with status ${xhr.status}`), null, extraVariables);
                        }
                    }

                    processQueue(); // Process the next request in the queue
                };

                xhr.onerror = function () {
                    if (retries > 0) {
                        // Retry the request
                        console.warn(`Retrying request to ${url}.amir :) Remaining retries: ${retries}`);
                        queue.unshift({method, url, data, callback, retries: retries - 1, timeout, extraVariables});
                    } else {
                        callback(new Error('Network error'), null, extraVariables);
                    }

                    processQueue(); // Process the next request in the queue
                };

                xhr.ontimeout = function () {
                    if (retries > 0) {
                        // Retry the request
                        console.warn(`Retrying request to ${url} due to timeout. Remaining retries: ${retries}`);
                        queue.unshift({method, url, data, callback, retries: retries - 1, timeout, extraVariables});
                    } else {
                        callback(new Error('Request timeout'), null, extraVariables);
                    }

                    processQueue(); // Process the next request in the queue
                };

                if (method === 'POST') {
                    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                    const formData = serializeFormData(data);
                    console.log("---------- :: QUEUE :: send request body :: " + formData + "-----------")
                    xhr.send(formData);
                } else {
                    xhr.send();
                }
            }
            updateQueueIndicator(); // Update the queue indicator
        }

        function serializeFormData(data) {
            var encodedData = [];
            for (var key in data) {
                if (data.hasOwnProperty(key) && data[key] !== undefined) {
                    encodedData.push(encodeURIComponent(key) + '=' + encodeURIComponent(data[key]));
                }
            }
            return encodedData.join('&');
        }


        function removeOldGetRequests() {
            for (var i = queue.length - 1; i >= 0; i--) {
                if (queue[i].method === 'GET') {
                    queue.splice(i, 1);
                    break; // Remove only one old GET request
                }
            }
        }

        function getQueueSize() {
            return queue.length;
        }

        function updateQueueIndicator() {
            const indicatorElement = document.getElementById('queue-indicator');
            if (indicatorElement) {
                indicatorElement.innerText = `Queue Size: ${getQueueSize()}`;
            }
        }

        return {
            enqueue: function (method, url, data, callback, retries, timeout, extraVariables) {
                retries = typeof retries !== 'undefined' ? retries : 3;
                timeout = typeof timeout !== 'undefined' ? timeout : 5000;
                extraVariables = typeof extraVariables !== 'undefined' ? extraVariables : null;

                if (method === 'POST') {
                    // Add all POST requests to the start of the queue
                    queue.unshift({
                        method: method,
                        url: url,
                        data: data,
                        callback: callback,
                        retries: retries,
                        timeout: timeout,
                        extraVariables: extraVariables
                    });
                } else {
                    // For non-POST requests, check if the queue size exceeds the limit
                    if (getQueueSize() >= maxQueueSize) {
                        // Remove old GET requests to make room for the new one
                        removeOldGetRequests();
                    }
                    // For non-POST requests, add them to the end of the queue
                    queue.push({
                        method: method,
                        url: url,
                        data: data,
                        callback: callback,
                        retries: retries,
                        timeout: timeout,
                        extraVariables: extraVariables
                    });
                }

                // Continue processing the queue
                processQueue();
            },
            processQueue: processQueue,
            getQueueSize: getQueueSize // Provide access to the getQueueSize function
        };

    }

    // max queue size of 10
    const requestQueue = createRequestQueue(10);

    // Function to make a GET request
    function makeGetRequest(url, callback, retries, timeout, extraVariables) {
        retries = typeof retries !== 'undefined' ? retries : 0;
        timeout = typeof timeout !== 'undefined' ? timeout : 5000;
        extraVariables = typeof extraVariables !== 'undefined' ? extraVariables : null;

        requestQueue.enqueue('GET', url, null, callback, retries, timeout, extraVariables);
    }

    // Function to make a POST request with higher priority
    function makePriorityPostRequest(url, data, callback, retries, timeout, extraVariables) {
        retries = typeof retries !== 'undefined' ? retries : 10;
        timeout = typeof timeout !== 'undefined' ? timeout : 5000;
        extraVariables = typeof extraVariables !== 'undefined' ? extraVariables : null;

        // Add the POST request to the start of the queue
        requestQueue.enqueue('POST', url, data, function (error, response, extras) {
            callback(error, response, extras);
            // Process the next request in the queue
            requestQueue.processQueue();
        }, retries, timeout, extraVariables);
    }


    // Get all elements with the class 'custom-card'


    var modal = document.getElementById('thermostat-modal');
    var overlay = document.getElementById('overlay');
    var updateThermostatModalValuesBeforeFirstUserInteraction_timer;
    overlay.addEventListener('click', function (event) {
        // Check if the click is outside the modal
        if (!modal.contains(event.target)) {
            // Close the modal and overlay
            modal.style.display = 'none';
            overlay.style.display = 'none';
        }
    });


    var customCards = document.querySelectorAll('.custom-card');

    // Add a click event listener to each custom-card element
    for (var i = 0; i < customCards.length; i++) {
        customCards[i].addEventListener('click', function () {
            // Toggle the 'active' class for the clicked custom-card element
            var switch_id = this.getAttribute('data-switch-id');
            var switch_contact_id = this.getAttribute('data-switch-contact-id');
            var switch_contact_value = this.getAttribute('data-switch-contact-value');
            var switch_type = this.getAttribute('data-switch-type');

            if (!this.hasAttribute('data-is-thermostat-button')) {

                change_button_status(this);

                // Send data to the server
                sendToServer(switch_id, switch_contact_id, switch_contact_value);

                switchs_data[switch_id][switch_contact_id]['created_by'] = 'user';
                switchs_data[switch_id][switch_contact_id]['created_at'] = new Date().getTime();
            } else {
                // clicked button is thermostat
                modal.style.display = 'block';
                overlay.style.display = 'block';
                initThermostatModal(switch_id);
                clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
                updateThermostatModalValuesBeforeFirstUserInteraction_timer = setInterval(function () {
                    updateThermostatModalValuesBeforeFirstUserInteraction(switch_id);
                }, 500);
            }
        });
    }


    var garden_button = document.querySelector('.garden-valve');

    // Add a click event listener to each custom-card element

    garden_button.addEventListener('click', function () {
        // Toggle the 'active' class for the clicked custom-card element

        change_button_status(this);
        var element = this;
        // Send data to the server
        // var switch_id = this.getAttribute('data-switch-id');
        // var switch_contact_id = this.getAttribute('data-switch-contact-id');
        var switch_contact_value = this.getAttribute('data-switch-contact-value');
        sendToServer_garden_valve(switch_contact_value);
        // setTimeout(function() {
        //     change_button_status(element);
        // }, 1000);
    });


    // var turn_off_button = document.querySelector('.turn_off_home_automation');
    //
    // // Add a click event listener to each custom-card element
    //
    // turn_off_button.addEventListener('click', function () {
    //     // Toggle the 'active' class for the clicked custom-card element
    //
    //     change_button_status(this);
    //     var element = this;
    //     // Send data to the server
    //     // var switch_id = this.getAttribute('data-switch-id');
    //     // var switch_contact_id = this.getAttribute('data-switch-contact-id');
    //     var switch_contact_value = this.getAttribute('data-switch-contact-value');
    //     sendToServer_turn_off_home_automation(switch_contact_value);
    //     // setTimeout(function() {
    //     //     change_button_status(element);
    //     // }, 1000);
    // });


    function change_button_status(parameter) {
        global_lock_acquired = 1;
        parameter.classList.toggle('active');

        var currentState = parameter.getAttribute('data-switch-contact-value') || 0;

        currentState = currentState === '1' ? '0' : '1';
        parameter.setAttribute('data-switch-contact-value', currentState);
        var littletextElement_status = parameter.querySelector(".little-text #status");

        // Update the content of the 'big-text' element
        if (littletextElement_status) {
            if (currentState === '1') {
                littletextElement_status.innerHTML = 'on';
                set_button_color(parameter);
            } else {
                littletextElement_status.innerHTML = 'off';
                restore_button_color(parameter);
            }
        }
        setTimeout(function () {
            global_lock_acquired = 0;
        }, 100);

    }


    function getRandomInt(max) {
        return Math.floor(Math.random() * max);
    }

    function set_button_color(element) {
        var botton_color_store = ["linear-gradient(to top, #c1dfc4 0%, #deecdd 100%)",
            "linear-gradient(to top, #accbee 0%, #e7f0fd 100%)",
        ]
        element.style.backgroundImage = botton_color_store[getRandomInt(botton_color_store.length)];
    }

    function restore_button_color(element) {
        element.style.backgroundImage = "linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%)";
    }


    // var switchIdsArray =['13', '10','36','11','12','33','31','30','35'];
    // // Example usage with setInterval
    // setInterval(function () {
    //     // Assuming switch IDs are numeric, adjust as needed
    //     for (var i = 0; i < switchIdsArray.length; i++) {
    //         var switchId = switchIdsArray[i];
    //         receiveFromServer(switchId);
    //     }
    //     receiveFromServer_garden_valve();
    // }, 500);


    // const switchIndex = 2; // Index of the switch (1 to 16)
    // const switchValue = 1; // Value of the switch (0 or 1)

    // const statusInt = generateSwitchStatusInt(switchIndex, switchValue);

    // console.log(statusInt);

    function generateSwitchStatusInt(switchIndex, switchValue) {
        if (switchIndex < 1 || switchIndex > 16) {
            throw new Error('Invalid switch index. It must be between 1 and 16.');
        }

        // Convert switchValue to a number (0 or 1)
        switchValue = Number(switchValue);

        if (isNaN(switchValue) || (switchValue !== 0 && switchValue !== 1)) {
            throw new Error('Invalid switch value. Use "0" or "1".');
        }

        return switchValue << (switchIndex - 1);
    }


    ///////////////////////////////////////////////////////////////////////

    function receiveFromServerCallBack(error, response, extras) {
        if (response) {
            console.log("================" + response + "================")
            var serverData = JSON.parse(response);
            // console.log("--------- received server data: " + serverData + "--------------------");
            if (serverData["tmp"] !== undefined) {
                updateThermostatValues(serverData);
            }

            updateswitchsContactValues(serverData);


        } else {
            // console.error("Request failed with status:", xhr.status);
            // Handle the error gracefully, e.g., show a user-friendly message
            // showError("Failed to fetch data. Please try again later.");
        }
    }

    function receiveFromServer(switchId) {

        // Construct the endpoint based on the switch ID
        var url = BASE_URL + '/get_dstatus' + switchId + '.cgi';

        makeGetRequest(url, receiveFromServerCallBack, retries = 0, timeout = 5000);
    }


    function sendToServerCallBack(error, response, extras) {
        if (response) {
            console.log('Server response:', response);
            console.log("extraaaaaaaaaaaaas", extras);
        } else if (error) {
            // console.error("Request failed with status:", xhr.status);

            var button = document.querySelector(`[data-switch-id="${extras.switch_id}"][data-switch-contact-id="${extras.switch_contact_id}"]`);
            change_button_status(button);
        }
    }

    function sendToServer(switch_id, switch_contact_id, switch_contact_value) {

        const url = BASE_URL + '/set_dstatus.cgi';
        const data = {
            'id': encodeURIComponent(switch_id),
            'hasCmd': encodeURIComponent(generateSwitchStatusInt(switch_contact_id, 1))
        }
        console.log("---------- send request body: " + JSON.stringify(data) + "-----------")
        makePriorityPostRequest(url, data, sendToServerCallBack, retries = 10, timeout = 5000, {
            'switch_id': switch_id,
            'switch_contact_id': switch_contact_id
        });
    }


    function sendToServer_garden_valveCallBack(error, response, extras) {
        if (response) {
            console.log('Server response:', response);
        } else if (error) {
            console.error("Request failed with status:", xhr.status);

        }
    }

    function sendToServer_garden_valve(switch_contact_value) {

        const url = BASE_URL + '/garden.cgi';
        const data = {'value': encodeURIComponent(Number(switch_contact_value))};

        makePriorityPostRequest(url, data, sendToServer_garden_valveCallBack, retries = 10, timeout = 5000);
    }


    function sendToServer_turn_off_home_automation_CallBack(error, response, extras) {
        if (response) {
            console.log('Server response:', response);
        } else if (error) {
            console.error("Request failed with status:", xhr.status);

        }
    }

    function sendToServer_turn_off_home_automation(switch_contact_value) {

        const url = BASE_URL + '/automation/turn-off-home';
        const data = {'value': encodeURIComponent(Number(switch_contact_value))};
        makePriorityPostRequest(url, data, sendToServer_turn_off_home_automation_CallBack, retries = 10, timeout = 5000);

    }


    function receiveFromServer_turn_off_home_automation_CallBack(error, response, extras) {
        if (response) {
            // console.log("================" + xhr.responseText)
            var serverData = JSON.parse(response);
            // console.log("--------- received server data: " + serverData + "--------------------");
            update_turn_off_home_automation_value(serverData);
        } else {
            // console.error("Request failed with status:", xhr.status);
            // Handle the error gracefully, e.g., show a user-friendly message
            // showError("Failed to fetch data. Please try again later.");
        }
    }

    function receiveFromServer_turn_off_home_automation() {

        // Construct the endpoint based on the switch ID
        var url = BASE_URL + '/automation/turn-off-home';
        makeGetRequest(url, receiveFromServer_turn_off_home_automation_CallBack, retries = 0, timeout = 5000);
    }


    function receiveFromServer_garden_valveCallBack(error, response, extras) {
        if (response) {
            // console.log("================" + xhr.responseText)
            var serverData = JSON.parse(response);
            // console.log("--------- received server data: " + serverData + "--------------------");
            update_turn_off_home_automation_value(serverData);
        } else {
            // console.error("Request failed with status:", xhr.status);
            // Handle the error gracefully, e.g., show a user-friendly message
            // showError("Failed to fetch data. Please try again later.");
        }
    }

    function receiveFromServer_garden_valve() {

        // Construct the endpoint based on the switch ID
        var url = BASE_URL + '/garden.cgi';
        makeGetRequest(url, receiveFromServer_garden_valveCallBack, retries = 0, timeout = 5000);
    }


    function update_turn_off_home_automation_value(serverData) {
        var outStatus;

        outStatus = parseInt(serverData.value, 10);
        // console.log(serverData.OutStatus)

        var button = document.querySelector(".turn_off_home_automation")

        if (button) {
            if (global_lock_acquired === 0) {
                // console.log('in update routine with global_lock_acquired = 0');
                var switchValue = (outStatus) ? 1 : 0;
                // console.log("switch :: " + switchId + " :: contact id :: " + (switchContactId + 1) + " :: value :: " + switchValue);


                if (switchValue !== parseInt(button.getAttribute('data-switch-contact-value'), 10)) {
                    change_button_status(button);
                }
            } else {
                // console.log('in update routine with global_lock_acquired = 1');
            }
        }
    }


    function update_garden_valve_value(serverData) {
        var outStatus;

        outStatus = parseInt(serverData.value, 10);
        // console.log(serverData.OutStatus)


        var button = document.querySelector(".garden-valve")

        if (button) {
            if (global_lock_acquired === 0) {
                // console.log('in update routine with global_lock_acquired = 0');
                var switchValue = (outStatus) ? 1 : 0;
                // console.log("switch :: " + switchId + " :: contact id :: " + (switchContactId + 1) + " :: value :: " + switchValue);


                if (switchValue !== parseInt(button.getAttribute('data-switch-contact-value'), 10)) {
                    change_button_status(button);
                }
            } else {
                // console.log('in update routine with global_lock_acquired = 1');
            }
        }
    }

    function updateswitchsContactValues(serverData) {
        var switchId, outStatus;

        switchId = serverData.id;
        outStatus = parseInt(serverData.OutStatus, 10);
        // console.log(serverData.OutStatus);
        get_time = new Date().getTime();
        // delay = get_time - start_get_command;
        // console.log("delay in milisecond: " + delay);

        for (var switchContactId = 0; switchContactId < 16; switchContactId++) {
            var button = document.querySelector(`[data-switch-id="${switchId}"][data-switch-contact-id="${switchContactId + 1}"]`);

            if (button) {
                // if (global_lock_acquired === 0) {

                // console.log('in update routine with global_lock_acquired = 0');
                var switchValue = (outStatus & (1 << switchContactId)) ? 1 : 0;
                // console.log("switch :: " + switchId + " :: contact id :: " + (switchContactId + 1) + " :: value :: " + switchValue);

                if (switchValue !== parseInt(button.getAttribute('data-switch-contact-value'), 10)) {

                    if (switchs_data[switchId][`${switchContactId + 1}`]['created_by'] === 'user') {
                        if (switchs_data[switchId][`${switchContactId + 1}`]['created_at']) {
                            if (switchs_data[switchId][`${switchContactId + 1}`]['created_at'] + get_interval_ms + 1380 < get_time) {

                                change_button_status(button);
                                // console.log('changed');

                                switchs_data[switchId][`${switchContactId + 1}`]['created_by'] = 'server';
                                // switchs_data[switchId][`${switchContactId+1}`]['created_at'] = new Date().getTime();
                                // console.log(switchs_data[switchId]);
                            } else {
                                // console.log("still user action is valid");
                            }
                        }
                    } else { // created_by == server

                        switchs_data[switchId][`${switchContactId + 1}`]['created_by'] = 'server';
                        // switchs_data[switchId][`${switchContactId+1}`]['created_at'] = new Date().getTime();
                        change_button_status(button);
                        // console.log('changed========');


                    }

                }
                // } else {
                //     console.log('in update routine with global_lock_acquired = 1');
                // }
            }
        }
    }


    function updateThermostatValues(serverData) {
        var switchId = parseInt(serverData.id, 10);
        var currentTemperature = parseInt(serverData.tmp, 10);
        var targetTemperature = parseInt(serverData.spt, 10);
        var fanManualSpeed = parseInt(serverData.fms, 10);
        var fanControlMode = parseInt(serverData.fct, 10);
        var heat_cool_mode = parseInt(serverData.hc, 10);

        thermostats_data[`${switchId}`]['currentTemperature'] = currentTemperature;
        thermostats_data[`${switchId}`]['targetTemperature'] = targetTemperature;
        thermostats_data[`${switchId}`]['fanManualSpeed'] = fanManualSpeed;
        thermostats_data[`${switchId}`]['fanControlMode'] = fanControlMode;
        thermostats_data[`${switchId}`]['heat_cool_mode'] = heat_cool_mode;

        console.log(thermostats_data);


        var button = document.querySelector(`[data-switch-id="${switchId}"][data-is-thermostat-button="true"]`);

        if (fanManualSpeed == 0) {
            switchValue = 0;
        } else {
            switchValue = 1;
        }

        if (switchValue !== parseInt(button.getAttribute('data-switch-contact-value'), 10)) {
            change_button_status(button);
        }
    }


    function sendToServerThermostatDataCallBack(error, response, extras) {
        if (response) {
            console.log('Server response:' + response);
            // بعد از اینکه کاربر موفق به تغییر مقادیر کنتلر شد، باز هم باید اطلاعات از کنترلر بگیرد
            setTimeout(function () {
                clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
                updateThermostatModalValuesBeforeFirstUserInteraction_timer = setInterval(function () {
                    updateThermostatModalValuesBeforeFirstUserInteraction(extras.thermostatSwitchId);
                }, 500);
            }, 2000);

        } else if (error) {
            // console.error("Request failed with status:", xhr.status);

            clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
            updateThermostatModalValuesBeforeFirstUserInteraction_timer = setInterval(function () {
                updateThermostatModalValuesBeforeFirstUserInteraction(thermostatSwitchId);
            }, 500);

        }
    }

    function sendToServerThermostatData(thermostatSwitchId, fanManualSpeed, fanControlMode, heat_cool_mode, target_temperature) {

        const url = BASE_URL + '/set_dstatus.cgi';
        const data = {
            'id': encodeURIComponent(thermostatSwitchId),
            'hasCmd': encodeURIComponent(15),
            'spt': encodeURIComponent(target_temperature),
            'fct': encodeURIComponent(fanControlMode),
            'fms': encodeURIComponent(fanManualSpeed),
            'hc': encodeURIComponent(heat_cool_mode)
        }

        makePriorityPostRequest(url, data, sendToServerThermostatDataCallBack, retries = 10, timeout = 5000, {'thermostatSwitchId': thermostatSwitchId});

    }

    function thermostatTimeoutStartTimer() {
        thermostatSendToServerTimer = setTimeout(function () {

            // console.log(fanManualSpeed);
            // console.log(fanControlMode);
            // console.log(heat_cool_mode);
            // console.log(parseInt(thermostat_target_temperature.innerText, 10));

            sendToServerThermostatData(thermostatSwitchId, fanManualSpeed, fanControlMode, heat_cool_mode, parseInt(thermostat_target_temperature.innerText, 10));

        }, 1000);
    }

    const fanButton = document.getElementById('fanButton');
    const power_switch = document.getElementById('thermostat-power-switch');
    const autoButton = document.getElementById('autoButton');
    const typeButton = document.getElementById('typeButton');

    const increaseButton = document.getElementById('thermostat-increase-button');
    const decreaseButton = document.getElementById('thermostat-decrease-button');

    const thermostat_target_temperature = document.getElementById('thermostat-target-temperature');
    const thermostat_environment_temperature = document.getElementById('thermostat-environment-temperature');

    // const fanBadge = document.getElementById('fanBadge');
    const fanStateElement = document.getElementById('fanState');
    const autoStateElement = document.getElementById('autoState');
    const typeStateElement = document.getElementById('typeState');

    const autoIconElement = document.getElementById('auto-icon');
    const manualIconElement = document.getElementById('manual-icon');
    const heatIconElement = document.getElementById('heat-icon');
    const coolIconElement = document.getElementById('cool-icon');


    const fanStates = ['کم', 'متوسط', 'زیاد'];
    const autoStates = ['دستی', 'اتوماتیک'];
    const typeStates = ['سرمایش', 'گرمایش'];

    var powerSwitchState;
    var fancurrentState;
    var autocurrentState;
    var typecurrentState;

    var fanManualSpeed;
    var fanControlMode;
    var heat_cool_mode;

    var thermostatSendToServerTimer;

    var thermostatSwitchId;

    max_thermostat_temperature = 39;
    min_thermostat_temperature = 3;

    // init thermostat event listeners
    increaseButton.addEventListener('click', function () {

        if (updateThermostatModalValuesBeforeFirstUserInteraction_timer) {
            clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
        }
        if (parseInt(thermostat_target_temperature.innerText, 10) < max_thermostat_temperature) {
            thermostat_target_temperature.innerText = (parseInt(thermostat_target_temperature.innerText, 10) + 1).toString();
        }
        if (thermostatSendToServerTimer) {
            clearTimeout(thermostatSendToServerTimer);
        }
        thermostatTimeoutStartTimer();
    });

    decreaseButton.addEventListener('click', function () {
        if (updateThermostatModalValuesBeforeFirstUserInteraction_timer) {
            clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
        }
        if (parseInt(thermostat_target_temperature.innerText, 10) > min_thermostat_temperature) {
            thermostat_target_temperature.innerText = (parseInt(thermostat_target_temperature.innerText, 10) - 1).toString();
        }
        if (thermostatSendToServerTimer) {
            clearTimeout(thermostatSendToServerTimer);
        }
        thermostatTimeoutStartTimer();

    });

    fanButton.addEventListener('click', function () {
        if (updateThermostatModalValuesBeforeFirstUserInteraction_timer) {
            clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
        }
        fancurrentState = (fancurrentState + 1) % fanStates.length;
        fanStateElement.textContent = fanStates[fancurrentState];
        if (powerSwitchState === true) {
            fanManualSpeed = fancurrentState + 1;
        }
        // thermostats_data[`${switch_id}`]['fanManualSpeed'] = fancurrentState + 1;
        if (thermostatSendToServerTimer) {
            clearTimeout(thermostatSendToServerTimer);
        }
        thermostatTimeoutStartTimer();

    });

    power_switch.addEventListener('click', function () {
        powerSwitchState = $("#thermostat-power-switch").is(":checked");
        if (updateThermostatModalValuesBeforeFirstUserInteraction_timer) {
            clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
        }

        if (powerSwitchState === false) {
            // thermostats_data[`${switch_id}`]['fanManualSpeed'] = 0;
            fanManualSpeed = 0;
        } else {
            fanManualSpeed = fancurrentState + 1;
        }

        if (thermostatSendToServerTimer) {
            clearTimeout(thermostatSendToServerTimer);
        }
        thermostatTimeoutStartTimer();

    });

    autoButton.addEventListener('click', function () {
        if (updateThermostatModalValuesBeforeFirstUserInteraction_timer) {
            clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
        }
        autocurrentState = (autocurrentState + 1) % autoStates.length;
        autoStateElement.textContent = autoStates[autocurrentState];
        fanControlMode = autocurrentState;

        if (autocurrentState === 0) {
            autoIconElement.style.display = 'none';
            manualIconElement.style.display = 'block';
        } else if (autocurrentState === 1) {
            autoIconElement.style.display = 'block';
            manualIconElement.style.display = 'none';
        }

        if (thermostatSendToServerTimer) {
            clearTimeout(thermostatSendToServerTimer);
        }
        thermostatTimeoutStartTimer();

    });

    typeButton.addEventListener('click', function () {
        if (updateThermostatModalValuesBeforeFirstUserInteraction_timer) {
            clearInterval(updateThermostatModalValuesBeforeFirstUserInteraction_timer);
        }
        typecurrentState = (typecurrentState + 1) % typeStates.length;
        typeStateElement.textContent = typeStates[typecurrentState];
        heat_cool_mode = typecurrentState;
        // thermostats_data[`${switch_id}`]['heat_cool_mode'] = typecurrentState;

        // Update button class for 'Fan Off' state
        if (typecurrentState === 0) {
            heatIconElement.style.display = 'none';
            coolIconElement.style.display = 'block';

        } else {
            heatIconElement.style.display = 'block';
            coolIconElement.style.display = 'none';
        }

        if (thermostatSendToServerTimer) {
            clearTimeout(thermostatSendToServerTimer);
        }
        thermostatTimeoutStartTimer();

    });


    function initThermostatModal(switch_id) {

        thermostatSwitchId = switch_id;

        powerSwitchState = false;
        fancurrentState = thermostats_data[`${switch_id}`]['fanManualSpeed'];
        autocurrentState = thermostats_data[`${switch_id}`]['fanControlMode'];
        typecurrentState = thermostats_data[`${switch_id}`]['heat_cool_mode'];


        fanManualSpeed = thermostats_data[`${switch_id}`]['fanManualSpeed'];
        fanControlMode = thermostats_data[`${switch_id}`]['fanControlMode'];
        heat_cool_mode = thermostats_data[`${switch_id}`]['heat_cool_mode'];

        if (thermostats_data[`${switch_id}`]['fanManualSpeed'] !== null) {
            if (thermostats_data[`${switch_id}`]['fanManualSpeed'] === 0) {
                $("#thermostat-power-switch").prop("checked", false);
                powerSwitchState = false;
            } else if (thermostats_data[`${switch_id}`]['fanManualSpeed'] > 0) {
                $("#thermostat-power-switch").prop("checked", true);
                powerSwitchState = true;
                fanStateElement.textContent = fanStates[fancurrentState - 1];
            }
        }
        if (thermostats_data[`${switch_id}`]['fanControlMode'] !== null) {
            autoStateElement.textContent = autoStates[autocurrentState];
        }
        if (thermostats_data[`${switch_id}`]['heat_cool_mode'] !== null) {
            typeStateElement.textContent = typeStates[typecurrentState];
        }
        if (thermostats_data[`${switch_id}`]['currentTemperature'] !== null) {
            thermostat_environment_temperature.innerText = thermostats_data[`${switch_id}`]['currentTemperature'];
        }
        if (thermostats_data[`${switch_id}`]['targetTemperature'] !== null) {
            thermostat_target_temperature.innerText = thermostats_data[`${switch_id}`]['targetTemperature'];
        }


    }

    function updateThermostatModalValuesBeforeFirstUserInteraction(switch_id) {

        if (thermostats_data[`${switch_id}`]['fanManualSpeed'] !== null) {
            if (thermostats_data[`${switch_id}`]['fanManualSpeed'] === 0) {
                $("#thermostat-power-switch").prop("checked", false);
                powerSwitchState = false;
            } else if (thermostats_data[`${switch_id}`]['fanManualSpeed'] > 0) {
                $("#thermostat-power-switch").prop("checked", true);
                powerSwitchState = true;
                fanStateElement.textContent = fanStates[thermostats_data[`${switch_id}`]['fanManualSpeed'] - 1];
            }
        }
        if (thermostats_data[`${switch_id}`]['fanControlMode'] !== null) {
            autoStateElement.textContent = autoStates[thermostats_data[`${switch_id}`]['fanControlMode']];
            if (thermostats_data[`${switch_id}`]['fanControlMode'] === 0) {
                autoIconElement.style.display = 'none';
                manualIconElement.style.display = 'block';
            } else if (thermostats_data[`${switch_id}`]['fanControlMode'] === 1) {
                autoIconElement.style.display = 'block';
                manualIconElement.style.display = 'none';
            }
        }
        if (thermostats_data[`${switch_id}`]['heat_cool_mode'] !== null) {

            typeStateElement.textContent = typeStates[thermostats_data[`${switch_id}`]['heat_cool_mode']];

            if (thermostats_data[`${switch_id}`]['heat_cool_mode'] === 0) {
                heatIconElement.style.display = 'none';
                coolIconElement.style.display = 'block';

            } else {
                heatIconElement.style.display = 'block';
                coolIconElement.style.display = 'none';
            }
        }
        if (thermostats_data[`${switch_id}`]['currentTemperature'] !== null) {
            thermostat_environment_temperature.innerText = thermostats_data[`${switch_id}`]['currentTemperature'];
        }
        if (thermostats_data[`${switch_id}`]['targetTemperature'] !== null) {
            thermostat_target_temperature.innerText = thermostats_data[`${switch_id}`]['targetTemperature'];
        }
    }


    // Get all elements with the class 'menu-button'
    var menuButtons = document.querySelectorAll('.menu-button');
    // Add a click event listener to each menu-button element
    for (var j = 0; j < menuButtons.length; j++) {
        menuButtons[j].addEventListener('click', function () {
            // Remove 'active' class from all menu buttons
            for (var k = 0; k < menuButtons.length; k++) {
                menuButtons[k].classList.remove('active');
            }

            // Toggle the 'active' class for the clicked menu-button element
            this.classList.toggle('active');

            // Get the index of the clicked menu button
            var clickedMenuButtonIndex = this.getAttribute("data-menu-button");

            // Hide all content blocks
            var allContent = document.querySelectorAll(".content");
            for (var l = 0; l < allContent.length; l++) {
                allContent[l].style.display = "none";
            }

            // Show the relevant content block based on the clicked menu button
            var relevantContent = document.querySelector('[data-menu-content="' + clickedMenuButtonIndex.toString() + '"]');
            if (relevantContent) {
                relevantContent.style.display = "flex";

                /////////////////////////////////////
                var containers = document.querySelectorAll('div[data-menu-content="' + clickedMenuButtonIndex.toString() + '"]' + "  div.animation-text-container");
                for (var m = 0; m < containers.length; m++) {
                    var text = containers[m].querySelector("span");
                    if (containers[m].clientWidth + 50 < text.clientWidth) {
                        text.classList.add("animate");
                    } else if (containers[m].clientWidth < text.clientWidth) {
                        text.classList.add("animate1");
                    }
                }
                ////////////////////////////////////
                if (garden_valve_get_interval) {
                    clearInterval(garden_valve_get_interval);
                }
                if (get_switchs_state_interval) {
                    clearInterval(get_switchs_state_interval);
                }


                if (clickedMenuButtonIndex === '9') {
                    // get first time immediately
                    receiveFromServer_garden_valve();
                    garden_valve_get_interval = setInterval(function () {
                        receiveFromServer_garden_valve();
                    }, get_interval_ms);
                } else if (clickedMenuButtonIndex === '10') {
                    // get first time immediately
                    receiveFromServer_turn_off_home_automation();
                    garden_valve_get_interval = setInterval(function () {
                        receiveFromServer_turn_off_home_automation();
                    }, get_interval_ms);
                } else {
                    // get first time immediately
                    for (var i = 0; i < menu_switch_ids[clickedMenuButtonIndex].length; i++) {
                        var switchId = menu_switch_ids[clickedMenuButtonIndex][i];
                        receiveFromServer(switchId);
                    }

                    get_switchs_state_interval = setInterval(function () {
                        // Assuming switch IDs are numeric, adjust as needed
                        for (var i = 0; i < menu_switch_ids[clickedMenuButtonIndex].length; i++) {

                            var switchId = menu_switch_ids[clickedMenuButtonIndex][i];
                            receiveFromServer(switchId);

                        }

                    }, get_interval_ms);
                }


            }
        });
    }

    var menuButton_1 = document.querySelector('.menu-button[data-menu-button="1"]');
    menuButton_1.click();
    // console.log("gfgfgg");





    // Get all elements with the class 'menu-button'
    var navButtons = document.querySelectorAll('.nav-button');
    // Add a click event listener to each menu-button element
    for (var j = 0; j < navButtons.length; j++) {
        navButtons[j].addEventListener('click', function () {
            // Remove 'active' class from all menu buttons
            for (var k = 0; k < navButtons.length; k++) {
                navButtons[k].classList.remove('active');
            }

            // Toggle the 'active' class for the clicked menu-button element
            this.classList.toggle('active');

            // Get the index of the clicked menu button
            var clickedNavButtonpage_name = this.getAttribute("data-page");

            // Hide all content blocks
            // var allMainPages = document.querySelectorAll(".main-page");
            // for (var l = 0; l < allMainPages.length; l++) {
            //     allMainPages[l].classList.remove('active-page');
            // }
            //
            // // Show the relevant content block based on the clicked menu button
            // var relevantContent = document.querySelector("." + clickedNavButtonpage_name.toString());
            // if (relevantContent) {
            //     relevantContent.classList.add('active-page');
            // }

        });
    }
});


///////////  Add animation to buttons bigtext element if their widths is higher than  button width /////////////
var containers = document.querySelectorAll("div.animation-text-container");
for (var m = 0; m < containers.length; m++) {
    var text = containers[m].querySelector("span");
    if (containers[m].clientWidth + 50 < text.clientWidth) {
        text.classList.add("animate");

    } else if (containers[m].clientWidth < text.clientWidth) {
        text.classList.add("animate1");
    }
}


console.log("end loading js")


