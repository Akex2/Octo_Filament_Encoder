/*
 * View model for Octo_Filament_Encoder
 *
 * Author: Alex
 * License: AGPLv3
 */
Octo_encoder = {};
 Octo_encoder.Printers = { 'current_profile_guid': function () {return null;}}
Octo_encoderViewModel = {};

$(function () {
    // Finds the first index of an array with the matching predicate


    Octo_encoder.displayPopup = function (options) {
        new PNotify(options);
    };

    Octo_encoder.Popups = {};
    Octo_encoder.displayPopupForKey = function (options, key) {
        if (key in Octo_encoder.Popups) {
            Octo_encoder.Popups[key].remove();
        }
        Octo_encoder.Popups[key] = new PNotify(options);
    };



    Octo_encoderViewModel = function (parameters) {
        var self = this;
        Octo_encoder.Globals = self;
        // Handle Plugin Messages from Server
        self.onStartupComplete = function () {
            console.log("Startup Complete")
            //self.getInitialState();

        };
        self.onDataUpdaterPluginMessage = function (plugin, data) {
            console.log(plugin);
            if (plugin !== "octo_encoder") {
                console.log('Octo_encoder.js return');
                return;
            }
            console.log('Octo_encoder.js not return');
            switch (data.type) {
                case "settings-changed":
                    {
                        // Was this from us?
                        if (self.client_id !== data.client_id && self.is_admin())
                        {
                            if (!Octo_encoder.IsShowingSettingsChangedPopup)
                            {
                                Octo_encoder.IsShowingSettingsChangedPopup = true;
                                if (confirm("A settings change was detected from another client.  Reload settings?"))
                                {
                                    Octo_encoder.Settings.loadSettings();
                                }
                                Octo_encoder.IsShowingSettingsChangedPopup = false;
                            }
                        }
                        self.updateState(data);
                    }
                    break;
                case "state-loaded":
                    {
                        //console.log('Octo_encoder.js - state-loaded');
                        self.updateState(data);
                    }
                    break;
                case "state-changed":
                    {
                        //console.log('Octo_encoder.js - state-changed');
                        self.updateState(data);
                    }
                    break;
                case "popup":
                    {
                        //console.log('Octo_encoder.js - popup');
                        var options = {
                            title: 'Octo_encoder Notice',
                            text: data.msg,
                            type: 'notice',
                            hide: true,
                            addclass: "Octo_encoder",
                            desktop: {
                                desktop: true
                            }
                        };
                        Octo_encoder.displayPopup(options);
                    }
                    break;
                case "popup-error":
                    {
                        //console.log('Octo_encoder.js - popup-error');
                        self.updateState(data);
                        var options = {
                            title: 'Octo_encoder Startup Failed',
                            text: data.msg,
                            type: 'error',
                            hide: false,
                            addclass: "Octo_encoder",
                            desktop: {
                                desktop: true
                            }
                        };
                        Octo_encoder.displayPopup(options);
                        break;
                    }
                case "warning":
                    //console.log("A warning was sent to the plugin.")
                        var options = {
                            title: 'Octo_encoder - Warning',
                            text: data.msg,
                            type: 'notice',
                            hide: true,
                            addclass: "Octo_encoder"
                        };
                        Octo_encoder.displayPopup(options, "warning");
                default:
                    {
                        //console.log('Octo_encoder.js - passing on message from server.  DataType:' + data.type);
                    }
            }
        };


    };
    OCTOPRINT_VIEWMODELS.push([
        Octo_encoderViewModel
        , ["loginStateViewModel", "printerStateViewModel"]
        , ["#Octo_encoder"]
    ]);



});