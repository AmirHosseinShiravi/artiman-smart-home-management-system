

const scene_page_nav_links = [...document.getElementsByClassName('scene-nav-link')]
const scene_automation_rule_section = document.getElementsByClassName('scene-automation-rules-section')[0];
const scene_tap_to_run_rule_section = document.getElementsByClassName('scene-tap-to-run-rules-section')[0];
scene_page_nav_links.forEach(element => {
    element.addEventListener('click', (event)=>{
        scene_page_nav_links.forEach(element =>{
            console.log("remove class");
            element.classList.remove('active');
        })


        console.log("add class");
        console.log(event);
        event.target.classList.add('active');
        if (event.target.id === 'tap-to-run-scene-nav-link'){
            scene_automation_rule_section.classList.remove('active-sub-page');
            scene_tap_to_run_rule_section.classList.add('active-sub-page');
            console.log(scene_tap_to_run_rule_section);
        }
        else if (event.target.id === "automation-scene-nav-link"){
            scene_tap_to_run_rule_section.classList.remove('active-sub-page');
            scene_automation_rule_section.classList.add('active-sub-page');
            console.log(scene_automation_rule_section);
        }

    })

})



// const create_new_scene_button = document.getElementById('add-scene');
//     create_new_scene_button.addEventListener('click', (event)=> {
//
//
//             showPage('.create-new-scene-page');
//
//
//     })



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
page('/web_app/v1/home', () => showPage('.home-page'));
page('/web_app/v1/scene', () => showPage('.scene-page'));
// page('/scene-wizard', () => showPage('.scene-wizard-page'));
page({
      click: true, // intercepts clicks on <a> tags
      popstate: true, // handles browser back/forward buttons
    });


let all_tap_to_run_scenes_rule_cards = document.querySelectorAll('.scene-tap-to-run-rules-section .scene-rule-card');

function update_tap_to_run_scene_rule_section(){
    tap_to_run_remove_event_listener_of_scene_rule_cards()
    tap_to_run_remove_event_listener_of_scene_rule_cards_edit_button()
    all_tap_to_run_scenes_rule_cards = document.querySelectorAll('.scene-tap-to-run-rules-section .scene-rule-card');
    tap_to_run_add_event_listener_to_scene_rule_cards()
    tap_to_run_add_event_listener_to_scene_rule_cards_edit_button()
}

function tap_to_run_remove_event_listener_of_scene_rule_cards(){
    all_tap_to_run_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector(' .scene-rule-card-detail-section');
        effective_area.removeEventListener('click', ()=>{
            alert('remove');
        })
    })
}

function tap_to_run_add_event_listener_to_scene_rule_cards(){
    all_tap_to_run_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector(' .scene-rule-card-detail-section');
        effective_area.addEventListener('click', ()=>{
            // open scene editor page
            alert('fdff');
        })
    })
}

function tap_to_run_add_event_listener_to_scene_rule_cards_edit_button(){
    all_tap_to_run_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector('.scene-rule-card-action-section .edit-icon');
        effective_area.addEventListener('click', ()=>{
            // open scene editor page
            alert('edit pressed');
        })
    })
}

function tap_to_run_remove_event_listener_of_scene_rule_cards_edit_button(){
    all_tap_to_run_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector('.scene-rule-card-action-section .edit-icon');
        effective_area.removeEventListener('click', ()=>{
            alert('remove');
        })
    })
}


update_tap_to_run_scene_rule_section();



let all_automation_scenes_rule_cards = document.querySelectorAll('.scene-automation-rules-section .scene-rule-card');
function update_automation_scene_rule_section(){
    // automation_remove_event_listener_of_scene_rule_cards()
    automation_remove_event_listener_of_scene_rule_cards_edit_button()
    all_automation_scenes_rule_cards = document.querySelectorAll('.scene-automation-rules-section .scene-rule-card');
    // automation_add_event_listener_to_scene_rule_cards()
    automation_add_event_listener_to_scene_rule_cards_edit_button()
}

// function automation_remove_event_listener_of_scene_rule_cards(){
//     all_automation_scenes_rule_cards.forEach(card => {
//         let effective_area = card.querySelector(' .scene-rule-card-detail-section');
//         effective_area.removeEventListener('click', ()=>{
//             alert('remove');
//         })
//     })
// }
//
// function automation_add_event_listener_to_scene_rule_cards(){
//     all_automation_scenes_rule_cards.forEach(card => {
//         let effective_area = card.querySelector(' .scene-rule-card-detail-section');
//         effective_area.addEventListener('click', ()=>{
//             // open scene editor page
//             alert('fdff');
//         })
//     })
// }

function automation_add_event_listener_to_scene_rule_cards_edit_button(){
    all_automation_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector('.scene-rule-card-action-section .edit-icon');
        effective_area.addEventListener('click', ()=>{
            // open scene editor page
            alert('edit pressed');
        })
    })
}

function automation_remove_event_listener_of_scene_rule_cards_edit_button(){
    all_automation_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector('.scene-rule-card-action-section .edit-icon');
        effective_area.removeEventListener('click', ()=>{
            alert('remove');
        })
    })
}


update_automation_scene_rule_section();


