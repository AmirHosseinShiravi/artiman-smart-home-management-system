// // Example JavaScript code
// console.log('Hello from script.js!');


// document.addEventListener('DOMContentLoaded', function () {
            
//     // Get all elements with the class 'custom-card'
//     const customCards = document.querySelectorAll('.custom-card');

//     // Add a click event listener to each custom-card element
//     customCards.forEach(card => {
//         card.addEventListener('click', () => {
//             // Toggle the 'active' class for the clicked custom-card element
//             card.classList.toggle('active');
//             // document.getElementById('amir').innerHTML= 'fdfdff';
//             // alert('gfgfgfg');
//         });
//     });

//     // Get all elements with the class 'custom-card'
//     const menu_buttons = document.querySelectorAll('.menu-button');

//     // Add a click event listener to each custom-card element
//     menu_buttons.forEach(button => {
//         button.addEventListener('click', () => {
//             menu_buttons.forEach(c => c.classList.remove('active'));
//             // Toggle the 'active' class for the clicked custom-button element
//             button.classList.toggle('active');

//             var clicked_menu_button_index = button.getAttribute("data-menu-button");
//             var all_content = document.querySelectorAll(".content");
//             all_content.forEach(content_block =>{
//                 content_block.style.display = "none";
//             })
//             var relevant_content = document.querySelector('[data-menu-content="' + clicked_menu_button_index.toString() + '"]');
//             relevant_content.style.display = "flex";


//             console.log(button);
//         });
//     });

// });
