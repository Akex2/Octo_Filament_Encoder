/*
 * View model for Octo_Filament_Encoder
 *
 * Author: Alex
 * License: AGPLv3
 */
$(function() {
    function Octo_encoderViewModel(parameters) {
        var self = this;
        self.onEventSettingsUpdated = function (payload) {
            console.log("mesh_data_z"+'\n'+"store_data+"'\n'+"mesh_data_x"+'\n'+"mesh_data_y"+'\n'+"mesh_data_z_height");
        }
        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }
    self.onEventSettingsUpdated = function (payload) {
        console.log("mesh_data_z"+'\n'+"store_data+"'\n'+"mesh_data_x"+'\n'+"mesh_data_y"+'\n'+"mesh_data_z_height");
    }
    //var ctx = document.getElementById("myChart").getContext('2d');

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: Octo_encoderViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "loginStateViewModel", "settingsViewModel"],
        // Elements to bind to, e.g. , ...
        elements: [ #settings_plugin_octo_encoder, #tab_plugin_octo_encoder ]
    });
});
