
const switchElement = document.querySelector('#theme-switch');
var sync_os_theme_status = localStorage.getItem('os-theme-status');
if (!sync_os_theme_status) {
    sync_os_theme_status = 'auto';
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('theme', theme);

    const iframe = document.querySelector(".tomorrow iframe");
    if (iframe) {
        if (theme === 'dark') {
            iframe.contentWindow.document.querySelector('html').style.backgroundColor = "#040a11";
        } else {
            iframe.contentWindow.document.querySelector('html').style.backgroundColor = "#f6f8fb";
        }
    }
}

function getPreferredTheme() {
    const storedTheme = localStorage.getItem('theme');
    if (storedTheme) {
        return storedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme() {
    // Set the default theme to dark if no setting is found in local storage
    if (sync_os_theme_status === 'auto') {
        const systemTheme = getSystemTheme();
        setTheme(systemTheme);
        if (switchElement) {
            switchElement.checked = systemTheme === 'dark';
        }
    }
    else {
        const currentTheme = getPreferredTheme();
        if (switchElement) {
            switchElement.checked = currentTheme === 'dark';
        }
        setTheme(currentTheme);
    }
}

function toggleTheme(event) {
    if (sync_os_theme_status === 'auto') {
        return;
    }
    console.log('in toggle')
    console.log(event)
    if (event.currentTarget.checked) {
        setTheme('dark');
    } else {
        setTheme('light');
    }

}

// Apply theme on load
applyTheme();

// Listen for system preference changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (sync_os_theme_status === 'auto') {
        setTheme(e.matches ? 'dark' : 'light');
        if (switchElement) {
            switchElement.checked = e.matches? 'dark': 'light';
        }
    } else {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
            if (switchElement) {
                switchElement.checked = e.matches? 'dark': 'light';
            }
        } else {
            setTheme(getPreferredTheme());
            if (switchElement) {
                switchElement.checked = getPreferredTheme() === 'dark';
            }
        }
    }
});

// Add event listener to theme toggle button
const theme_switch_el = document.querySelector('#theme-switch');
if(theme_switch_el){
    theme_switch_el.addEventListener('click', e => toggleTheme(e));
}


const sync_os_theme_el = document.querySelector('#sync-os-theme');



if(sync_os_theme_el){
    if (sync_os_theme_status === 'auto'){
        sync_os_theme_el.value = 'auto';
        sync_os_theme_el.querySelector('option[value="auto"]').selected = true;
    } else {
        sync_os_theme_el.value = 'manual';
        sync_os_theme_el.querySelector('option[value="manual"]').selected = true;
    }
}


if(sync_os_theme_el){
    sync_os_theme_el.addEventListener('change', e => {
        sync_os_theme_status = e.target.value;
        if (sync_os_theme_status === 'auto') {
            localStorage.setItem('os-theme-status', 'auto');
            const systemTheme = getSystemTheme();
            setTheme(systemTheme);
            if (switchElement) {
                switchElement.checked = systemTheme === 'dark';
            }
        } else {
            const currentTheme = getPreferredTheme();
            localStorage.setItem('os-theme-status', 'manual');
            setTheme(currentTheme);
            if (switchElement) {
                switchElement.checked = currentTheme === 'dark';
            }
        }
    });
}

