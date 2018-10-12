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
                        
                        console.log(Octo_encoder.graphData)
                        var trace1 = {
                              x: Octo_encoder.graphData.x,
                              y: Octo_encoder.graphData.y,
                              type: 'scatter'
                            };
                        var data = [trace1];

                        Plotly.newPlot('tester', data);
                        
                    }
                    break;
                case "popup":
                    {
                        //console.log('Octo_encoder.js - popup');
                        var trace1 = {
                              x: [1, 2, 3, 4],
                              y: [10, 15, 13, 17],
                              type: 'scatter'
                            };

                        var trace2 = {
                              x: [1, 2, 3, 4],
                              y: [16, 5, 11, 9],
                              type: 'scatter'
                            };

                        var data = [trace1];

                        //Plotly.newPlot('tester', data);
                        //Plotly.react('tester', data);

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