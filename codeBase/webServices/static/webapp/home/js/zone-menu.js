function zoneMenu() {
    const homeZones = JSON.parse(document.getElementById('home-zones-data').textContent);
    const zonesMenuContainer = document.querySelector('.zones-menu-container .row.zones-menu-slider div');
    const zoneContentContainer = document.querySelector('.zone-content-container .col-12');
    zonesMenuContainer.innerHTML = '';
    zoneContentContainer.innerHTML = '';

    homeZones.forEach((zone, index) => {
        // Create menu buttons
        const menuButton = document.createElement('div');
        menuButton.className = 'p-3 menu-button d-flex justify-content-center align-items-center';
        menuButton.setAttribute('data-menu-button', index + 1);
        menuButton.setAttribute('data-menu-button-zone', zone.zone_uuid);
        menuButton.innerHTML = `<div class="menu-text">${zone.zone_name}</div>`;
        
        if (index === 0) {
            menuButton.classList.add('active');
        }

        zonesMenuContainer.appendChild(menuButton);

        // Create content divs
        const contentDiv = document.createElement('div');
        contentDiv.className = 'row mt-3 content';
        contentDiv.setAttribute('data-menu-content', index + 1);
        contentDiv.setAttribute('data-menu-content-zone', zone.zone_uuid);
        
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
        content.style.display = content.getAttribute('data-menu-content') === contentId ? 'flex' : 'none';
    });

    buttons.forEach(button => {
        button.classList.toggle('active', button.getAttribute('data-menu-button') === contentId);
    });
}