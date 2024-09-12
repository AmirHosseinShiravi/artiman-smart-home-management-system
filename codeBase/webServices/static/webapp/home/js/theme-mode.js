const switchElement = document.querySelector('#theme-switch');

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
    const currentTheme = getPreferredTheme();
    document.documentElement.setAttribute('data-bs-theme', currentTheme);
    if(switchElement){
        switchElement.checked = currentTheme === 'dark';
    }
    setTheme(currentTheme);
}

function toggleTheme(event) {
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
    if (!localStorage.getItem('theme')) {
        setTheme(e.matches ? 'dark' : 'light');
    } else {
        setTheme(getPreferredTheme());
    }
});

// Add event listener to theme toggle button
const theme_switch_el = document.querySelector('#theme-switch');
if(theme_switch_el){
    theme_switch_el.addEventListener('click', e => toggleTheme(e));
}

