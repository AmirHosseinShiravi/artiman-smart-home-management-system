

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
            scene_automation_rule_section.style.display = "none";
            scene_tap_to_run_rule_section.style.display = "block";
            console.log(scene_tap_to_run_rule_section);
        }
        else if (event.target.id === "automation-scene-nav-link"){
            scene_tap_to_run_rule_section.style.display = "none";
            scene_automation_rule_section.style.display = "block";
            console.log(scene_automation_rule_section);
        }
    })

})


let all_scenes_rule_cards = document.querySelectorAll('.scene-rule-card');

function update_scene_rule_section(){
    remove_event_listener_of_scene_rule_cards()
    all_scenes_rule_cards = document.querySelectorAll('.scene-rule-card');
    add_event_listener_to_scene_rule_cards()
}

function remove_event_listener_of_scene_rule_cards(){
    all_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector('.scene-rule-card-detail-section');
        effective_area.removeEventListener('click', ()=>{
            alert('remove');
        })
    })
}

function add_event_listener_to_scene_rule_cards(){
    all_scenes_rule_cards.forEach(card => {
        let effective_area = card.querySelector('.scene-rule-card-detail-section');
        effective_area.addEventListener('click', ()=>{
            // open scene editor page
            alert('fdff');
        })
    })
}

update_scene_rule_section();




