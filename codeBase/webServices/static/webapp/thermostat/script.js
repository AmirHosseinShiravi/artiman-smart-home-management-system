class TemperatureDial {
  constructor(tempDisplaySelector, tempHandleSelector, dialCenterSelector, modalButtonSelector) {
    this.tempDisplay = document.querySelector(tempDisplaySelector);
    this.tempHandle = document.querySelector(tempHandleSelector);
    this.dialCenter = document.querySelector(dialCenterSelector);
    this.modlaButton = document.querySelector(modalButtonSelector);

    this.minTemp = 16.0;
    this.maxTemp = 32.0;
    this.tempRange = this.maxTemp - this.minTemp;

    this.origin = this.calculateRotationOrigin();
    this.rotating = false;
    // this.get_dialCenter_coordinates_intervel_entity = null;
    this.initEventListeners();
  }

  calculateRotationOrigin() {
    const { width, height, x, y } = this.dialCenter.getBoundingClientRect();
    console.log(x,y,width,height);
    return {
      x: x + width / 2,
      y: y + height / 2,
    };
  }

  handleMouseDown = (event) => {
    this.rotating = true;
  }

  handleMouseMove = (event) => {
    if (this.rotating) {
      const { clientX, clientY } = event;
      this.rotate(clientX, clientY);
    }
  }

  handleTouchMove = (event) => {
    if (this.rotating) {
      event.preventDefault();
      const { clientX, clientY } = event.touches[0];
      this.rotate(clientX, clientY);
    }
  }

  handleMouseUp = (event) => {
    this.rotating = false;
  }

  rotate(x, y) {
    const angle = Math.atan2(y - this.origin.y, x - this.origin.x);
    const angleDegrees = 180 + angle * 180 / Math.PI;
    this.updateDial(angleDegrees);
  }

  updateDial(angle) {
    const percentageOfFullRange = ((360 + (angle - 90)) % 360) / 360;
    const newTemp = (this.minTemp + this.tempRange * percentageOfFullRange).toFixed(1);
    const hue = percentageOfFullRange < 0.5 ? 200 : 5;
    const alpha = 40 + 2 * 45 * Math.abs(percentageOfFullRange - 0.5);

    this.tempDisplay.innerHTML = newTemp;
    document.documentElement.style.setProperty("--temp-rotation", `${angle}deg`);
    document.documentElement.style.setProperty("--temp-hue", hue);
    document.documentElement.style.setProperty("--temp-alpha", `${alpha}%`);
  }

  initEventListeners() {
    this.tempHandle.addEventListener("mousedown", this.handleMouseDown);
    this.tempHandle.addEventListener("touchstart", this.handleMouseDown);

    this.modlaButton.addEventListener("click", () => {
      setTimeout(()=>{
        this.origin = this.calculateRotationOrigin();
      }, 500);
      return true;

    });

    document.addEventListener("mousemove", this.handleMouseMove);
    document.addEventListener("touchmove", this.handleTouchMove, { passive: false });

    document.addEventListener("mouseup", this.handleMouseUp);
    document.addEventListener("touchend", this.handleMouseUp);

    window.addEventListener("resize", () => {
      this.origin = this.calculateRotationOrigin();
      return true;
    });
  }
}

// Example usage:
// const tempDial = new TemperatureDial("#temp-display", "#temp-handle", "#dial-center");


