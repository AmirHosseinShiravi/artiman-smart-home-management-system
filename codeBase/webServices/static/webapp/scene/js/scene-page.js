

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
page('/web_app/v1/setting', () => showPage('.setting-page'));

page({
      click: true, // intercepts clicks on <a> tags
      popstate: true, // handles browser back/forward buttons
    });

