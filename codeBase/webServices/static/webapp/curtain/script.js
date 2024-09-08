
class CurtainAnimation {
    constructor({
        curtainLeftSelector,
        curtainRightSelector,
        openButtonSelector,
        closeButtonSelector,
        animationDuration = 5000,
    }) {
        this.curtainLeft = document.querySelector(curtainLeftSelector);
        this.curtainRight = document.querySelector(curtainRightSelector);
        this.openButton = document.querySelector(openButtonSelector);
        this.closeButton = document.querySelector(closeButtonSelector);
        this.animationDuration = animationDuration;

        this.isAnimating = false;
        this.isOpening = false;
        this.openProgress = 0; // 0 = fully closed, 1 = fully open
        this.animationFrameId = null;

        this.initialize();
    }

    setTransform(element, progress) {
        const maxTranslate = 70;
        const translate = maxTranslate * progress;
        const direction = element === this.curtainLeft ? -1 : 1;
        element.style.transform = `translate(${direction * translate}%, 0%)`;
    }

    updateCurtainPosition() {
        this.setTransform(this.curtainLeft, this.openProgress);
        this.setTransform(this.curtainRight, this.openProgress);
    }

    animateCurtains(targetProgress) {
        const startProgress = this.openProgress;
        const startTime = performance.now();
        const animationDurationAdjusted = this.animationDuration * Math.abs(targetProgress - startProgress);

        const animate = (currentTime) => {
            const elapsedTime = currentTime - startTime;
            const animationProgress = Math.min(elapsedTime / animationDurationAdjusted, 1);

            this.openProgress = startProgress + (targetProgress - startProgress) * animationProgress;
            this.updateCurtainPosition();

            if (animationProgress < 1 && this.isAnimating) {
                this.animationFrameId = requestAnimationFrame(animate);
            } else {
                this.isAnimating = false;
                this.openProgress = targetProgress;
                this.updateCurtainPosition();
            }
        };

        this.isAnimating = true;
        this.animationFrameId = requestAnimationFrame(animate);
    }

    startAnimation(opening) {
        this.stopAnimation(); // Stop any ongoing animation
        this.isOpening = opening;
        const targetProgress = this.isOpening ? 1 : 0;
        this.animateCurtains(targetProgress);
    }

    stopAnimation() {
        this.isAnimating = false;
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }

    handleButtonClick(action) {
        if (this.isAnimating) {
            if ((action === 'open' && this.isOpening) || (action === 'close' && !this.isOpening)) {
                // Cancel the current animation if the same button is pressed again
                this.stopAnimation();
            } else {
                // Reverse the animation if the opposite button is pressed
                this.stopAnimation();
                this.startAnimation(!this.isOpening);
            }
        } else {
            if (action === 'open' && this.openProgress < 1) {
                this.startAnimation(true);
            } else if (action === 'close' && this.openProgress > 0) {
                this.startAnimation(false);
            }
        }
    }

    initialize() {
        if (this.openButton) {
            this.openButton.addEventListener('click', () => this.handleButtonClick('open'));
        }
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.handleButtonClick('close'));
        }
        this.updateCurtainPosition();
    }
}




// Example usage:
// Create an instance of the CurtainAnimation class
// const curtainAnimation = new CurtainAnimation({
//     curtainLeftSelector: '.curtain-left',
//     curtainRightSelector: '.curtain-right',
//     openButtonSelector: '#openButton',
//     closeButtonSelector: '#closeButton',
//     animationDuration: 5000, // 5 seconds
// });


// const curtainLeft = document.querySelector('.curtain-left');
// const curtainRight = document.querySelector('.curtain-right');
// const openButton = document.getElementById('openButton');
// const closeButton = document.getElementById('closeButton');
//
// let isAnimating = false;
// let isOpening = false;
// const animationDuration = 5000; // 5 seconds
// let openProgress = 0; // 0 = fully closed, 1 = fully open
// let animationFrameId = null;
//
// function setTransform(element, progress) {
//     const maxTranslate = 70;
//     const translate = maxTranslate * progress;
//     const direction = element.classList.contains('curtain-left') ? -1 : 1;
//     element.style.transform = `translate(${direction * translate}%, 0%)`;
// }
//
// function updateCurtainPosition() {
//     setTransform(curtainLeft, openProgress);
//     setTransform(curtainRight, openProgress);
// }
//
// function animateCurtains(targetProgress) {
//     const startProgress = openProgress;
//     const startTime = performance.now();
//     const animationDurationAdjusted = animationDuration * Math.abs(targetProgress - startProgress);
//
//     function animate(currentTime) {
//         const elapsedTime = currentTime - startTime;
//         const animationProgress = Math.min(elapsedTime / animationDurationAdjusted, 1);
//
//         openProgress = startProgress + (targetProgress - startProgress) * animationProgress;
//         updateCurtainPosition();
//
//         if (animationProgress < 1 && isAnimating) {
//             animationFrameId = requestAnimationFrame(animate);
//         } else {
//             isAnimating = false;
//             openProgress = targetProgress;
//             updateCurtainPosition();
//         }
//     }
//
//     isAnimating = true;
//     animationFrameId = requestAnimationFrame(animate);
// }
//
// function startAnimation(opening) {
//     stopAnimation(); // Stop any ongoing animation
//     isOpening = opening;
//     const targetProgress = isOpening ? 1 : 0;
//     animateCurtains(targetProgress);
// }
//
// function stopAnimation() {
//     isAnimating = false;
//     if (animationFrameId) {
//         cancelAnimationFrame(animationFrameId);
//         animationFrameId = null;
//     }
// }
//
// function handleButtonClick(action) {
//     if (isAnimating) {
//         if ((action === 'open' && isOpening) || (action === 'close' && !isOpening)) {
//             // Cancel the current animation if the same button is pressed again
//             stopAnimation();
//         } else {
//             // Reverse the animation if the opposite button is pressed
//             stopAnimation();
//             startAnimation(!isOpening);
//         }
//     } else {
//     if (action === 'open' && openProgress < 1) {
//         startAnimation(true);
//     } else if (action === 'close' && openProgress > 0) {
//         startAnimation(false);
//     }
// }
// }
//
// openButton.addEventListener('click', () => handleButtonClick('open'));
// closeButton.addEventListener('click', () => handleButtonClick('close'));
//
// // Initialize curtain position
// updateCurtainPosition();
