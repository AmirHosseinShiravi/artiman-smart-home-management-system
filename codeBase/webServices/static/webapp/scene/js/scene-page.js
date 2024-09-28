

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



