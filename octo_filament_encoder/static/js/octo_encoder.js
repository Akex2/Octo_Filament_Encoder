/*
 * View model for Octo_Filament_Encoder
 *
 * Author: Alex
 * License: AGPLv3
 */
Octo_encoder = {};
 Octo_encoder.Printers = { 'current_profile_guid': function () {return null;}}
Octo_encoderViewModel = {};



$(function (parameters) {
    // Finds the first index of an array with the matching predicate
    self.settings = parameters[0];


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

    Octo_encoder.graphData = new Object;
    Octo_encoder.graphData.x = [];
    Octo_encoder.graphData.y = [];
    Octo_encoder.graphData.type = 'scatter';
    Octo_encoder.drawGraph = function(tehDatas) {
        //console.log(tehDatas)
        Plotly.newPlot('tester', tehDatas);
    }



    Octo_encoderViewModel = function (parameters) {
        var self = this;
        self.settingsViewModel = parameters[0]
        self.controlViewModel = parameters[1];
        self.Octo_Filament_EncoderViewModel = parameters[2];
        Octo_encoder.Globals = self;
        /*
        
        */
        // Handle Plugin Messages from Server
        self.onAfterBinding = function() { //self.onStartupComplete = function () {
            //console.log("Startup Complete")
            enable = self.settingsViewModel.settings.plugins.octo_encoder.enable();
            enable_graph = self.settingsViewModel.settings.plugins.octo_encoder.enable_graph();
            calibrated = self.settingsViewModel.settings.plugins.octo_encoder.calibrated();
            console.log("enable", enable)
            console.log("enable_graph", enable_graph)
            console.log("calibrated", calibrated)
            if ((enable == false) || (enable_graph == false) || (calibrated == false))
            {
                $('#tab_plugin_octo_encoder_link').hide();
            }
            //$('#control_link,#temp_link').hide();
            //$('#tab_plugin_octo_encoder_link').hide();
            //self.getInitialState();

        };
        self.onDataUpdaterPluginMessage = function (plugin, data) {
            //console.log(plugin);
            //console.log(self.settingsViewModel.settings.plugins.octo_encoder.autocalib());
            if (plugin !== "octo_encoder") {
                //console.log(self.settingsViewModel.autocalib());
                
                return;
            }
            //console.log('Octo_encoder.js not return');
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
                case "x_graph":
                    {
                        //console.log('Octo_encoder.js - graph');
                        // de python : data = {"type": "x_graph", "msg": encoder_step
                        if (Octo_encoder.graphData.y.length > 20) {
                            Octo_encoder.graphData.y.shift();
                        }
                        Octo_encoder.graphData.y.push(parseInt(data.msg));
                        Octo_encoder.graphData.x = [];
                        for (var iii = 0 ; iii < Octo_encoder.graphData.y.length ; iii++) {
                            Octo_encoder.graphData.x.push(iii);
                        }
                        //Octo_encoder.drawGraph(Octo_encoder.graphData);
                        
                        //console.log(Octo_encoder.graphData)
                        var trace1 = {
                              x: Octo_encoder.graphData.x,
                              y: Octo_encoder.graphData.y,
                              type: 'scatter'
                            };
                        var data = [trace1];
                        var layout = {
                              autosize: false,
                              width: 600,
                              height: 500,
                              margin: {
                                l: 25,
                                r: 2,
                                b: 20,
                                t: 20,
                                pad: 4
                              },
                              //paper_bgcolor: '#7f7f7f',
                              //plot_bgcolor: '#c7c7c7'
                            };

                        Plotly.newPlot('tester', data, layout);
                        
                    }
                    break;
                case "popup":
                    {
                        //console.log('octolapse.js - popup');
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
                        Octo_encoder.displayPopup(options, "warning");
                    }
                    break;
                case "popup_success":
                    {
                        //console.log('Octo_encoder.js - popup');
                        var options = {
                            title: 'Octo_encoder Notice',
                            text: data.msg,
                            type: 'success',
                            hide: true,
                            addclass: "Octo_encoder",
                            desktop: {
                                desktop: true
                            }
                        };
                        Octo_encoder.displayPopup(options);
                    }
                    break;
                case "popup_info":
                    {
                        //console.log('Octo_encoder.js - popup');
                        var options = {
                            title: 'Octo_encoder Notice',
                            text: data.msg,
                            type: 'info',
                            hide: true,
                            addclass: "Octo_encoder",
                            desktop: {
                                desktop: true
                            }
                        };
                        Octo_encoder.displayPopup(options);
                    }
                    break;
                case "popup_error":
                    {
                        //console.log('Octo_encoder.js - popup-error');
                        //self.updateState(data);
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
        , ["settingsViewModel", "printerStateViewModel", "loginStateViewModel"]
        , ["#settings_plugin_octo_encoder", "controlViewModel", "Octo_Filament_Encoder_ViewModel", "#Octo_encoder"]
    ]);



});
