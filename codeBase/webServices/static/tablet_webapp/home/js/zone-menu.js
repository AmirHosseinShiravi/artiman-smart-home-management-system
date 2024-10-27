function zoneMenu() {
    const homeZones = all_home_zones;
    const zonesMenuContainer = document.querySelector('.zones-menu-container .row.zones-menu-slider div');
    const zoneContentContainer = document.querySelector('.zone-content-container .col-12');
    zonesMenuContainer.innerHTML = '';
    zoneContentContainer.innerHTML = '';

    homeZones.forEach((zone, index) => {
        // Create menu buttons
        const menuButton = document.createElement('div');
        // menuButton.className = 'p-3 menu-button d-flex justify-content-center align-items-center';
        menuButton.className = 'menu-button';
        menuButton.setAttribute('data-menu-button', index + 1);
        menuButton.setAttribute('data-menu-button-zone', zone.zone_uuid);
        menuButton.innerHTML = `<div class="menu-text">${zone.zone_name}</div>`;
        
        if (index === 0) {
            menuButton.classList.add('active');
        }

        zonesMenuContainer.appendChild(menuButton);

        // Create content divs
        const contentDiv = document.createElement('div');
        contentDiv.className = 'grid-container mt-3 content';
        contentDiv.setAttribute('data-menu-content', index + 1);
        contentDiv.setAttribute('data-menu-content-zone', zone.zone_uuid);
//         contentDiv.innerHTML = `<div style="
//   /* height: 313px; */
//   grid-row: span 1;
//   overflow-y: scroll;
//   overflow-x: hidden;
//   max-height: 260px;
//   margin-right: -4px;
//   ">
//     <div class="row">
        
//         <div class="col-12" style="padding-bottom: 8px">
//             <div class="row scene-rule-card" style="background-color: #b6fff0;height:120px;">
//                 <div class="col-6" style="display: flex;
//                                                     justify-content: center;
//                                                     align-items: center;
//                                                     margin-top: 9px;
//                                                     margin-left:-10px;">
//                     <div class="text-section">
//                         <div class="title-text" style="color: rgb(0, 0, 0);">Leave Home</div>
//                     </div>
//                 </div>
//                 <div class="col-6 scene-rule-card-detail-section" style="display: flex;justify-content: flex-end;">
//                         <div class="icon-section" style="width:70px!important">
//                             <i class="fa-solid fa-wand-magic-sparkles" style="color: rgb(0, 0, 0);"></i>
//                         </div>
//                     </div>
//                 </div>
//         </div>
//         <div class="col-12">
//             <div class="row scene-rule-card" style="background-color: #FFC6FF;height:120px;">
//                 <div class="col-6" style="display: flex;
//                                                     justify-content: center;
//                                                     align-items: center;
//                                                     margin-top: 9px;
//                                                     margin-left:-10px;">
//                     <div class="text-section">
//                         <div class="title-text" style="color: rgb(0, 0, 0);">Leave Home</div>
//                     </div>
//                 </div>
//                 <div class="col-6 scene-rule-card-detail-section" style="display: flex;justify-content: flex-end;">
//                         <div class="icon-section" style="width:70px!important">
//                             <i class="fa-solid fa-wand-magic-sparkles" style="color: rgb(0, 0, 0);"></i>
//                         </div>
//                     </div>
//                 </div>
//         </div>
//         <div class="col-12">
//             <div class="row scene-rule-card" style="background-color: #b6fff0;height:120px;">
//                 <div class="col-6" style="display: flex;
//                                                     justify-content: center;
//                                                     align-items: center;
//                                                     margin-top: 9px;
//                                                     margin-left:-10px;">
//                     <div class="text-section">
//                         <div class="title-text" style="color: rgb(0, 0, 0);">Leave Home</div>
//                     </div>
//                 </div>
//                 <div class="col-6 scene-rule-card-detail-section" style="display: flex;justify-content: flex-end;">
//                         <div class="icon-section" style="width:70px!important">
//                             <i class="fa-solid fa-wand-magic-sparkles" style="color: rgb(0, 0, 0);"></i>
//                         </div>
//                     </div>
//                 </div>
//         </div>
//         <div class="col-12">
//             <div class="row scene-rule-card" style="background-color: #b6fff0;height:120px;">
//                 <div class="col-6" style="display: flex;
//                                                     justify-content: center;
//                                                     align-items: center;
//                                                     margin-top: 9px;
//                                                     margin-left:-10px;">
//                     <div class="text-section">
//                         <div class="title-text" style="color: rgb(0, 0, 0);">Leave Home</div>
//                     </div>
//                 </div>
//                 <div class="col-6 scene-rule-card-detail-section" style="display: flex;justify-content: flex-end;">
//                         <div class="icon-section" style="width:70px!important">
//                             <i class="fa-solid fa-wand-magic-sparkles" style="color: rgb(0, 0, 0);"></i>
//                         </div>
//                     </div>
//                 </div>
//         </div>
        
//     </div>
//   </div>`;

//   <div class="col-12">
//             <div class="scene-rule-card" style="background-color: #000000;height: 125px;display: flex;overflow: hidden;justify-content: space-between;">
                        
//                 <div class="scene-rule-card-detail-section" style="width: 100%;height: 100%;background-color: #292929;display: flex;justify-content: flex-start;background-image: url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/cHJpdmF0ZS9sci9pbWFnZXMvd2Vic2l0ZS8yMDI0LTAxL3Jhd3BpeGVsX29mZmljZV8zMl9hX2JsYWNrX2FuZF93aGl0ZV9waG90b19vZl90aGVfbW9vbl9tZXJjdXJ5X19kMThiZDFiOS1kMzc1LTRmMTAtOWQ2YS1lOGM2MTgwMzE3YmFfMS5qcGc1-removebg-pr.png);background-position: -75px -120px;align-items: center;flex-direction: row;font-weight: 900;padding: 18px 14px 14px 14px;color: aliceblue;font-size:20px">Night Mode
//                 </div>
//             </div>
//         </div>
//         <div class="col-12">
//             <div class="scene-rule-card" style="background-color: #000000;height: 125px;display: flex;overflow: hidden;justify-content: space-between;">
                        
//                 <div class="scene-rule-card-detail-section" style="width: 100%;height: 100%;background-color: #292929;display: flex;justify-content: flex-start;background-image: url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/pink-sky.png);background-position: -25px -450px;align-items: center;flex-direction: row;font-weight: 900;padding: 18px 14px 14px 14px;color: aliceblue;font-size:20px">Good Morning
//                 </div>
//             </div>
//         </div>
//         <div class="col-12">
//             <div class="scene-rule-card" style="background-color: #000000;height: 125px;display: flex;overflow: hidden;justify-content: space-between;">
                        
//                 <div class="scene-rule-card-detail-section" style="width: 100%;height: 100%;background-color: #ff7d7d;display: flex;justify-content: flex-start;background-repeat:no-repeat;background-image: url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/popcorn.png);background-position: 115px -68px;align-items: center;flex-direction: row;font-weight: 900;padding: 18px 14px 14px 14px;color: aliceblue;font-size:20px">Movie Time
//                 </div>
//             </div>
//         </div>
//         <div class="col-12">
//             <div class="scene-rule-card" style="background-color: #000000;height: 125px;display: flex;overflow: hidden;justify-content: space-between;">
                        
//                 <div class="scene-rule-card-detail-section" style="width: 100%;height: 100%;background-color: #ff7d7d;display: flex;justify-content: flex-start;background-repeat:no-repeat;background-image: url(https://349d-5-126-44-252.ngrok-free.app/static/tablet_webapp/images/dinner-table2.jpg);background-position: -165px -170px;align-items: center;flex-direction: row;font-weight: 900;padding: 18px 14px 14px 14px;color: aliceblue;font-size:20px">Dinner Time
//                 </div>
//             </div>
//         </div>


        if (index !== 0) {
            contentDiv.style.display = 'none';
        }

        zoneContentContainer.appendChild(contentDiv);
    });

    // Add click event listeners to menu buttons
    const menuButtons = document.querySelectorAll('[data-menu-button]');
    menuButtons.forEach(button => {
        button.addEventListener('click', () => {
            const contentId = button.getAttribute('data-menu-button');
            showContent(contentId);
        });
    });
};

function showContent(contentId) {
    const contents = document.querySelectorAll('[data-menu-content]');
    const buttons = document.querySelectorAll('[data-menu-button]');

    contents.forEach(content => {
        content.style.display = content.getAttribute('data-menu-content') === contentId ? 'grid' : 'none';
    });

    buttons.forEach(button => {
        button.classList.toggle('active', button.getAttribute('data-menu-button') === contentId);
    });
}