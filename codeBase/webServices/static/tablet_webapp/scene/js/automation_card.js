class Card {
  constructor(id, icon, title, description, status, mqttClient = null) {
    this.id = id;
    this.icon = icon;
    this.title = title;
    this.description = description;
    this.status = status;
    this.mqttClient = mqttClient;
    this.eventListeners = new Map();
    this.element = this.createCardElement();
  }

  createCardElement() {
    const card = document.createElement('div');
    card.className = 'scene-rule-card row';
    card.dataset.sceneAutomationRuleId = this.id;

    card.innerHTML = `
      <div class="col-9 scene-rule-card-detail-section">
        <div class="icon-section d-flex align-items-end">
          ${this.icon}
        </div>
        <div class="text-section">
          <div class="big-text">${this.title}</div>
          <div class="little-text"><span id="status">${this.status}</span>${this.description}</div>
        </div>
      </div>
      <div class="col-3 d-flex justify-content-end scene-rule-card-action-section">
        <div class="d-flex flex-column">
          <div class="edit-icon">
            <i class="fa-solid fa-ellipsis-vertical fa-xl"></i>
          </div>
          <div class="rule-status-switch-container">
            <div class="rule-status-switch">
              <input type="checkbox" class="checkbox" id="checkbox-${this.id}">
              <label class="switch" for="checkbox-${this.id}">
                <span class="slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>
    `;

    this.setupEventListeners(card);

    return card;
  }

  setupEventListeners(card) {
    const editIcon = card.querySelector('.edit-icon');
    editIcon.addEventListener('click', () => this.onEditClick());

    const checkbox = card.querySelector('.checkbox');
    checkbox.addEventListener('change', (event) => this.onStatusChange(event.target.checked));
  }

  setIcon(icon) {
    this.icon = icon;
    const iconSection = this.element.querySelector('.icon-section');
    iconSection.innerHTML = icon;
  }

  setTitle(title) {
    this.title = title;
    const titleElement = this.element.querySelector('.big-text');
    titleElement.textContent = title;
  }

  setDescription(description) {
    this.description = description;
    const descriptionElement = this.element.querySelector('.little-text');
    descriptionElement.innerHTML = `<span id="status">${this.status}</span>${description}`;
  }

  setStatus(status) {
    this.status = status;
    const statusElement = this.element.querySelector('#status');
    statusElement.textContent = status;
  }

  onEditClick() {
    console.log('Edit clicked for card:', this.id);
    this.sendMqttMessage('card_edit_clicked', { id: this.id });
  }

  onStatusChange(isChecked) {
    console.log('Status changed for card:', this.id, 'New status:', isChecked);
    this.sendMqttMessage('card_status_changed', { id: this.id, status: isChecked });
  }

  addEventListener(eventType, selector, callback) {
    const element = this.element.querySelector(selector);
    if (element) {
      const listener = (event) => {
        callback(event);
        this.sendMqttMessage(`${eventType}_on_${selector}`, { id: this.id, eventType, selector });
      };
      element.addEventListener(eventType, listener);
      this.eventListeners.set(`${eventType}_${selector}`, { element, listener });
    }
  }

  removeEventListener(eventType, selector) {
    const key = `${eventType}_${selector}`;
    const listenerInfo = this.eventListeners.get(key);
    if (listenerInfo) {
      const { element, listener } = listenerInfo;
      element.removeEventListener(eventType, listener);
      this.eventListeners.delete(key);
    }
  }

  sendMqttMessage(topic, message) {
    if (this.mqttClient && this.mqttClient.connected) {
      this.mqttClient.publish(topic, JSON.stringify(message));
    } else {
      console.log('MQTT client not connected. Message not sent:', { topic, message });
    }
  }

  setMqttClient(mqttClient) {
    this.mqttClient = mqttClient;
  }

  send_linkage_rule_to_server(){
    // set uuid in front end. we know it's so rare to have duplicate uuid, so we set rule uuid in frontend
    //   send data to server
  //   receive server status. if server get success status, we subscribe to all needed mqtt topics. before that, if we
  //   send subscribe command, it will be rejected.
  }

  render(container) {
    container.appendChild(this.element);
  }
}

// Usage example:
// const mqttClient = mqtt.connect('mqtt://broker.example.com');
// const svgIcon = `<svg width="48" height="48" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
//                    <!-- Your SVG path here -->
//                  </svg>`;
// const card = new Card(1, svgIcon, 'سناریو آبیاری', 'فعال &larr; هر هفته &larr; چهارشنبه‌ها &larr; ساعت ۷:۰۰ &larr;۳ دقیقه', 'فعال', mqttClient);
// card.render(document.body);