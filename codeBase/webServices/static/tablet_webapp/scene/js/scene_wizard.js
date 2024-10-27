const instanceMap = new WeakMap();

class SceneWizardPageClass {
    constructor() {
        if (instanceMap.has(SceneWizardPageClass)) {
            return instanceMap.get(SceneWizardPageClass);
        }

        this.if_conditions_list = [];
        this.then_actions_list = [];
        this.decision_expr = "or";
        this.rule_name = "";
        this.rule_style_color = '#FFB5A7';
        // this.ruleStyleImage = null;
        this.showSceneRuleInZones = new Set();

        this.add_to_home_status = false;

        this.rule_config_type = "";

        this.currentMode = "if"; // "if" or "then"
        this.selectedDevice = null;
        this.selectedDPF = null;
        this.pageHistory = [];
        this.currentPageIndex = -1;
        this.selectedDPFs = [];
        this.dpf_modal = document.querySelector('#dpf-modal');
        this.dpf_bootstrap_modal_instance = bootstrap.Modal.getOrCreateInstance(this.dpf_modal);
        // Close modal
        this.dpf_modal.addEventListener('hidden.bs.modal', this.handleDpfModalHidden);


        this.save_dpfs_button = document.getElementById('save-dpf-btn');
        this.save_dpfs_button.addEventListener('click', this.handleSaveDpfsButtonClick);


        this.page_dom = null;

        this.handle_if_add_icon_click = this.handle_if_add_icon_click.bind(this);
        this.handle_then_add_icon_click = this.handle_then_add_icon_click.bind(this);
        this.handle_if_then_lists_items_delete_button_click = this.handle_if_then_lists_items_delete_button_click.bind(this);
        this.hanlde_if_then_lists_items_edit_button_click = this.hanlde_if_then_lists_items_edit_button_click.bind(this);

        this.handleDpfModalHidden = this.handleDpfModalHidden.bind(this);
        this.handleSaveDpfsButtonClick = this.handleSaveDpfsButtonClick.bind(this);
        this.handleDeleteButtonClick = this.handleDeleteButtonClick.bind(this);
        this.handleSaveButtonClick = this.handleSaveButtonClick.bind(this);
        this.handleSchedulerModalHidden = this.handleSchedulerModalHidden.bind(this);
 

        this.scheduler_modal = document.getElementById('automate_modal_scheduler');
        this.scheduler_bootstrap_modal_instance = new bootstrap.Modal(this.scheduler_modal);
        this.scheduler_modal_weekdays = ['once', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        this.scheduler_modal_datePicker = null;


        this.delay_modal = document.getElementById('automate_modal_delay_action');
        this.delay_bootstrap_modal_instance = new bootstrap.Modal(this.delay_modal);
        this.delay_modal_datePicker = null;


        var _ = document.querySelector('#automate_modal');
        this.if_condition_options_modal = bootstrap.Modal.getOrCreateInstance(_);


        var __ = document.querySelector('#automate_modal_action_options');
        this.then_action_options_modal = bootstrap.Modal.getOrCreateInstance(__); // Returns a Bootstrap modal instance


        this.editing_item = {
            item_category: '',
            item_type: '',
            item_index: ''
        }
        this.in_editing_mode = false;


        this.scene_wizard_save_button = null;
        this.scene_wizard_delete_button = null;

        this.in_editing_linkage_rule = false;
        this.in_editing_linkage_rule_index = null;
        this.in_editing_linkage_rule_type = "";

        this.in_sending_request_progress = false;

        this.rule_config_type = "";
        // render empty scene wizard page
        this.page_dom = this.create_page_element();
        this.render(document.querySelector('.container-fluid'));
        this.addEventListeners(this.page_dom);
        this.init_sortables_lists();
        this.init_color_picker();
        // this.init_scheduler_modal();
        this.show_if_condition_empty_item();
        this.show_then_actions_empty_item();
        this.init_if_condition_options_modal();
        this.init_then_action_options_modal();
        this.enable_if_condition_tap_to_run_option();
        this.init_scheduler_modal();
        this.init_delay_modal();

        instanceMap.set(SceneWizardPageClass, this);
    }

    static getInstance() {
        if (!instanceMap.has(SceneWizardPageClass)) {
            new SceneWizardPageClass();
        }
        return instanceMap.get(SceneWizardPageClass);
    }

    destroy() {
        // Perform any cleanup here
        console.log("Destroying SceneWizardPageClass instance");

        if (this.scheduler_modal_datePicker) {
            this.scheduler_modal_datePicker.destroy(); // Assuming Picker has a destroy method
            this.scheduler_modal_datePicker = null;
        }
        if (this.delay_modal_datePicker) {
            this.delay_modal_datePicker.destroy(); // Assuming Picker has a destroy method
            this.delay_modal_datePicker = null;
        }
        this.scheduler_modal.removeEventListener('hidden.bs.modal', this.save_scheduler_item);
        this.delay_modal.removeEventListener('hidden.bs.modal', this.save_delay_item);
        this.dpf_modal.removeEventListener('hidden.bs.modal', this.handleDpfModalHidden);
        this.save_dpfs_button.removeEventListener('click', this.handleSaveDpfsButtonClick);
        if(this.scene_wizard_delete_button){    
            this.scene_wizard_delete_button.removeEventListener('click', this.handleDeleteButtonClick);
        }
        this.scene_wizard_save_button.removeEventListener('click', this.handleSaveButtonClick);
        this.scheduler_modal.removeEventListener('hidden.bs.modal', this.handleSchedulerModalHidden);

        instanceMap.delete(SceneWizardPageClass);
    }


    handleDpfModalHidden = (event) => {
        try {
            this.dpfModalSave();
        } catch (error) {
            console.error('Error in dpfModalSave:', error);
        } finally {
            this.dpf_bootstrap_modal_instance.hide();
        }
    };

    handleSaveDpfsButtonClick = (event) => {
        event.preventDefault();
        console.log('Click handler called');
        this.addConditionsOrActionsDevice();
        this.showPage('#scene-wizard-page');
        // prevent default behavior of save button
        return true;
    };

    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    create_page_element(){

        // const buttons = mode === "edit"? `
        //                                     <div class="d-flex flex-row">
        //                                     <div class="btn btn-danger btn w-100 me-3 ms-2" id="scene-wizard-delete-button">Delete</div> 
        //                                     <div class="btn btn-success btn w-100 ms-3 me-2" id="scene-wizard-save-button">Save</div> 
        //                                     </div>
        //                                   ` :
        //                                             `
        //                                                 <div class="btn btn-success btn-lg w-100 " id="scene-wizard-save-button">Save</div>
        //                                             `;
        const zone_buttons = all_home_zones.map(zone=>`
            <input type="checkbox" id="zone-${zone.zone_name}" name="scene-wizard-zone-selection" value="${zone.zone_uuid}">
                <label for="zone-${zone.zone_name}">${zone.zone_name}</label>
            `).join("");

        const scene_wizard_dom = document.createElement('div');
        scene_wizard_dom.className = 'page scene-sub-page scene-wizard-page';
        scene_wizard_dom.id = 'scene-wizard-page';
        scene_wizard_dom.innerHTML = `
        <div class="scene-page-header mt-4">
          <a href="/web_app/v1/scene" class="back-link">Cancel</a>
          <div class="scene-wizard-header-name">New Scene</div>
        </div>
        <div class="container-sm" style="max-width:80%;margin:auto;">
        <div class="scene-wizard-if-conditions-section mb-3 mt-4">
          <div class="row">

            <div class="col-9 pt-4 ps-4">
              <h3>
                If
              </h3>
              <div class="" style="width:210px">
                <select class="form-select form-select-sm bg-snow" id="decision_expr_select_input" style="border:none">
                  <option value="or">When any condition is met</option>
                  <option value="and">When all condition are met</option>
                </select>
              </div>
            </div>

            <div class="col-3 if-add-item-icon">
              <div>
                <i class="fa-solid fa-plus fa-xl"></i>
              </div>
            </div>

          </div>

          <div class="divider mt-2"></div>

          <div class="if-conditions-container">
            <div class="pb-1">
            <div class="empty-if-condition-item" style="display: none;">Add Condition</div>
            </div>
            <ul class="if-conditions-sortable-list">

            </ul>

          </div>

        </div>

        <div class="scene-wizard-then-conditions-section mt-2 mb-3 ">
          <div class="row">

            <div class="col-9 pt-4 ps-4">
              <h3>
                Then
              </h3>
            </div>

            <div class="col-3 then-add-item-icon">
              <div><i class="fa-solid fa-plus fa-xl"></i></div>
            </div>

          </div>

          <div class="then-actions-container">
            <div class="pb-1">
              <div class="empty-then-action-item" style="display: none;">Add Action</div>
            </div>
            <ul class="then-actions-sortable-list" >

            </ul>

          </div>

        </div>

        <div class="scene-wizard-linkage-rule-name mb-3 p-3">
          <div class="">
            <label for="scene_name_input" class="form-label">Rule Name</label>
            <input type="text" class="form-control fs-5" id="scene_name_input" placeholder="Set Rule Name" required>
          </div>
        </div>

        <div class="scene-wizard-linkage-rule-style mb-3 p-3">
            <div class="example full">
              <label for="scene_color_picker_input" class="form-label">Select Rule Color</label>
              <input type="text" class="coloris instance1" id="scene_color_picker_input" value="#FFB5A7" readonly>
            </div>

        </div>
        
        <div class="d-flex justify-content-between align-items-center mb-3 p-3" id="add-to-home-section">
          <span class="mr-3">Show on Home Page</span>
          <div class="form-check form-switch">
            <input class="form-check-input" style="height: 30px;width: 50px;" type="checkbox" id="scene-wizard-add-to-home-switch">
          </div>
        </div>
        <div class="scene-wizard-select-zones-section p-3" id="add-to-zones-section">            
            <div class="mt-2">
              <p class="mb-4 fs-5 fw-bold">Select Zones</p>
              <div class="zone-checkbox-container">
                ${zone_buttons}
              </div>
            </div>

        </div>
        <div class="mt-5 mb-5" id="scene-wizard-action-buttons-container">
            <div class="d-flex flex-row">
                <div class="btn btn-danger btn w-100 me-2 ms-2" id="scene-wizard-delete-button" style="display:none;">Delete<span class="spinner-border spinner-border-sm ms-2" role="status" aria-hidden="true" style="display:none;"></span></div> 
                <div class="btn btn-success btn w-100 ms-2 me-2" id="scene-wizard-save-button">Save<span class="spinner-border spinner-border-sm ms-2" role="status" aria-hidden="true" style="display:none;"></span></div> 
            </div>
        </div>
        </div>
        `;


        // add eventListener on select decision expression select input.
        const decision_expr_select_input_element = scene_wizard_dom.querySelector('#decision_expr_select_input');
        decision_expr_select_input_element.addEventListener('change', (event) => {
            this.decision_expr = event.target.value;
            return true;
        });

        const linkage_rule_name_input_element = scene_wizard_dom.querySelector('.scene-wizard-linkage-rule-name #scene_name_input');
        linkage_rule_name_input_element.addEventListener('change', (event) => {
            this.rule_name = event.target.value;
            return true;
        });

        const linkage_rule_style_color_input_element = scene_wizard_dom.querySelector('.scene-wizard-linkage-rule-style #scene_color_picker_input');
        linkage_rule_style_color_input_element.addEventListener('change', (event) => {
            this.rule_style_color = event.target.value;
            return true;
        });

        const linkage_rule_add_to_home_switch_element = scene_wizard_dom.querySelector('#scene-wizard-add-to-home-switch');
        linkage_rule_add_to_home_switch_element.addEventListener('change', (event) => {
            this.add_to_home_status = event.target.checked;
            return true;
        });

        const linkage_rule_add_to_zones_buttons_element = scene_wizard_dom.querySelectorAll('.zone-checkbox-container input[name=scene-wizard-zone-selection]');
        linkage_rule_add_to_zones_buttons_element.forEach(zone_button =>{
            zone_button.addEventListener('change', (event) => {
                if(event.target.checked){
                    this.showSceneRuleInZones.add(event.target.value)
                }
                else {
                    this.showSceneRuleInZones.delete(event.target.value)
                }
                return true;
            });
        })

        this.scene_wizard_save_button = scene_wizard_dom.querySelector('#scene-wizard-save-button');
        this.scene_wizard_save_button.addEventListener('click', this.handleSaveButtonClick);

        
        this.scene_wizard_delete_button = scene_wizard_dom.querySelector('#scene-wizard-delete-button');
        this.scene_wizard_delete_button.addEventListener("click", this.handleDeleteButtonClick);
        

        return scene_wizard_dom
    }

    handleDeleteButtonClick = (event) => {
        if (this.in_sending_request_progress){
            return;
        }
        this.in_sending_request_progress = true;    
        this.delete_selected_rule()
            .then(() => {
                this.showPage('.scene-page');
            })
            .catch((error) => {
                console.error('Error deleting linkage rule:', error);
            });
        this.in_sending_request_progress = false;
    };

    handleSaveButtonClick = () => {
        if (this.in_sending_request_progress){
            return;
        }
        this.in_sending_request_progress = true;
        this.save_linkage_rule()
            .then(() => {
                this.showPage('.scene-page');
            })
            .catch((error) => {
                console.error('Error saving linkage rule:', error);
            });
        this.in_sending_request_progress = false;
    };

    create_tap_to_run_item(){
        let item_dom = document.createElement('div');
        item_dom.className = 'item-card';
        item_dom.innerHTML = `
                  <div class="item-icon-section">
                   <i class="fa-regular fa-hand-back-point-up fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">Launch Tap to run</div>
                    <div class="detail-sub-title truncate-responsive">triggerd by user touch</div>
                  </div>
                  <div class="edit-section">
                    <div class="delete-icon">
                      <i class="fa-light fa-trash-can fa-lg"></i>
                    </div>
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>`;
        return item_dom
    }

    create_scheduler_item(title_string, sub_title_string){
        let item_dom = document.createElement('div');
        item_dom.className = 'item-card';

        item_dom.innerHTML = `
                  <div class="item-icon-section">
                    <i class="fa-regular fa-clock fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">${title_string}</div>
                    <div class="detail-sub-title truncate-responsive">${sub_title_string}</div>
                  </div>
                  <div class="edit-section">
                    <div class="delete-icon">
                      <i class="fa-light fa-trash-can fa-lg"></i>
                    </div>
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>`;
        return item_dom
    }

    create_device_item(device_name, zone_name, data_point_name, comparator, data_point_value){
        const item_dom = document.createElement('div');
        item_dom.className = 'item-card';
        item_dom.innerHTML = `
                  <div class="item-icon-section">
                    <i class="fa-sharp fa-regular fa-microchip fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">${device_name}(${zone_name})</div>
                    <div class="detail-sub-title truncate-responsive">${data_point_name}: ${comparator} ${data_point_value}</div>
                  </div>
                  <div class="edit-section">
                    <div class="delete-icon">
                      <i class="fa-light fa-trash-can fa-lg"></i>
                    </div>
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>`;

        return item_dom
    }

    create_delay_action_item(delay_string){
        let item_dom = document.createElement('div');
        item_dom.className = 'item-card';
        item_dom.innerHTML = `
                  <div class="item-icon-section">
                    <i class="fa-regular fa-clock fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">Delay the action</div>
                    <div class="detail-sub-title truncate-responsive">${delay_string}</div>
                  </div>
                  <div class="edit-section">
                    <div class="delete-icon">
                      <i class="fa-light fa-trash-can fa-lg"></i>
                    </div>
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>`;
        return item_dom
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    init_sortables_lists() {

        const if_conditions_list = this.page_dom.getElementsByClassName('if-conditions-sortable-list')[0];

        new Sortable(if_conditions_list, {
            delay: 300,
            delayOnTouchOnly: true,
            direction: 'horizontal',
            animation: 150,
            ghostClass: 'ghost',
            onEnd:  ()=> {
                this.update_if_condition_items_Indexes();
            }
        });

        const then_actions_list = this.page_dom.getElementsByClassName('then-actions-sortable-list')[0];

        new Sortable(then_actions_list, {
            delay: 300,
            delayOnTouchOnly: true,
            direction: 'horizontal',
            animation: 150,
            ghostClass: 'ghost',
            onEnd: ()=> {
                this.update_then_action_items_Indexes();
            }
        });
    }

    update_if_condition_items_Indexes() {
        const items = this.page_dom.querySelectorAll('.if-conditions-sortable-list li');
        // Create a new array to store the updated order
        const newItemsArray = [];

        if (items.length > 0) {
            items.forEach((item, index) => {
                // Get the original id
                const originalId = parseInt(item.getAttribute('data-item-index'));

                // Find the corresponding item in the original array
                const originalItem = this.if_conditions_list.find(arrItem => parseInt(arrItem["code"]) === originalId + 1);

                // Update the data-id attribute to reflect the new position
                // const newId = index + 1;
                // item.setAttribute('data-id', newId);
                // const indexSpan = item.querySelector('.index');
                item.setAttribute('data-item-index', index.toString());
                // Update the item's text content (optional)
                // item.textContent = `Item ${newId}`;

                // Create a new object with updated id and add it to the new array
                // tap-to-run card card have data-index but we decide to didn't add it to if_conditions_list, so
                // when resort if conditions list, this function called and added an item to newItemsArray. this is not
                // our desire.
                if (originalItem) {
                    newItemsArray.push({
                        ...originalItem,
                        "code": index + 1
                    });
                }

            });
            // Replace the old itemsArray with the new one
            this.if_conditions_list = newItemsArray;

        } else {
            // no element exist, so show "add action" div
            this.show_if_condition_empty_item();
            // this.enable_if_condition_tap_to_run_option();
        }
    }

    show_if_condition_empty_item() {
        const if_conditions_sortable_list_element = this.page_dom.querySelector('.if-conditions-sortable-list');
        const empty_if_condition_item_element = this.page_dom.querySelector('.empty-if-condition-item');
        if_conditions_sortable_list_element.style.display = 'none';
        empty_if_condition_item_element.style.display = 'flex';
    }

    show_if_actions_sortable_list() {
        const if_conditions_sortable_list_element = this.page_dom.querySelector('.if-conditions-sortable-list');
        const empty_if_condition_item_element = this.page_dom.querySelector('.empty-if-condition-item');
        if_conditions_sortable_list_element.style.display = 'block';
        empty_if_condition_item_element.style.display = 'none';
    }

    update_then_action_items_Indexes() {
        const items = this.page_dom.querySelectorAll('.then-actions-sortable-list li');

        // Create a new array to store the updated order
        const newItemsArray = [];

        if (items.length > 0) {
            items.forEach((item, index) => {
                // Get the original id
                const originalId = parseInt(item.getAttribute('data-item-index'));

                // Find the corresponding item in the original array
                const originalItem = this.then_actions_list.find(arrItem => parseInt(arrItem["code"]) === originalId + 1);

                // Update the data-id attribute to reflect the new position
                // const newId = index + 1;
                // item.setAttribute('data-id', newId);
                // const indexSpan = item.querySelector('.index');
                item.setAttribute('data-item-index', index.toString());
                // Update the item's text content (optional)
                // item.textContent = `Item ${newId}`;

                // Create a new object with updated id and add it to the new array
                // tap-to-run card card have data-index but we decide to didn't add it to then_actions_list, so
                // when resort if conditions list, this function called and added an item to newItemsArray. this is not
                // our desire.
                if (originalItem) {
                    newItemsArray.push({
                        ...originalItem,
                        "code": index + 1
                    });
                }

            });
            // Replace the old itemsArray with the new one
            this.then_actions_list = newItemsArray;

        } else {
            // no element exist, so show "add action" div
            this.show_then_actions_empty_item();
        }
    }

    show_then_actions_empty_item() {
        const then_actions_sortable_list_element = this.page_dom.querySelector('.then-actions-sortable-list');
        const empty_then_action_item_element = this.page_dom.querySelector('.empty-then-action-item');
        then_actions_sortable_list_element.style.display = 'none';
        empty_then_action_item_element.style.display = 'flex';
    }

    show_then_actions_sortable_list() {
        const then_actions_sortable_list_element = this.page_dom.querySelector('.then-actions-sortable-list');
        const empty_then_action_item_element = this.page_dom.querySelector('.empty-then-action-item');
        then_actions_sortable_list_element.style.display = 'block';
        empty_then_action_item_element.style.display = 'none';
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    init_color_picker(){

        Coloris({
            el: '.coloris',
            swatches: [
                '#264653',
                '#2a9d8f',
                '#e9c46a',
                '#f4a261',
                '#e76f51',
                '#d62828',
                '#023e8a',
                '#0077b6',
                '#0096c7',
                '#00b4d8',
                '#48cae4'
            ],
            themeMode: 'auto',
        });

        Coloris.setInstance('.instance1', {
            theme: 'pill',
            themeMode: 'dark',
            focusInput: false,
            // Select and focus the color value input when the color picker dialog is opened.
            selectInput: false,
            formatToggle: true,
            closeButton: true,
            clearButton: true,
            // swatchesOnly: true,
            swatches: [
                '#FFADAD',
                '#FFD6A5',
                '#FDFFB6',
                '#CAFFBF',
                '#9BF6FF',
                '#A0C4FF',
                '#BDB2FF',
                '#BDB2FF',
                '#FFC6FF',
            ]
        });

    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    add_if_add_icon_event_listener(){
        const if_add_icon = this.page_dom.querySelector('.if-add-item-icon');
        const if_empty_item = this.page_dom.querySelector('.empty-if-condition-item');
        if_add_icon.addEventListener('click', this.handle_if_add_icon_click);
        if_empty_item.addEventListener('click', this.handle_if_add_icon_click);
    }

    remove_if_add_icon_event_listener(){
        const if_add_icon = this.page_dom.querySelector('.if-add-item-icon');
        const if_empty_item = this.page_dom.querySelector('.empty-if-condition-item');
        if_add_icon.removeEventListener('click', this.handle_if_add_icon_click);
        if_empty_item.removeEventListener('click', this.handle_if_add_icon_click);
    }

    handle_if_add_icon_click(e){
        e.stopPropagation();
        if (e.target == this.page_dom.querySelector('.if-add-item-icon i') || e.target.classList.contains('empty-if-condition-item')) {
            // if we have any condition in conditions list, we should disable tap-to-run option.
            if (this.rule_config_type === "scene" || this.rule_config_type === "automation"){
                this.disable_if_condition_tap_to_run_option();
            }
            if(this.if_conditions_list.length === 0 && this.rule_config_type !== "scene"){
                this.enable_if_condition_tap_to_run_option();
                this.disable_add_to_home();
                this.disable_add_to_zones();
            }
            if(this.rule_config_type !== "scene"){
                // show condition options modal
                this.if_condition_options_modal.show();
                // console.log('handle_if_add_icon_click');
            }           
        }
    }


    add_then_add_icon_event_listener(){
        const then_add_icon = this.page_dom.querySelector('.then-add-item-icon');
        const then_empty_item = this.page_dom.querySelector('.empty-then-action-item');
        then_add_icon.addEventListener('click', this.handle_then_add_icon_click);
        then_empty_item.addEventListener('click', this.handle_then_add_icon_click);
    }

    remove_then_add_icon_event_listener(){
        const then_add_icon = this.page_dom.querySelector('.then-add-item-icon');
        const then_empty_item = this.page_dom.querySelector('.empty-then-action-item');
        then_add_icon.removeEventListener('click', this.handle_then_add_icon_click);
        then_empty_item.removeEventListener('click', this.handle_then_add_icon_click);
    }

    handle_then_add_icon_click(e){
        this.then_action_options_modal.show();
    }

    handle_if_then_lists_items_delete_button_click(e) {
        const listItem = e.target.closest('li');
        if (listItem) {

            const item_category = listItem.getAttribute('data-item-category');
            const item_type = listItem.getAttribute('data-item-type');
            const item_index = parseInt(listItem.getAttribute('data-item-index'));
            if (item_category === "if-condition-item") {
                // create new list without item that want to remove
                this.if_conditions_list.splice(item_index, 1);

                if (this.if_conditions_list.length == 0) {
                    this.rule_config_type = "";
                    this.enable_if_condition_tap_to_run_option();
                    this.disable_add_to_home();
                    this.disable_add_to_zones();
                }

                listItem.remove();

                if (item_type === 'tap-to-run') {
                    // this.rule_config_type = "";
                    this.enable_if_add_button();
                    // this.enable_if_condition_tap_to_run_option();
                } else if (item_type === 'scheduler') {
                }


                this.update_if_condition_items_Indexes();

            } else if (item_category === "then-action-item") {
                // create new list without item that want to remove
                this.then_actions_list.splice(item_index, 1);
                listItem.remove();
                this.update_then_action_items_Indexes();
            }
        }

        return true;
    }

    hanlde_if_then_lists_items_edit_button_click(e) {
        const listItem = e.target.closest('li');
        if (listItem) {
            const item_category = listItem.getAttribute('data-item-category');
            const item_type = listItem.getAttribute('data-item-type');
            const item_index = parseInt(listItem.getAttribute('data-item-index'));
            if (item_category === "if-condition-item") {
                //     get correspond list item
                //     open device page
                this.editing_item.item_category = item_category;
                this.editing_item.item_type = item_type;
                this.editing_item.item_index = item_index;

                if(item_type === "scheduler"){
                    const selected_if_condition_item = this.if_conditions_list.find(item => item["code"] === item_index + 1);
                    // double check item_type to sure about it is scheduler item.
                    if (selected_if_condition_item["entity_type"] === "timer"){
                        const schedulet_date = selected_if_condition_item["expr"]["date"];
                        const scheduler_time = selected_if_condition_item["expr"]["time"];
                        const scheduler_loop = selected_if_condition_item["expr"]["loops"].toString();
                        const datetime = schedulet_date.toString() + " " + scheduler_time.toString();
                        this.scheduler_modal_show_modal_with_values(datetime, scheduler_loop);
                        this.in_editing_mode = true;
                    }

                }
                else if (item_type === "device_report"){
                    this.currentMode = "if";
                    // this.in_editing_mode = true;
                    this.edit_device_item();
                }

            } else if (item_category === "then-action-item") {

                this.editing_item.item_category = item_category;
                this.editing_item.item_type = item_type;
                this.editing_item.item_index = item_index;

                if(item_type === "delay"){
                    const selected_then_action_item = this.then_actions_list.find(item => item["code"] === item_index + 1);
                    // double check item_type to sure about it is scheduler item.
                    if (selected_then_action_item["action_executor"] === "delay"){
                        const delay_seconds = parseInt(selected_then_action_item["executor_property"]["delay_seconds"]);
                        this.delay_modal_show_modal_with_values(delay_seconds);
                        this.in_editing_mode = true;
                    }

                }
                else if (item_type === "device_issue"){
                    this.currentMode = "then";
                    // this.in_editing_mode = true;
                    this.edit_device_item();
                }
            }
        }
    }

    addEventListeners(page_dom){
        // add event listener for delete buttons
        const delete_buttons = document.querySelectorAll('.scene-wizard-page .delete-icon');
        delete_buttons.forEach(delete_button =>{
            delete_button.addEventListener('click', this.handle_if_then_lists_items_delete_button_click);
        });

        // add event listener for edit buttons
        const edit_buttons = document.querySelectorAll('.scene-wizard-page .edit-icon');
        edit_buttons.forEach(edit_button =>{
            edit_button.addEventListener('click', this.hanlde_if_then_lists_items_edit_button_click);
        });

        this.add_if_add_icon_event_listener();
        this.add_then_add_icon_event_listener();

        // const then_add_icon = page_dom.querySelector('.then-add-item-icon');
        // then_add_icon.addEventListener('click', (e) => {
        //     //     show action options modal
        //     });



        // Add event listener to 'Once' checkbox
        document.querySelector('#automate_modal_scheduler .weekday-checkbox-container #once').addEventListener('change', this.scheduler_modal_update_weekday_checkboxes);


    }

    removeEventListeners(page_dom){
        // browser garbage collector remove unused event listener. also browser has no issue with multiple identical
        // eventlistener for one element, so we let browser to handle it :) .

        const delete_buttons = document.querySelectorAll('.scene-wizard-page .delete-icon');
        delete_buttons.forEach(delete_button =>{
            delete_button.removeEventListener('click', this.handle_if_then_lists_items_delete_button_click);
        });
        //
        // // add event listener for edit buttons
        // const edit_buttons = page_dom.querySelectorAll('.edit-icon');
        // edit_buttons.forEach(edit_button => {
        //     edit_button.removeEventListener('click', function (e) {
        //     });
        // });

        this.remove_if_add_icon_event_listener();
        this.remove_then_add_icon_event_listener();

        // const then_add_icon = page_dom.querySelector('.then-add-item-icon');
        // then_add_icon.removeEventListener('click', function (e) {});
        //
        // // add eventListener on select decision expression select input.
        // const decision_expr_select_input_element = page_dom.querySelector('#decision_expr_select_input');
        // decision_expr_select_input_element.removeEventListener('change', function (event) {});
    }

    update_event_listeners(){
        this.removeEventListeners(this.page_dom);
        this.addEventListeners(this.page_dom);
    }



    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    // enable/disable if section add icon.
    disable_if_add_button(){
        const if_add_icon = this.page_dom.querySelector('.if-add-item-icon');
        if_add_icon.classList.add('text-muted');
        this.remove_if_add_icon_event_listener();
    }

    enable_if_add_button(){
        const if_add_icon = this.page_dom.querySelector('.if-add-item-icon');
        if_add_icon.classList.remove('text-muted');
        this.add_if_add_icon_event_listener();
    }

    disable_if_condition_tap_to_run_option() {
        const tap_to_run_el = document.querySelector('#automate_modal li[data-option-type="tap-to-run"]');
        tap_to_run_el.style.opacity = 0.3;
    }

    enable_if_condition_tap_to_run_option() {

        const tap_to_run_el = document.querySelector('#automate_modal li[data-option-type="tap-to-run"]');
        tap_to_run_el.style.opacity = 1;
    }

    enable_add_to_home() {
        const add_to_home_section_element = document.querySelector('#add-to-home-section');
        add_to_home_section_element.classList.add('active');
    }

    disable_add_to_home() {
        const add_to_home_section_element = document.querySelector('#add-to-home-section');
        add_to_home_section_element.classList.remove('active');
    }


    enable_add_to_zones() {
        const add_to_zones_section_element = document.querySelector('#add-to-zones-section');
        add_to_zones_section_element.classList.add('active');
    }

    disable_add_to_zones() {
        const add_to_zones_section_element = document.querySelector('#add-to-zones-section');
        add_to_zones_section_element.classList.remove('active');
    }

    reset_add_to_home_switch(){
        const linkage_rule_add_to_home_switch_element = document.querySelector('#scene-wizard-add-to-home-switch');
        linkage_rule_add_to_home_switch_element.checked = false;
    }

    reset_add_to_zones_checkboxes(){
        const weekdayCheckboxes = document.querySelectorAll('.zone-checkbox-container input[name=scene-wizard-zone-selection][type="checkbox"]');
        weekdayCheckboxes.forEach(cb => {
            cb.checked = false;
        });
    }

    init_add_to_zones_checkboxes(){
        const zoneSelectionCheckboxes = document.querySelectorAll('.zone-checkbox-container input[name=scene-wizard-zone-selection][type="checkbox"]');
        zoneSelectionCheckboxes.forEach(checkbox=>{
            checkbox.checked = false;
        });
        this.showSceneRuleInZones.forEach(selected_zone =>{
                zoneSelectionCheckboxes.forEach(checkbox=>{
                    if (checkbox.value === selected_zone){
                        checkbox.checked = true;
                    }
                    
                });
        });
    }
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////\n
    ///////////////////////////////////////////////////////////////////////////////////////////////

    init_if_condition_options_modal(){
        const modal = document.querySelector('#automate_modal .modal-dialog');
        const previous_modal_content = document.querySelector('#automate_modal .modal-content');
        if(previous_modal_content){
            previous_modal_content.remove();
        }

        const modal_content = document.createElement('div');
        modal_content.className = 'modal-content';
        modal_content.innerHTML = `
        <div class="modal-header padding-l-20 padding-r-20 justify-content-center border-0">
          <div class="itemProduct_sm">
            <h1 class="size-18 weight-900 color-secondary m-0">Add Condition</h1>
          </div>
          <!-- here is close button -->
          <div class="absolute right-0 padding-r-20">
            <button type="button" class="btn-close close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
        </div>
        <div class="modal-body" style="padding:0;">
          <div class="padding-1">

            <ul class="if-condition-options-list">
              <li data-option-type="tap-to-run">
                <div class="item-card">
                  <div class="item-icon-section">
                    <i class="fa-regular fa-hand-back-point-up fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">Launch Tap to run</div>
                  </div>
                  <div class="edit-section">
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>
                </div>
              </li>
              <li data-option-type="schedule">
                <div class="item-card">
                  <div class="item-icon-section">
                    <i class="fa-regular fa-clock fa-xl" style="color: #63E6BE;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">Scehdule</div>
                  </div>
                  <div class="edit-section">
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>
                </div>
              </li>
              <li data-option-type="select-device-status">
                <div class="item-card">
                  <div class="item-icon-section">
                    <i class="fa-sharp fa-regular fa-microchip fa-xl" style="color: #FFD43B;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">When device status changes</div>
                  </div>
                  <div class="edit-section">
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>
                </div>
              </li>

            </ul>

          </div>

        </div>`;
        modal.appendChild(modal_content);

        const all_li_items = document.querySelectorAll('#automate_modal li');
        all_li_items.forEach(option => {
            option.addEventListener('click', (e) => {
                const option_type = e.currentTarget.getAttribute('data-option-type');
                if(option_type === 'tap-to-run'){

                    if (this.rule_config_type === "scene" || this.if_conditions_list.length > 0){return}

                    // add tap-to-run-codition to config
                    const if_condition_list_length = this.if_conditions_list.length;
                    this.if_conditions_list.push({
                                                    "code": if_condition_list_length + 1,
                                                    "entity_type": "tap-to-run",
                                                 });

                    const tap_to_run_element = this.create_tap_to_run_item();
                    const list_el = document.createElement('li');
                    list_el.dataset.itemCategory= "if-condition-item";
                    list_el.dataset.itemIndex= if_condition_list_length.toString();
                    list_el.dataset.itemType= "tap-to-run";
                    list_el.appendChild(tap_to_run_element);
                    const if_condition_sortable_list_el = this.page_dom.querySelector('.if-conditions-sortable-list');
                    if_condition_sortable_list_el.appendChild(list_el);
                    this.show_if_actions_sortable_list();
                    this.if_condition_options_modal.hide();
                    this.rule_config_type = "scene";
                    this.disable_if_add_button();
                    this.enable_add_to_home();
                    this.enable_add_to_zones();
                    this.update_event_listeners();

                }
                else if(option_type === 'schedule'){
                    // open scheduler page
                    // create if-scheduler-condition-temp-config
                    // const if_condition_list_length = this.if_conditions_list.length;
                    // this.if_conditions_list.push({
                    //     "code": if_condition_list_length + 1,
                    //     "entity_type": "timer",
                    //     "expr": {
                    //         "date": "",
                    //         "time": "",
                    //         "loops": "",
                    //         "timezone_id": "Asia/Tehran"
                    //     }
                    // })
                    // this.if_condition_in_process_item = if_condition_list_length;
                    this.scheduler_modal_reset_modal_values();
                    this.if_condition_options_modal.hide();
                    this.scheduler_bootstrap_modal_instance.show();
                    this.disable_add_to_home();
                    this.disable_add_to_zones();

                }
                else if(option_type === 'select-device-status'){
                    this.currentMode = "if";
                    this.if_condition_options_modal.hide();
                    this.showDeviceSelectionPage();
                    this.disable_add_to_home();
                    this.disable_add_to_zones();

                }

            });
        })




    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    // used to show select then actions options modal
    init_then_action_options_modal(){
        const modal = document.querySelector('#automate_modal_action_options .modal-dialog');
        const previous_modal_content = document.querySelector('#automate_modal_action_options .modal-content');
        if(previous_modal_content){
            previous_modal_content.remove();
        }
        const modal_content = document.createElement('div');
        modal_content.className = 'modal-content';
        modal_content.innerHTML = `
        <div class="modal-header padding-l-20 padding-r-20 justify-content-center border-0">
          <div class="itemProduct_sm">
            <h1 class="size-18 weight-900 color-secondary m-0">Add Action</h1>
          </div>
          <!-- here is close button -->
          <div class="absolute right-0 padding-r-20">
            <button type="button" class="btn-close close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
        </div>
        <div class="modal-body"  style="padding:0;">
          <div class="padding-1">

            <ul class="then-actions-options-list">

              <li data-option-type="delay">
                <div class="item-card">
                  <div class="item-icon-section">
                    <i class="fa-regular fa-hourglass-start fa-xl" style="color: #63E6BE;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">Delay the action</div>
                  </div>
                  <div class="edit-section">
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>
                </div>
              </li>
              <li data-option-type="control-single-device">
                <div class="item-card">
                  <div class="item-icon-section">
                    <i class="fa-sharp fa-regular fa-microchip fa-xl" style="color: #FFD43B;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">Control single device</div>
                  </div>
                  <div class="edit-section">
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>
                </div>
              </li>

            </ul>

          </div>

        </div>`;
        modal.appendChild(modal_content);

        const all_li_items = document.querySelectorAll('#automate_modal_action_options li');
        all_li_items.forEach(option => {
            option.addEventListener('click', (e) => {
                const option_type = e.currentTarget.getAttribute('data-option-type');
                if(option_type === 'delay'){

                    this.then_action_options_modal.hide();
                    this.delay_modal_reset_modal_values();
                    this.delay_bootstrap_modal_instance.show();

                }
                else if(option_type === 'control-single-device'){
                    this.currentMode = "then";
                    this.then_action_options_modal.hide();
                    this.showDeviceSelectionPage();

                }

            });
        })

    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    init_scheduler_modal() {
        // Initialize date picker
        let el = document.querySelector('.scheduler-modal-inline-picker');
        el.innerHTML = '';
        this.scheduler_modal_datePicker = new Picker(el, {
            controls: true,
            format: 'MM-DD HH:mm',
            headers: true,
            inline: true,
            rows: 3
        });
        this.scheduler_modal_reset_modal_values();
        // Add event listener for modal close
        this.scheduler_modal.addEventListener('hidden.bs.modal', this.handleSchedulerModalHidden);

    }

    handleSchedulerModalHidden = () => {
        this.save_scheduler_item();
    }

    getWeekdayString(isoWeekdayString) {
        const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        let selectedDays = [];

        // Loop through the ISO weekday string and collect the selected days
        for (let i = 0; i < isoWeekdayString.length; i++) {
            if (isoWeekdayString[i] === '1') {
                selectedDays.push(weekdays[i]);
            }
        }

        // Check if all days are selected
        if (selectedDays.length === 7) {
            return "All Days";
        }

        // If more than 4 days are selected, show the first two and last two with "..." in between
        if (selectedDays.length > 4) {
            return `${selectedDays[0]},${selectedDays[1]},...,${selectedDays[selectedDays.length - 2]},${selectedDays[selectedDays.length - 1]}`;
        }

        // Otherwise, return the full list of selected days
        return selectedDays.join(',');
    }

    save_scheduler_item = () => {
        if(!this.in_editing_mode) {
            const data = this.scheduler_modal_get_modal_values();

            const if_condition_list_length = this.if_conditions_list.length;
            this.if_conditions_list.push({
                "code": if_condition_list_length + 1,
                "entity_type": "timer",
                "expr": {
                    "date": "",
                    "time": "",
                    "loops": "",
                    "timezone_id": "Asia/Tehran"
                }
            });

            let scheduler_card_title = "";
            let scheduler_card_sub_title = "";
            if (data.weekLoop === "once") {
                let [date, time] = data.selectedDate.split(" ");
                this.if_conditions_list[if_condition_list_length]["expr"]["date"] = date;
                this.if_conditions_list[if_condition_list_length]["expr"]["time"] = time;
                this.if_conditions_list[if_condition_list_length]["expr"]["loops"] = "once";
                scheduler_card_title = `Scheduler: ${time}`;
                scheduler_card_sub_title = `${date}`;
            } else {
                let [date, time] = data.selectedDate.split(" ");
                this.if_conditions_list[if_condition_list_length]["expr"]["date"] = "";
                this.if_conditions_list[if_condition_list_length]["expr"]["time"] = time;
                this.if_conditions_list[if_condition_list_length]["expr"]["loops"] = data.weekLoop;
                scheduler_card_title = `Scheduler: ${time}`;
                scheduler_card_sub_title = this.getWeekdayString(data.weekLoop);
            }


            // console.log(`scheduler_modal_values:: ${data}`);

            // update scheduler if condition card title and sub-title
            const scheduler_item = this.create_scheduler_item(scheduler_card_title, scheduler_card_sub_title);
            const list_el = document.createElement('li');
            list_el.dataset.itemCategory = "if-condition-item";
            list_el.dataset.itemIndex = if_condition_list_length.toString();
            list_el.dataset.itemType = "scheduler";
            list_el.appendChild(scheduler_item);
            const if_condition_sortable_list_el = this.page_dom.querySelector('.if-conditions-sortable-list');
            if_condition_sortable_list_el.appendChild(list_el);
            this.show_if_actions_sortable_list();

            this.rule_config_type = "automation";
            // add condition to rule config
            this.update_event_listeners();
        }
        else{
            const data = this.scheduler_modal_get_modal_values();

            const item_index = this.editing_item.item_index;

            const scheduler_card_el = document.querySelector(`.if-conditions-sortable-list li[data-item-index="${item_index}"]`);
            let scheduler_card_title_el = scheduler_card_el.querySelector(".detail-title");
            let scheduler_card_sub_title_el = scheduler_card_el.querySelector(".detail-sub-title");

            let scheduler_card_title = "";
            let scheduler_card_sub_title = "";
            if (data.weekLoop === "once") {
                let [date, time] = data.selectedDate.split(" ");
                this.if_conditions_list[item_index]["expr"]["date"] = date;
                this.if_conditions_list[item_index]["expr"]["time"] = time;
                this.if_conditions_list[item_index]["expr"]["loops"] = "once";
                scheduler_card_title = `Scheduler: ${time}`;
                scheduler_card_sub_title = `${date}`;
            } else {
                let [date, time] = data.selectedDate.split(" ");
                this.if_conditions_list[item_index]["expr"]["date"] = "";
                this.if_conditions_list[item_index]["expr"]["time"] = time;
                this.if_conditions_list[item_index]["expr"]["loops"] = data.weekLoop;
                scheduler_card_title = `Scheduler: ${time}`;
                scheduler_card_sub_title = this.getWeekdayString(data.weekLoop);
            }
            scheduler_card_title_el.textContent = scheduler_card_title;
            scheduler_card_sub_title_el.textContent = scheduler_card_sub_title;

            this.in_editing_mode = false;
            this.editing_item.item_category = "";
            this.editing_item.item_type = "";
            this.editing_item.item_index = "";

        }

    }

    // Function to reset values
    scheduler_modal_reset_modal_values() {
        this.scheduler_modal_weekdays.forEach(day => {
            document.querySelector(`#automate_modal_scheduler .weekday-checkbox-container #${day}`).checked = false;
        });
        document.querySelector('#automate_modal_scheduler .weekday-checkbox-container #once').disabled = false;
        this.scheduler_modal_weekdays.slice(1).forEach(day => {
            document.querySelector(`#automate_modal_scheduler .weekday-checkbox-container #${day}`).disabled = false;
        });
        // this.scheduler_modal_datePicker.setDate(new Date());
    }

    parseDateTime(dateTimeString) {
        const [date, time] = dateTimeString.split(' ').map(part => part.trim());
        let month, day, hour, minute;

        if (date) {
            [month, day] = date.split('-').map(part => part.trim());
            month = month ? parseInt(month, 10) : new Date().getMonth() + 1; // default to current month if month is missing
            day = day ? parseInt(day, 10) : new Date().getDate(); // default to current day if day is missing
        } else {
            month = new Date().getMonth() + 1; // default to current month if date is missing
            day = new Date().getDate(); // default to current day if date is missing
        }

        if (time) {
            [hour, minute] = time.split(':').map(part => part.trim());
            hour = hour ? parseInt(hour, 10) : 0; // default to 0 if hour is missing
            minute = minute ? parseInt(minute, 10) : 0; // default to 0 if minute is missing
        } else {
            hour = 0; // default to 0 if time is missing
            minute = 0; // default to 0 if time is missing
        }

        if (month && day && hour && minute) {
            return new Date(`${month}/${day}/${new Date().getFullYear()} ${hour}:${minute}:00`);
        } else {
            return null; // or some other value to indicate that the input is invalid
        }
    }

    // Function to set modal values and show modal
    scheduler_modal_show_modal_with_values(dateTime, weekLoopString) {
        this.scheduler_modal_datePicker.setDate(this.parseDateTime(dateTime));
        if (weekLoopString.length === 0) {
            this.scheduler_modal_weekdays.forEach((day) => {
                const checkbox = document.querySelector(`#automate_modal_scheduler .weekday-checkbox-container #${day}`);
                checkbox.checked = false;
            });
        } else {
            this.scheduler_modal_weekdays.forEach((day, index) => {
                const checkbox = document.querySelector(`#automate_modal_scheduler .weekday-checkbox-container #${day}`);
                if (day === 'once') {
                    checkbox.checked = weekLoopString === 'once';
                } else {
                    checkbox.checked = weekLoopString[index - 1] === '1';
                }
            });
        }
        this.scheduler_modal_update_weekday_checkboxes();
        this.scheduler_bootstrap_modal_instance.show();
    }

    // Function to get modal values
    scheduler_modal_get_modal_values() {
        const selectedDate = this.scheduler_modal_datePicker.getDate(true);
        const weekLoop = this.getWeekLoop();
        return {selectedDate, weekLoop};
    }

    // Helper function to get week loop
    getWeekLoop() {
        const onceCheckbox = document.querySelector('#automate_modal_scheduler .weekday-checkbox-container #once');
        if (onceCheckbox.checked) {
            return 'once';
        }
        let week_loop = '';
        this.scheduler_modal_weekdays.slice(1).forEach(day => {
            week_loop += document.querySelector(`#automate_modal_scheduler .weekday-checkbox-container #${day}`).checked ? '1' : '0';
        });
        if(week_loop === '0000000'){
            return 'once';
        }
        else{
            return week_loop;
        }
    }

    // Function to update weekday checkboxes based on 'Once' checkbox
    scheduler_modal_update_weekday_checkboxes() {
        const onceCheckbox = document.querySelector('#automate_modal_scheduler .weekday-checkbox-container #once');
        const weekdayCheckboxes = document.querySelectorAll('#automate_modal_scheduler .weekday-checkbox-container input[type="checkbox"]:not(#once)');
        if (onceCheckbox.checked) {
            weekdayCheckboxes.forEach(cb => {
                cb.checked = false;
                cb.disabled = true;
            });
        } else {
            weekdayCheckboxes.forEach(cb => {
                cb.disabled = false;
            });
        }
    }

    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    init_delay_modal() {
        // Initialize date picker
        let el = document.querySelector('.delay-modal-inline-picker');
        el.innerHTML = "";
        this.delay_modal_datePicker = new Picker(el, {
            controls: true,
            format: 'HH:mm:ss',
            headers: true,
            inline: true,
            rows: 3
        });
        this.delay_modal_reset_modal_values();
        // Add event listener for modal close
        this.delay_modal.addEventListener('hidden.bs.modal', (event) => {
            this.save_delay_item();
        });
    }

    formatTimeToText(timeString) {
        // Split the time string into hours, minutes, and seconds
        let [hours, minutes, seconds] = timeString.split(':').map(Number);

        // Initialize the result string
        let result = '';

        // Add hours if greater than 0
        if (hours > 0) {
            result += hours + 'h';
        }

        // Add minutes if greater than 0
        if (minutes > 0) {
            result += minutes + 'min';
        }

        // Add seconds if greater than 0
        if (seconds > 0) {
            result += seconds + 'sec';
        }

        // Return the formatted string
        return result;
    }

    timeToSeconds(timeString) {
        // Split the time string into hours, minutes, and seconds
        let [hours, minutes, seconds] = timeString.split(':').map(Number);

        // Calculate total seconds
        let totalSeconds = (hours * 3600) + (minutes * 60) + seconds;

        return totalSeconds;
    }

    secondsToTimeParts(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secondsRemaining = seconds % 60;

        function pad(number) {
        return (number < 10 ? '0' : '') + number;
    }
        return [pad(hours), pad(minutes), pad(secondsRemaining)];
    }

    save_delay_item = () => {
        if(this.in_editing_mode === false) {
            const data = this.delay_modal_get_modal_values();

            if (data.selectedTime === "00:00:00") {
                return;
            };

            const then_actions_list_length = this.then_actions_list.length;
            this.then_actions_list.push({
                "code": then_actions_list_length + 1,
                "action_executor": "delay",
                "executor_property": {
                    "delay_seconds": "5"
                }
            });

            this.then_actions_list[then_actions_list_length]["executor_property"]["delay_seconds"] = this.timeToSeconds(data.selectedTime).toString();
            let delay_card_sub_title = this.formatTimeToText(data.selectedTime);


            const delay_card_element = this.create_delay_action_item(delay_card_sub_title);
            const list_el = document.createElement('li');
            list_el.dataset.itemCategory = "then-action-item";
            list_el.dataset.itemIndex = then_actions_list_length.toString();
            list_el.dataset.itemType = "delay";
            list_el.appendChild(delay_card_element);
            const then_actions_sortable_list_el = this.page_dom.querySelector('.then-actions-sortable-list');
            then_actions_sortable_list_el.appendChild(list_el);
            this.show_then_actions_sortable_list();
            this.update_event_listeners();
        }
        else{
            const data = this.delay_modal_get_modal_values();

            if (data.selectedTime === "00:00:00") {
                this.in_editing_mode = false;
                this.editing_item.item_category = "";
                this.editing_item.item_type = "";
                this.editing_item.item_index = "";
                return;
            };

            const item_index = this.editing_item.item_index;

            const delay_card_el = document.querySelector(`.then-actions-sortable-list li[data-item-index="${item_index}"]`);
            let delay_card_sub_title_el = delay_card_el.querySelector(".detail-sub-title");


            this.then_actions_list[item_index]["executor_property"]["delay_seconds"] = this.timeToSeconds(data.selectedTime).toString();
            delay_card_sub_title_el.textContent = this.formatTimeToText(data.selectedTime);


            this.in_editing_mode = false;
            this.editing_item.item_category = "";
            this.editing_item.item_type = "";
            this.editing_item.item_index = "";

        }
    }

    // Function to reset values
    delay_modal_reset_modal_values() {
        let date = new Date();
        date.setHours(0, 0, 0, 0); // Sets time to 00:00:00.000
        this.delay_modal_datePicker.setDate(date);
    }

    // Function to set modal values and show modal
    delay_modal_show_modal_with_values(total_seconds) {
        const now = new Date();
        const [hour, minute, second] = this.secondsToTimeParts(total_seconds);
        this.delay_modal_datePicker.setDate(new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, minute, second));
        this.delay_bootstrap_modal_instance.show();
    }

    // Function to get modal values
    delay_modal_get_modal_values() {
        const selectedTime = this.delay_modal_datePicker.getDate(true);
        return {selectedTime};
    }
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////


    showDeviceSelectionPage() {
            const deviceSelectionList = document.getElementById("device-selection-list");
            deviceSelectionList.innerHTML = all_home_devices.map(device => `
              <li data-device-id="${device.device_uuid}">
                <div class="device-card">
                  <div class="item-icon-section">
                    <i class="fa-sharp fa-regular fa-microchip fa-xl" style="color: #74C0FC;"></i>
                  </div>
                  <div class="detail-section">
                    <div class="detail-title truncate-responsive">${device.name}</div>
                    <div class="detail-sub-title truncate-responsive">${device.dataPointFunctions.length} dataPoint</div>
                  </div>
                  <div class="edit-section">
                    <div class="edit-icon">
                      <i class="fa-solid fa-angle-right fa-lg"></i>
                    </div>
                  </div>
                </div>
              </li>`).join("");


            deviceSelectionList.addEventListener("click", (e) => {
                if (e.target.closest("li")) {
                    const deviceId = e.target.closest("li").dataset.deviceId;
                    this.selectedDevice = all_home_devices.find(d => d.device_uuid === deviceId);
                    this.selectedDPFs = [];
                    this.showDPFSelectionPage();
                }
            });

            this.showPage("#device-selection-page");
    };


    edit_device_item(){
        const item_index = this.editing_item.item_index;
        let selected_item;
        let matched_items;
        if(this.currentMode === "if"){
            selected_item = this.if_conditions_list.find(item => item["code"] === item_index + 1);
            matched_items = this.if_conditions_list.filter(item => item["entity_type"] === "device_report" && item.hasOwnProperty("device_uuid") && item["device_uuid"] === selected_item.device_uuid);

        }
        else{
            selected_item = this.then_actions_list.find(item => item["code"] === item_index + 1);
            matched_items = this.then_actions_list.filter(item => item["action_executor"] === "device_issue" && item.hasOwnProperty("device_uuid") && item["device_uuid"] === selected_item.device_uuid);
        }
        const device_uuid = selected_item.device_uuid;
        this.selectedDevice = all_home_devices.find(d => d.device_uuid === device_uuid);
        this.selectedDPFs = [];
        this.showDPFSelectionPage();

        this.selectedDevice.dataPointFunctions.forEach(dataPoint =>{

            if (this.currentMode === "if"){
                const matched_condition = matched_items.find(condition => condition.expr.status_code === dataPoint.function_name);

                if (matched_condition){

                    const value = {value_type: matched_condition.expr.value_type, value: matched_condition.expr.status_value, comparasion_value: matched_condition.expr.comparator};

                    if(value.value_type === "BOOLEAN" || value.value_type === "STRING" ){
                        const dpfCard = document.querySelector(`.dpf-card[data-dpf-name="${dataPoint.function_name}"]`);
                        const valueElement = dpfCard.querySelector('.selected-value');
                        valueElement.textContent = `${value.value}`;
                        valueElement.dataset.dpfValue = value.value;
                        valueElement.classList.add('visible');
                    }
                    else if (value.value_type === "DECIMAL"){
                        let comparasion_string = "";
                        if (value.comparasion_value === ">"){
                            comparasion_string = "greater than";
                        }
                        else if (value.comparasion_value === "<"){
                            comparasion_string = "less than";
                        }
                        else if (value.comparasion_value === "=="){
                            comparasion_string = "equal";
                        }
                        const dpfCard = document.querySelector(`.dpf-card[data-dpf-name="${dataPoint.function_name}"]`);
                        const valueElement = dpfCard.querySelector('.selected-value');
                        valueElement.textContent = `${comparasion_string} ${value.value}`;
                        valueElement.dataset.dpfValue = value.value;
                        valueElement.dataset.dpfComparisionOperator = value.comparasion_value;
                        valueElement.classList.add('visible');
                    }
                    this.selectedDPFs.push({
                        name: dataPoint.function_name,
                        value
                    });
                }
            }
            else if (this.currentMode === "then"){

                const matched_action = matched_items.find(action => action.executor_property.function_code === dataPoint.function_name);

                if (matched_action){

                    const value = {value_type: dataPoint.type , value: matched_action.executor_property.function_value, comparasion_value: "=="};

                    if(value.value_type === "BOOLEAN" || value.value_type === "STRING" ){
                        const dpfCard = document.querySelector(`.dpf-card[data-dpf-name="${dataPoint.function_name}"]`);
                        const valueElement = dpfCard.querySelector('.selected-value');
                        valueElement.textContent = `${value.value}`;
                        valueElement.dataset.dpfValue = value.value;
                        valueElement.classList.add('visible');
                    }
                    else if (value.value_type === "DECIMAL"){
                        let comparasion_string = "";
                        if (value.comparasion_value === ">"){
                            comparasion_string = "greater than";
                        }
                        else if (value.comparasion_value === "<"){
                            comparasion_string = "less than";
                        }
                        else if (value.comparasion_value === "=="){
                            comparasion_string = "equal";
                        }
                        const dpfCard = document.querySelector(`.dpf-card[data-dpf-name="${dataPoint.function_name}"]`);
                        const valueElement = dpfCard.querySelector('.selected-value');
                        valueElement.textContent = `${comparasion_string} ${value.value}`;
                        valueElement.dataset.dpfValue = value.value;
                        valueElement.dataset.dpfComparisionOperator = value.comparasion_value;
                        valueElement.classList.add('visible');
                    }
                    this.selectedDPFs.push({
                        name: dataPoint.function_name,
                        value
                    });
                }


            }

        })

    }

    // Show DPF selection page
    showDPFSelectionPage() {
        const dpfSelectionList = document.getElementById("dpf-selection-list");
        let output_string = ""
        this.selectedDevice.dataPointFunctions.map(dpf =>{
            if(this.currentMode == "then"){
                if (dpf.io_permission === "W" | dpf.io_permission === "R/W"){
                    output_string +=  `
                    <div class="dpf-card d-flex justify-content-between align-items-center p-3 border-0 rounded-10 mb-2" data-dpf-name="${dpf.function_name}" >
                      <span class="font-weight-bold">${dpf.display_name}</span>
                      <span class="d-flex align-items-center">
                        <span class="me-3 selected-value" data-dpf-value="" data-dpf-comparision-operator="=="></span>
                        <i class="fa-solid fa-angle-right fa-lg"></i>
                      </span>
                    </div>
                    `; 
                }
            }
            else {
                output_string +=  `
                    <div class="dpf-card d-flex justify-content-between align-items-center p-3 border-0 rounded-10 mb-2" data-dpf-name="${dpf.function_name}" >
                      <span class="font-weight-bold">${dpf.display_name}</span>
                      <span class="d-flex align-items-center">
                        <span class="me-3 selected-value" data-dpf-value="" data-dpf-comparision-operator="=="></span>
                        <i class="fa-solid fa-angle-right fa-lg"></i>
                      </span>
                    </div>
                    `; 
            }
        });
        dpfSelectionList.innerHTML = output_string;

        dpfSelectionList.addEventListener("click", (e) => {
            if (e.target.closest(".dpf-card")) {
                const dpfName = e.target.closest(".dpf-card").dataset.dpfName;
                this.selectedDPF = this.selectedDevice.dataPointFunctions.find(d => d.function_name === dpfName);
                this.showDPFModal();
            }
        });

        showPage("#dpf-selection-page");
    }

    // Show DPF modal
    showDPFModal() {
        let dpf_modal_title = this.dpf_modal.querySelector('.modal-header h1');
        dpf_modal_title.textContent = `${this.selectedDPF.display_name}`;
        let dpf_modal_body = this.dpf_modal.querySelector('.modal-body div');
        dpf_modal_body.innerHTML = this.generateModalContent(this.selectedDPF);
        this.dpf_bootstrap_modal_instance.show();
    }

    // Generate modal content based on DPF type
    generateModalContent(dpf) {
        switch (dpf.type) {
            case "BOOLEAN":
              return `
                    <div class="form-group p-3">
                      <style>
                        .custom-radio-row {
                          display: flex;
                          justify-content: space-between;
                          align-items: center;
                          padding: 10px;
                          cursor: pointer;
                          margin-bottom: 10px;
                          color: var(--tblr-body-color);
                        }
                        .custom-radio-row input[type="radio"] {
                          margin-left: 10px;
                          scale: 1.3;
                        }
                        .custom-radio-row span {
                          color: var(--tblr-body-color);                        
                        }
                      </style>
                      ${dpf.typeEnum.map(value => `
                        <label class="custom-radio-row">
                          <span class="fs-6 fw-bold">${value}</span>
                          <input class="form-check-input" type="radio" name="booleanValue" value="${value}">
                        </label>
                      `).join("")}
                    </div>
            
                    <script>
                    document.querySelectorAll('.custom-radio-row').forEach(row => {
                      row.addEventListener('click', function(e) {
                        const radio = this.querySelector('input[type="radio"]');
                        radio.checked = true;
                        
                        // Trigger a change event on the radio button
                        const changeEvent = new Event('change', { bubbles: true });
                        radio.dispatchEvent(changeEvent);
                      });
                    });
                    </script>
                  `;

              case "STRING":
              return `
                    <div class="form-group mt-2 p-3">
                      <style>
                        .custom-radio-row2 {
                          display: flex;
                          justify-content: space-between;
                          align-items: center;
                          padding: 10px;
                          cursor: pointer;
                          margin-bottom: 10px;
                        }
                        .custom-radio-row2 input[type="radio"] {
                          margin-left: 10px;
                          scale: 1.3;
                        }
                        .custom-radio-row2 span {
                          color: var(--tblr-body-color);                        
                        }
                      </style>
                      ${dpf.typeEnum.map(value => `
                        <label class="custom-radio-row2">
                          <span class="fs-6 fw-bold">${value}</span>
                          <input class="form-check-input" type="radio" name="stringValue" value="${value}">
                        </label>
                      `).join("")}
                    </div>
            
                    <script>
                    document.querySelectorAll('.custom-radio-row2').forEach(row => {
                      row.addEventListener('click', function(e) {
                        const radio = this.querySelector('input[type="radio"]');
                        radio.checked = true;
                        
                        // Trigger a change event on the radio button
                        const changeEvent = new Event('change', { bubbles: true });
                        radio.dispatchEvent(changeEvent);
                      });
                    });
                    </script>
                  `;
            case "DECIMAL":
              const minValue = Math.min(...dpf.typeEnum);
              const maxValue = Math.max(...dpf.typeEnum);
              if(this.currentMode === 'if'){
                  return `
                <div class="comparison-buttons m-2 p-4 d-flex flex-column justify-content-center rounded-10">
                    <div class="text-center mb-3 fs-6 fw-bold">select comparasion</div>
                    <div class="btn-group w-100" role="group" aria-label="Comparison buttons">
                      <button type="button" onclick="dpf_comarasion_buttons_action('<')" class="btn btn-outline-primary" data-selected-status="false" data-operator="<">&lt;</button>
                      <button type="button" onclick="dpf_comarasion_buttons_action('==')" class="btn btn-outline-primary active" data-selected-status="true" data-operator="==">=</button>
                      <button type="button" onclick="dpf_comarasion_buttons_action('>')" class="btn btn-outline-primary" data-selected-status="false" data-operator=">">&gt;</button>
                    </div>
                </div>
                <div class="range-selector m-2 p-4 rounded-10">
                  <div class="text-center mb-2">
                  <label for="customRange" class="form-label fs-6 fw-bold">Select dataPoint value</label>
                  
                    <div class="current-value-display fs-5 fw-bold">${minValue}</div>
                  </div>
                  <input type="range" class="form-range" onchange="dpf_modal_range_input_show_value()" id="customRange" min="${minValue}" max="${maxValue}" step="1" value="${minValue}">
                  <div class="d-flex justify-content-between mt-2">
                    <span class="range-value-min">${minValue}</span>
                    <span class="range-value-max">${maxValue}</span>
                  </div>
                </div>
              `;
              }
              else{
                  return `
                <div class="range-selector m-2 p-4 rounded-10">
                  <div class="text-center mb-2">
                  <label for="customRange" class="form-label fs-6 fw-bold">Select dataPoint value</label>
                  
                    <div class="current-value-display fs-5 fw-bold">${minValue}</div>
                  </div>
                  <input type="range" class="form-range" onchange="dpf_modal_range_input_show_value()" id="customRange" min="${minValue}" max="${maxValue}" step="1" value="${minValue}">
                  <div class="d-flex justify-content-between mt-2">
                    <span class="range-value-min">${minValue}</span>
                    <span class="range-value-max">${maxValue}</span>
                  </div>
                </div>
              `;
              }

            default:
                return `<select>${dpf.typeEnum.map(value => `<option value="${value}">${value}</option>`).join("")}</select>`;
        }
    }



    // // Save DPF value
    dpfModalSave(){
        const selectedValue = this.getSelectedValue(this.selectedDPF.type);
        if(selectedValue === false){return}
        this.updateDPFValue(selectedValue);
        // this.dpf_bootstrap_modal_instance.hide();

        // Add or update the selected DPF
        const existingDPFIndex = this.selectedDPFs.findIndex(dpf => dpf.function_name === this.selectedDPF.function_name);
        if (existingDPFIndex !== -1) {
            this.selectedDPFs[existingDPFIndex].value = selectedValue;
        } else {
            this.selectedDPFs.push({
                name: this.selectedDPF.function_name,
                value: selectedValue
            });
        }
    };

    // Get selected value based on DPF type
    getSelectedValue(type) {
        let comparasion_value = "==";
        switch (type) {
            case "BOOLEAN":
                 const radio_value = document.querySelector('input[name="booleanValue"]:checked');
                 if (radio_value){
                     return {value_type: "BOOLEAN", value: radio_value.value, comparasion_value}
                 }
                 else{
                    return false
                 }
            case "STRING":
                 const string_radio_value = document.querySelector('input[name="stringValue"]:checked');
                 if(string_radio_value){
                     return {value_type: "STRING", value: string_radio_value.value, comparasion_value}
                 }
                 else{
                     return false
                 }
            case "DECIMAL":
                const range_selector = document.querySelector('.range-selector input').value;
                const selected_comparasion = document.querySelector('.comparison-buttons button[data-selected-status="true"]');

                if(selected_comparasion){
                    comparasion_value = selected_comparasion.dataset.operator;
                }
                return {value_type: "DECIMAL", value: range_selector, comparasion_value}
            default:
                return document.querySelector('select').value;
        }
    }

    // Update DPF value in the selection list
    updateDPFValue(value) {
        if(value.value_type === "BOOLEAN" || value.value_type === "STRING" ){
            const dpfCard = document.querySelector(`.dpf-card[data-dpf-name="${this.selectedDPF.function_name}"]`);
            const valueElement = dpfCard.querySelector('.selected-value');
            valueElement.textContent = `${value.value}`;
            valueElement.dataset.dpfValue = value.value;
            valueElement.classList.add('visible');
        }
        else if (value.value_type === "DECIMAL"){
            let comparasion_string = "";
            if (value.comparasion_value === ">"){
                comparasion_string = "greater than";
            }
            else if (value.comparasion_value === "<"){
                comparasion_string = "less than";
            }
            else if (value.comparasion_value === "=="){
                comparasion_string = "equal";
            }
            const dpfCard = document.querySelector(`.dpf-card[data-dpf-name="${this.selectedDPF.function_name}"]`);
            const valueElement = dpfCard.querySelector('.selected-value');
            valueElement.textContent = `${comparasion_string} ${value.value}`;
            valueElement.dataset.dpfValue = value.value;
            valueElement.dataset.dpfComparisionOperator = value.comparasion_value;
            valueElement.classList.add('visible');
        }

    }


    // Add conditions or actions to the rule wizard page
    addConditionsOrActionsDevice() {
        console.log('============== addConditionsOrActionsDevice called ==================');
        const listElement = this.currentMode === "if" ?
            document.querySelector(".if-conditions-sortable-list") :
            document.querySelector(".then-actions-sortable-list");

        this.selectedDPFs.forEach(dpf => {
            // add to list
            const device_zone = all_home_zones.find(zone => zone.zone_uuid === this.selectedDevice.zone_uuid);
            const device_name = this.selectedDevice.name;
            const desire_dpf = this.selectedDevice.dataPointFunctions.find(item => item.function_name === dpf.name);
            let comparasion_string = "";

            if(this.currentMode === "if"){

                let matched_if_condition = this.if_conditions_list.find(item => item["entity_type"] === "device_report" && item.hasOwnProperty("device_uuid") && item["device_uuid"] === this.selectedDevice.device_uuid && item["expr"]["status_code"] === dpf.name);
                if(matched_if_condition){

                    matched_if_condition['expr']["comparator"] = dpf.value.comparasion_value;
                    matched_if_condition['expr']["status_value"] = dpf.value.value;

                    const if_matched_card_el = document.querySelector(`.if-conditions-sortable-list li[data-item-index="${parseInt(matched_if_condition["code"]) - 1}"]`);
                    let if_matched_card_title_el = if_matched_card_el.querySelector(".detail-title");
                    let if_matched_card_sub_title_el = if_matched_card_el.querySelector(".detail-sub-title");
                    if_matched_card_title_el.textContent = `${device_name}(${device_zone.zone_name})`;

                    if (dpf.value.comparasion_value === ">"){
                        comparasion_string = "greater than";
                    }
                    else if (dpf.value.comparasion_value === "<"){
                        comparasion_string = "less than";
                    }
                    else if (dpf.value.comparasion_value === "=="){
                        comparasion_string = "equal";
                    }
                    if_matched_card_sub_title_el.textContent = `${desire_dpf.display_name}: ${comparasion_string} ${dpf.value.value}`;
                }
                else {
                    // if condition with those constrain not exist, so we create new one
                    const if_conditions_list_length = this.if_conditions_list.length;
                    this.if_conditions_list.push({
                        "code": if_conditions_list_length + 1,
                        "entity_type": "device_report",
                        "controller_uuid": `${this.selectedDevice.controller_uuid}`,
                        "device_uuid": `${this.selectedDevice.device_uuid}`,
                        "expr": {
                            "status_code": `${desire_dpf.function_name}`,
                            "comparator": `${dpf.value.comparasion_value}`,
                            "status_value": `${dpf.value.value}`,
                            "value_type": `${dpf.value.value_type}`
                        }
                    });

                    if (dpf.value.comparasion_value === ">"){
                        comparasion_string = "greater than";
                    }
                    else if (dpf.value.comparasion_value === "<"){
                        comparasion_string = "less than";
                    }
                    else if (dpf.value.comparasion_value === "=="){
                        comparasion_string = "equal";
                    }
                    const condition_device_card_element = this.create_device_item(device_name, device_zone.zone_name, desire_dpf.display_name, comparasion_string, dpf.value.value);
                    const condition_list_el = document.createElement('li');
                    condition_list_el.dataset.itemCategory = "if-condition-item";
                    condition_list_el.dataset.itemIndex = if_conditions_list_length.toString();
                    condition_list_el.dataset.itemType = "device_report";
                    condition_list_el.appendChild(condition_device_card_element);
                    listElement.appendChild(condition_list_el);
                    this.show_if_actions_sortable_list();
                    this.rule_config_type = "automation";
                }
            }
            else if(this.currentMode === "then"){

                let matched_then_action = this.then_actions_list.find(item => item["action_executor"] === "device_issue" && item.hasOwnProperty("device_uuid") && item["device_uuid"] === this.selectedDevice.device_uuid && item["executor_property"]["function_code"] === dpf.name);
                if(matched_then_action){

                    matched_then_action['executor_property']["function_value"] = dpf.value.value;
                    const then_matched_card_el = document.querySelector(`.then-actions-sortable-list li[data-item-index="${parseInt(matched_then_action["code"]) - 1}"]`);
                    let then_matched_card_title_el = then_matched_card_el.querySelector(".detail-title");
                    let then_matched_card_sub_title_el = then_matched_card_el.querySelector(".detail-sub-title");
                    then_matched_card_title_el.textContent = `${device_name}(${device_zone.zone_name})`;
                    if (dpf.value.comparasion_value === ">"){
                        comparasion_string = "greater than";
                    }
                    else if (dpf.value.comparasion_value === "<"){
                        comparasion_string = "less than";
                    }
                    else if (dpf.value.comparasion_value === "=="){
                        comparasion_string = "equal";
                    }
                    then_matched_card_sub_title_el.textContent = `${desire_dpf.display_name}: ${comparasion_string} ${dpf.value.value}`;
                }
                else{
                    // if condition with those constrain not exist, so we create new one
                    const then_actions_list_length = this.then_actions_list.length;
                    this.then_actions_list.push({
                        "code": then_actions_list_length + 1,
                        "action_executor": "device_issue",
                        "controller_uuid": `${this.selectedDevice.controller_uuid}`,
                        "device_uuid": `${this.selectedDevice.device_uuid}`,
                        "executor_property": {
                            "function_code": `${desire_dpf.function_name}`,
                            "function_value": `${dpf.value.value}`
                        }
                    });
                    if (dpf.value.comparasion_value === ">"){
                        comparasion_string = "greater than";
                    }
                    else if (dpf.value.comparasion_value === "<"){
                        comparasion_string = "less than";
                    }
                    else if (dpf.value.comparasion_value === "=="){
                        comparasion_string = "equal";
                    }
                    const then_device_card_element = this.create_device_item(device_name, device_zone.zone_name, desire_dpf.display_name, comparasion_string, dpf.value.value);
                    const action_list_el = document.createElement('li');
                    action_list_el.dataset.itemCategory = "then-action-item";
                    action_list_el.dataset.itemIndex = then_actions_list_length.toString();
                    action_list_el.dataset.itemType = "device_issue";
                    action_list_el.appendChild(then_device_card_element);
                    listElement.appendChild(action_list_el);
                    this.show_then_actions_sortable_list();
                }

            }


        });
        this.update_event_listeners();
    }



    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////

    generateUUID4() {
        return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    }

    async save_linkage_rule() {
        let rule_index = 0;
        let rule_config = {};

        if(!this.in_editing_linkage_rule) {

            if (this.rule_config_type === 'scene') {
                const all_scene_rules = linkage_rules.filter(item => item["type"] === "scene");
                rule_index = all_scene_rules.length;
            }
            else if (this.rule_config_type === "automation") {
                const all_automation_rules = linkage_rules.filter(item => item["type"] === "automation");
                rule_index = all_automation_rules.length;
            }
            else {
                // do nothing and return to scene page without adding new rule to linkage rules array.
                console.log(linkage_rules);
                return
            }

            if (this.if_conditions_list.length === 0 || this.then_actions_list.length === 0) {
                return
            }

            rule_config = {
                "name": `${this.rule_name}`,
                "index": rule_index,
                "rule_uuid": `${this.generateUUID4()}`,
                "project_uuid": `${project_uuid}`,
                "home_uuid": `${home_uuid}`,
                "type": `${this.rule_config_type}`,
                "status": "enable",
                "add_to_home_status": `${this.add_to_home_status}`,
                "style": {
                    "color": `${this.rule_style_color}`
                },
                "show_scene_rule_in_zones": [...this.showSceneRuleInZones],
                "decision_expr": `${this.decision_expr}`,
                "effective_time": {
                    "start": "00:00:00",
                    "end": "23:59:59",
                    "loops": "1111111",
                    "timezone_id": "Asia/Tehran"
                },
                "conditions": this.if_conditions_list,
                "actions": this.then_actions_list
            };

            console.log(rule_config);


            try {
                
                // this.in_sending_request_progress = true;
                this.scene_wizard_save_button.querySelector('span').style.display = "inline-block";
                this.scene_wizard_save_button.disabled = true;
                // this.scene_wizard_save_button.textContent = "Saving...";

                const response = await fetch(`${linkage_rule_base_url}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token
                    },
                    body: JSON.stringify(rule_config)
                });
                if (response.ok) {
                    const result = await response.json();
                    console.log('Success:', result);
                    if (result.status === "success") {
                        rule_config["rule_uuid"] = result.rule_uuid;
                        linkage_rules.push(rule_config);

                        mqttClient.publish(`v1/projects/${project_uuid}/homes/${home_uuid}/linkage-rules/${result.rule_uuid}/actions/create-new-rule-event`, 'True', {qos:2});

                        get_linkage_rules().then(() => {
                            generateRuleCards();
                            add_tap_to_run_rules_to_selected_zones();
                        });

                    } else {
                        console.error('Error:', response.status);
                        // Handle error
                    }
                } else {
                    console.error('Error:', response.status);
                    // Handle error
                }
            } catch (error) {
                console.error('Error:', error);
                // Handle network error or other unexpected errors
            }

        }
        else if(this.in_editing_linkage_rule){

            let matched_rule = linkage_rules.find(rule => rule["index"] === this.in_editing_linkage_rule_index && rule.type === this.in_editing_linkage_rule_type);

            if(matched_rule) {

                let copy_object = {...matched_rule};
                copy_object["name"] = `${this.rule_name}`;
                if(this.rule_config_type !== this.in_editing_linkage_rule_type){
                    const number_of_new_rule_type_rules = linkage_rules.filter(rule => rule.type === this.rule_config_type).length;
                    copy_object["index"] = number_of_new_rule_type_rules;
                }
                copy_object["type"] = `${this.rule_config_type}`;
                copy_object["add_to_home_status"] = `${this.add_to_home_status}`;
                copy_object["show_scene_rule_in_zones"] = [...this.showSceneRuleInZones];
                copy_object["style"] = {
                    "color": `${this.rule_style_color}`
                }
                copy_object["decision_expr"] = `${this.decision_expr}`;
                copy_object["conditions"] = this.if_conditions_list;
                copy_object["actions"] = this.then_actions_list;


                try {
                    
                    // this.in_sending_request_progress = true;
                    this.scene_wizard_save_button.querySelector('span').style.display = "inline-block";
                    this.scene_wizard_save_button.disabled = true;
                    // this.scene_wizard_save_button.textContent = "Saving...";

                    const response = await fetch(`${linkage_rule_base_url}${matched_rule["rule_uuid"]}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token
                        },
                        body: JSON.stringify(copy_object)
                    });

                    if (response.ok) {
                        const result = await response.json();
                        console.log('Success:', result);
                        if(result.status === "success") {
                            matched_rule["name"] = `${this.rule_name}`;
                            if (this.rule_config_type !== this.in_editing_linkage_rule_type) {
                                const number_of_new_rule_type_rules = linkage_rules.filter(rule => rule.type === this.rule_config_type).length;
                                matched_rule["index"] = number_of_new_rule_type_rules;
                            }
                            matched_rule["type"] = `${this.rule_config_type}`;
                            matched_rule["add_to_home_status"] = `${this.add_to_home_status}`;
                            matched_rule["show_scene_rule_in_zones"] = [...this.showSceneRuleInZones];
                            matched_rule["style"] = {
                                "color": `${this.rule_style_color}`
                            }
                            matched_rule["decision_expr"] = `${this.decision_expr}`;
                            matched_rule["conditions"] = this.if_conditions_list;
                            matched_rule["actions"] = this.then_actions_list;

                            mqttClient.publish(`v1/projects/${project_uuid}/homes/${home_uuid}/linkage-rules/${result.rule_uuid}/actions/create-new-rule-event`, 'True', {qos:2});

                            get_linkage_rules().then(() => {
                                generateRuleCards();
                                add_tap_to_run_rules_to_selected_zones();
                            });
                        }

                    } else {
                        console.error('Error:', response.status);
                        // Handle error
                    }
                } catch (error) {
                    console.error('Error:', error);
                    // Handle network error or other unexpected errors
                }
            }

        }


    }




    async delete_selected_rule(){
        if(this.in_editing_linkage_rule){
            let matched_rule = linkage_rules.find(rule => rule["index"] === this.in_editing_linkage_rule_index && rule.type === this.in_editing_linkage_rule_type);

            if(matched_rule) {
                try {
                    
                    // this.in_sending_request_progress = true;
                    this.scene_wizard_delete_button.querySelector('span').style.display = "inline-block";
                    this.scene_wizard_delete_button.disabled = true;
                    // this.scene_wizard_delete_button.textContent = "Deleting...";

                    const response = await fetch(`${linkage_rule_base_url}delete/${matched_rule["rule_uuid"]}/`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token
                        },
                    });

                    if (response.ok) {
                        const result = await response.json();
                        console.log('Success:', result);
                        if(result.status === "success"){
                            const rule_index = linkage_rules.findIndex(rule => rule.rule_uuid === matched_rule.rule_uuid);
                            if (rule_index > -1) {
                              linkage_rules.splice(rule_index, 1);
                            }
                            mqttClient.publish(`v1/projects/${project_uuid}/homes/${home_uuid}/linkage-rules/${result.rule_uuid}/actions/create-new-rule-event`, 'True');
                            get_linkage_rules().then(() => {
                            generateRuleCards();
                            add_tap_to_run_rules_to_selected_zones();
                            });
                        }

                    } else {
                        console.error('Error:', response.status);
                        // Handle error
                    }
                } catch (error) {
                    console.error('Error:', error);
                    // Handle network error or other unexpected errors
                }
            }
        }
    }


    // Show page
    showPage(page_query) {
        document.querySelectorAll(".page").forEach(page => page.classList.remove("active-page"));
        // Show the selected page
        const page = document.querySelector(page_query);
        if (page) {
            page.classList.add('active-page');
        }

        // Update page history
        if (this.pageHistory[this.currentPageIndex] !== page_query) {
            this.currentPageIndex++;
            this.pageHistory = this.pageHistory.slice(0, this.currentPageIndex);
            this.pageHistory.push(page_query);
        }

        // updateNavigationButtons(pageId);
    }



    // render scene wizard page.
    render(container) {
        const scene_wizard_el = document.querySelector('.scene-wizard-page');
        if(scene_wizard_el){
        scene_wizard_el.remove();
        }
        container.appendChild(this.page_dom);
    }

    render_scene_wizard_page(rule_id=null, container_query_selector='.container-fluid'){
        if(rule_id === null){
            // this.rule_config_type = "";
            // // render empty scene wizard page
            // this.page_dom = this.create_page_element();
            // this.render(document.querySelector(container_query_selector));
            // this.addEventListeners(this.page_dom);
            // this.init_sortables_lists();
            // this.init_color_picker();
            // // this.init_scheduler_modal();
            // this.show_if_condition_empty_item();
            // this.show_then_actions_empty_item();
            // this.init_if_condition_options_modal();
            // this.init_then_action_options_modal();
            // this.enable_if_condition_tap_to_run_option();
            // this.init_scheduler_modal();
            // this.init_delay_modal();

            this.if_conditions_list = [];
            this.then_actions_list = [];
            this.decision_expr = "or";
            this.rule_name = "";
            this.rule_style_color = '#FFB5A7';
            this.add_to_home_status = false;
            this.showSceneRuleInZones = new Set();
            this.rule_config_type = "";
            this.currentMode = "if"; // "if" or "then"
            this.selectedDevice = null;
            this.selectedDPF = null;
            this.pageHistory = [];
            this.currentPageIndex = -1;
            this.selectedDPFs = [];
            this.editing_item = {
                    item_category: '',
                    item_type: '',
                    item_index: ''
                }
            this.in_editing_mode = false;
            this.in_editing_linkage_rule = false;
            this.in_editing_linkage_rule_index = null;
            this.in_editing_linkage_rule_type = "";
            this.rule_config_type = "";

            // clear if-conditions-sortable-list
            const ifConditionsList = this.page_dom.querySelector('.if-conditions-sortable-list');
            while (ifConditionsList.firstChild) {
                ifConditionsList.removeChild(ifConditionsList.firstChild);
            }

            // clear then-actions-sortable-list
            const thenActionsList = this.page_dom.querySelector('.then-actions-sortable-list');
            while (thenActionsList.firstChild) {
                thenActionsList.removeChild(thenActionsList.firstChild);
            }

            // reset decision expression select input
            const decisionExprSelect = this.page_dom.querySelector('#decision_expr_select_input');
            decisionExprSelect.value = 'or';

            // reset rule name input
            const ruleNameInput = this.page_dom.querySelector('#scene_name_input');
            ruleNameInput.value = '';

            // reset color picker
            const colorPicker = this.page_dom.querySelector('#scene_color_picker_input');
            colorPicker.value = "#FFB5A7";

            // reset page header name
            const pageHeader = this.page_dom.querySelector('.scene-wizard-header-name');
            pageHeader.textContent = 'New Scene';
            
            this.scene_wizard_delete_button.style.display = "none";
            
            this.in_sending_request_progress = false;
            this.scene_wizard_delete_button.querySelector('span').style.display = "none";
            this.scene_wizard_save_button.querySelector('span').style.display = "none";
            this.scene_wizard_save_button.disabled = false;
            // this.scene_wizard_save_button.textContent = "Save";


            this.show_if_condition_empty_item();
            this.show_then_actions_empty_item();
            this.enable_if_condition_tap_to_run_option();

            this.disable_add_to_home();
            this.disable_add_to_zones();

            this.enable_if_add_button();

            this.reset_add_to_home_switch();
            this.reset_add_to_zones_checkboxes();

        }
        else {
            const rule_config = linkage_rules.find(rule => rule.rule_uuid === rule_id);
            if(rule_config) {
                this.in_editing_linkage_rule = true;
                this.in_editing_linkage_rule_index = rule_config["index"];
                this.in_editing_linkage_rule_type = rule_config.type;
                // this.page_dom = this.create_page_element({scene_header_name:"Edit Scene", mode:"edit"});
                // this.render(document.querySelector(container_query_selector));

                this.currentMode = "if"; // "if" or "then"
                this.selectedDevice = null;
                this.selectedDPF = null;
                this.pageHistory = [];
                this.currentPageIndex = -1;
                this.selectedDPFs = [];
                this.editing_item = {
                        item_category: '',
                        item_type: '',
                        item_index: ''
                    }
                this.in_editing_mode = false;
                
                const ifConditionsList = this.page_dom.querySelector('.if-conditions-sortable-list');
                while (ifConditionsList.firstChild) {
                    ifConditionsList.removeChild(ifConditionsList.firstChild);
                }

                // clear then-actions-sortable-list
                const thenActionsList = this.page_dom.querySelector('.then-actions-sortable-list');
                while (thenActionsList.firstChild) {
                    thenActionsList.removeChild(thenActionsList.firstChild);
                }

                const pageHeader = this.page_dom.querySelector('.scene-wizard-header-name');
                pageHeader.textContent = 'Edit Scene';

                
                this.scene_wizard_delete_button.style.display = "flex";

                this.decision_expr = rule_config['decision_expr'];
                const decision_expr_select_input_element = this.page_dom.querySelector('#decision_expr_select_input');
                decision_expr_select_input_element.value = rule_config['decision_expr'];

                this.rule_name = rule_config.name;
                const rule_name_input_el = this.page_dom.querySelector('.scene-wizard-linkage-rule-name #scene_name_input');
                rule_name_input_el.value = this.rule_name;

                this.rule_style_color = rule_config.style.color;
                const rule_color_input_el = this.page_dom.querySelector('.scene-wizard-linkage-rule-style #scene_color_picker_input');
                rule_color_input_el.value = this.rule_style_color;

                this.in_sending_request_progress = false;
                
                this.scene_wizard_save_button.querySelector('span').style.display = "none";
                this.scene_wizard_save_button.disabled = false;
                // this.scene_wizard_save_button.textContent = "Save";
                
                this.scene_wizard_delete_button.querySelector('span').style.display = "none";
                this.scene_wizard_delete_button.disabled = false;
                // this.scene_wizard_delete_button.textContent = "Delete";
                
                
                this.add_to_home_status = rule_config.add_to_home_status;
                const linkage_rule_add_to_home_switch_element = this.page_dom.querySelector('#scene-wizard-add-to-home-switch');
                if(this.add_to_home_status === "true"){
                    this.enable_add_to_home();
                    linkage_rule_add_to_home_switch_element.checked = true;
                }
                else{
                    this.disable_add_to_home();
                    linkage_rule_add_to_home_switch_element.value = false;

                }
                // check zone existance. it is possible to remove or changed one or more zone properties after creation of each linkage rules. so selected
                // zone data in linkage rule json file not be valid and exist anymore.
                this.showSceneRuleInZones = new Set();
                all_home_zones.forEach(zone=>{
                    if(rule_config.show_scene_rule_in_zones && rule_config.show_scene_rule_in_zones.length > 0){
                        rule_config.show_scene_rule_in_zones.forEach(selected_zone=>{
                            if(zone.zone_uuid === selected_zone){
                                this.showSceneRuleInZones.add(selected_zone);
                            }
                        });
                    }
                });
                if(rule_config.show_scene_rule_in_zones && rule_config.show_scene_rule_in_zones.length > 0){
                    this.init_add_to_zones_checkboxes();
                    this.enable_add_to_zones();
                } else {
                    this.reset_add_to_zones_checkboxes();
                    this.disable_add_to_zones();
                }

                this.rule_config_type = rule_config.type;
                
                // make linkage-rules error proof by checking device existance.
                // TODO: check device_report elements and verify device is still exist. if not, don't copy it to if_conditions_list
                this.if_conditions_list = rule_config.conditions;
                // TODO: check device_issue elements and verify device is still exist. if not, don't copy it to then_actions_list
                this.then_actions_list = rule_config.actions;

                if (this.if_conditions_list.length === 0){
                    this.show_if_condition_empty_item();
                }
                if(this.then_actions_list.length === 0){
                    this.show_then_actions_empty_item();
                }

                // this.init_sortables_lists();
                // this.init_color_picker();
                // this.init_if_condition_options_modal();
                // this.init_then_action_options_modal();
                this.enable_if_condition_tap_to_run_option();
                // this.init_scheduler_modal();
                // this.init_delay_modal();

                // create conditions and actions cards

                // if conditions list
                this.if_conditions_list.forEach(condition => {
                    if (condition.entity_type === "tap-to-run"){
                        const tap_to_run_element = this.create_tap_to_run_item();
                        const list_el = document.createElement('li');
                        list_el.dataset.itemCategory= "if-condition-item";
                        list_el.dataset.itemIndex= parseInt(condition.code) - 1;
                        list_el.dataset.itemType= "tap-to-run";
                        list_el.appendChild(tap_to_run_element);
                        const if_condition_sortable_list_el = this.page_dom.querySelector('.if-conditions-sortable-list');
                        if_condition_sortable_list_el.appendChild(list_el);
                        this.show_if_actions_sortable_list();
                        this.rule_config_type = "scene";
                        // this.update_event_listeners();
                        // this.disable_if_add_button();
                        this.disable_if_add_button();
                        this.enable_add_to_home();
                        this.enable_add_to_zones();
                    }
                    else if (condition.entity_type === "timer"){
                        // this.scheduler_modal_reset_modal_values();
                        // this.if_condition_options_modal.hide();
                        // this.scheduler_bootstrap_modal_instance.show();
                        this.disable_add_to_home();
                        this.disable_add_to_zones();

                        let scheduler_card_title = "";
                        let scheduler_card_sub_title = "";

                        const date = condition["expr"]["date"];
                        const time = condition["expr"]["time"];
                        const loops = condition["expr"]["loops"];

                        if (loops === "once") {

                            scheduler_card_title = `Scheduler: ${time}`;
                            scheduler_card_sub_title = `${date}`;
                        } else {

                            scheduler_card_title = `Scheduler: ${time}`;
                            scheduler_card_sub_title = this.getWeekdayString(loops);
                        }

                        const scheduler_item = this.create_scheduler_item(scheduler_card_title, scheduler_card_sub_title);
                        const list_el = document.createElement('li');
                        list_el.dataset.itemCategory = "if-condition-item";
                        list_el.dataset.itemIndex = parseInt(condition.code) - 1;
                        list_el.dataset.itemType = "scheduler";
                        list_el.appendChild(scheduler_item);
                        const if_condition_sortable_list_el = this.page_dom.querySelector('.if-conditions-sortable-list');
                        if_condition_sortable_list_el.appendChild(list_el);
                        this.show_if_actions_sortable_list();
                        this.rule_config_type = "automation";
                        this.disable_if_condition_tap_to_run_option();
                        // add condition to rule config
                        // this.update_event_listeners();
                    }
                    else if (condition.entity_type === "device_report"){

                        let comparasion_string = "";

                        if (condition.expr.comparator === ">"){
                            comparasion_string = "greater than";
                        }
                        else if (condition.expr.comparator === "<"){
                            comparasion_string = "less than";
                        }
                        else if (condition.expr.comparator === "=="){
                            comparasion_string = "equal";
                        }
                        const device = all_home_devices.find(device => device.device_uuid === condition.device_uuid);
                        const device_zone = all_home_zones.find(zone => zone.zone_uuid === device.zone_uuid);
                        const desire_dpf = device.dataPointFunctions.find(dpf => dpf.function_name === condition.expr.status_code);
                        const condition_device_card_element = this.create_device_item(device.name, device_zone.zone_name, desire_dpf.display_name, comparasion_string, condition.expr.status_value);
                        const condition_list_el = document.createElement('li');
                        condition_list_el.dataset.itemCategory = "if-condition-item";
                        condition_list_el.dataset.itemIndex = parseInt(condition.code) - 1;
                        condition_list_el.dataset.itemType = "device_report";
                        condition_list_el.appendChild(condition_device_card_element);
                        const if_condition_sortable_list_el = this.page_dom.querySelector('.if-conditions-sortable-list');
                        if_condition_sortable_list_el.appendChild(condition_list_el);
                        this.show_if_actions_sortable_list();
                        this.rule_config_type = "automation";
                        this.disable_add_to_home();
                        this.disable_add_to_zones();
                        this.disable_if_condition_tap_to_run_option();
                    }
                })


                this.then_actions_list.forEach(action => {
                    if (action.action_executor === "delay"){
                        const delay_second = parseInt(action.executor_property.delay_seconds);
                        const [hours, minutes, seconds] = this.secondsToTimeParts(delay_second);
                        let delay_card_sub_title = this.formatTimeToText(`${hours}:${minutes}:${seconds}`);

                        const delay_card_element = this.create_delay_action_item(delay_card_sub_title);
                        const list_el = document.createElement('li');
                        list_el.dataset.itemCategory = "then-action-item";
                        list_el.dataset.itemIndex = parseInt(action.code) - 1;
                        list_el.dataset.itemType = "delay";
                        list_el.appendChild(delay_card_element);
                        const then_actions_sortable_list_el = this.page_dom.querySelector('.then-actions-sortable-list');
                        then_actions_sortable_list_el.appendChild(list_el);
                        this.show_then_actions_sortable_list();
                        // this.update_event_listeners();
                    }
                    else if (action.action_executor === "device_issue"){


                        let comparasion_string = "equal";

                        const device = all_home_devices.find(device => device.device_uuid === action.device_uuid);
                        const device_zone = all_home_zones.find(zone => zone.zone_uuid === device.zone_uuid);
                        const desire_dpf = device.dataPointFunctions.find(dpf => dpf.function_name === action.executor_property.function_code);
                        const action_device_card_element = this.create_device_item(device.name, device_zone.zone_name, desire_dpf.display_name, comparasion_string, action.executor_property.function_value);
                        const action_list_el = document.createElement('li');
                        action_list_el.dataset.itemCategory = "then-action-item";
                        action_list_el.dataset.itemIndex = parseInt(action.code) - 1;
                        action_list_el.dataset.itemType = "device_issue";
                        action_list_el.appendChild(action_device_card_element);
                        const then_actions_sortable_list_el = this.page_dom.querySelector('.then-actions-sortable-list');
                        then_actions_sortable_list_el.appendChild(action_list_el);
                        this.show_then_actions_sortable_list();

                    }
                })



                this.update_event_listeners();

            }
        }
    }



}
