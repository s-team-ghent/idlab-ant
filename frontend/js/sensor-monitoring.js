// Websocket to retrieve session data from
const wsUri = "ws://localhost:8765";

// Text of start/end button
const button_start_text = "Start Session";
const button_end_text = "End Session";

let websocket;

let plot_intervals = []; // Intervals updating the plots
// Object keeping track of mapping from ANT device ID to rider name. Mapping will be displayed in table on webpage
let assigned_sensors = {};

// Dynamic elements in the webpage
let elements = {};
window.addEventListener("load", () => {
    elements = {
        session_button: document.getElementById("session-button"),
        output: document.getElementById("output"),
        plot_container_value: document.getElementById("plot-container-value"),
        dashboard_container: document.getElementById("dashboard-container"),
        sensor_input: document.getElementById("ant-id"),
        rider_input: document.getElementById("rider-name"),
        mapping_table: document.getElementById("mapping-table"),
        plot_type_checkbox: document.getElementById("plot-type")
    };
}, false);

/**
 * - Create a connection to the websocket
 * - Send server request to start/stop session
 * - Initialize the dashboard
 */
function connect() {
    const button = elements.session_button; // start/stop button
    const endpoint = button.value == button_start_text ? "start" : "end"; // Endpoint to send server request to
    
    if (button.value == button_start_text) {
        // Start a new session
        openWebSocket();
        removePlots();
    }
    else {
        // Stop the current session
        closeWebSocket();
    }
    // Change start/stop button text
    button.value = button.value == button_start_text ? button_end_text : button_start_text;
    button.className = button.value == button_start_text ? "btn btn-success" : "btn btn-danger";
}

function convertTimestamp(ts) {
    // Timestamp given by WASP-N is in CDT timezone
    // CAUTION: WASP aggregator does not synchronise time when disconnected form internet. Therefore, use current timestamp to update real-time plots.
    return new Date();
}

/**
 * Generate ID of dashboard item value
 * @param device_id: ID of the dashboard item value
 * @param data_type: Type of the data displayed in the dashboard item value
 */
function dashboardIdValue(device_id, data_type) {
    return "dashboard_" + device_id + "_" + data_type + "_value";
}

function dashboardIdUnit(device_id, data_type){
    return "dashboard_" + device_id + "_" + data_type + "_unit";
}

function headerIdManufacturer(device_id){
    return "sensor_container_header_manufacturer_"+device_id;

}

/**
 * Generate ID of dashboard item device type
 * @param device_id: ID of the dashboard item device type
 * @param data_type: Type of the data displayed in the dashboard item device type
 */
function dashboardIdDevice(device_id, data_type) {
    return "dashboard_" + device_id + "_" + data_type + "_device";
}

/**
 * Generate layout for plot
 * @param data: Data to create plot for
 * @param data_type: Type of the data to create plot for
 */
function plotLayout(data, data_type) {
    // Create plot between previous minute and next minute
    const now = new Date();
    var start = now.setMinutes(now.getMinutes() - 1);
    var end = now.setMinutes(now.getMinutes() + 1);

    return {
            xaxis: {
                type: "date",
                range: [start, end],
                title: "Time"
            },
            yaxis: {
                // Unit of displayed data is included in retrieved data, except for the RSSI value
                title: data_type_units[data_type]
            },
            // Replace the device number with the name of rider if device assigned
            title:  data_type + " (" + (devices[data.extendedDeviceID] ? devices[data.extendedDeviceID] : manufacturers[data.manufacturer_id]) + "): " + (assigned_sensors[data.extendedDeviceID] ? assigned_sensors[data.extendedDeviceID].rider : data.extendedDeviceID + (riders[data.extendedDeviceID] ? " (" + riders[data.extendedDeviceID] + ")" : ""))
        }
}

/**
 * Initialize plots and dashboard for new device
 * @param data: First data packet received for this device
 * @param data_type: Type of data that needs to be shown in plots and dashboard
 */
function createPlot(data, data_type, data_container) {
    // Create div element for plot
    //plot_element = document.createElement("div");
    //plot_element.id = plotId(data.extendedDeviceID, data_type);
    //plot_element.setAttribute("style","display:inline-block;width:45%");
    //elements.plot_container_value.appendChild(plot_element);

    // Initialize plot with empty data, first data point will be added by a plot update
    //const plot_data = [{
    //        x: [],
    //        y: [],
    //        mode: "line",
    //    }];
    //plot_data[0]["type"] = "scatter";

    // Add plot to created div
    //Plotly.newPlot(plotId(data.extendedDeviceID, data_type), plot_data, plotLayout(data, data_type));

    // Update plot each second
    //plot_intervals.push(setInterval(function() {
    //    Plotly.relayout(plotId(data.extendedDeviceID, data_type), plotLayout(data, data_type));
    //}, 1000));

    var widget = createSensorValueWidget(data, data_type)
    data_container.appendChild(widget)
}

/**
 * Update plot with given data message
 */
function updatePlot(sensor_json) {
    // Sample data packet
    /*
        {
            "deviceID": 104, 
            "extendedDeviceID": 104, 
            "transmissionType": 5, 
            "timestamp": 1630397249.1180897, 
            "deviceType": "MuscleOxygen", 
            "sensorData": {"SMO2": 20.0, "Saturation": 50.0, "Previous Saturation": 50.0}
        }
    */
    // Create a dashboard container for extended device id if not yet exists
    var sensorContainer = document.getElementById("sensor_container_"+sensor_json.extendedDeviceID);
    if(!sensorContainer){
        createSensorContainer(sensor_json)
    }
    sensorContainer = document.getElementById("sensor_container_data_"+sensor_json.extendedDeviceID);
    // Add plots for all retrieved sensors
    for (const data_type of Object.keys(sensor_json.sensorData)) {
        // Update plot and dashboard only for valid data types
        if (!data_types.has(data_type)) continue;
        
        // If plot and dashboard for device data type not already exist, they should be created
        if (!document.getElementById(dashboardIdValue(sensor_json.extendedDeviceID, data_type))) {
            createPlot(sensor_json, data_type, sensorContainer);
        }
        
        // Add received data value to plot data
        //const update = {
        //    x: [[convertTimestamp(sensor_json["timestamp"])]],
        //    y: [[sensor_json.sensorData[data_type]]]
        //}

        // Update plot
        //Plotly.extendTraces(plotId(sensor_json.extendedDeviceID, data_type), update, [0]);

        // Update sensor type in table with assigned sensors
        if (assigned_sensors[sensor_json.extendedDeviceID]) {
            assigned_sensors[sensor_json.extendedDeviceID].type = sensor_json["deviceType"];
            document.getElementById(assigned_sensors[sensor_json.extendedDeviceID].type_cell).innerHTML = sensor_json["deviceType"];
            document.getElementById(assigned_sensors[sensor_json.extendedDeviceID].type_cell).innerHTML = sensor_json["deviceType"];
        }

        // Update manufacturer info if required
        if (sensor_json['manufacturer_id']){
            document.getElementById(headerIdManufacturer(sensor_json.extendedDeviceID)).innerHTML = '<i class="fas fa-industry"></i> '+manufacturers[sensor_json['manufacturer_id']]
        }

        if (document.getElementById(dashboardIdValue(sensor_json.extendedDeviceID, data_type))) {
            // Update dashboard value
            document.getElementById(dashboardIdValue(sensor_json.extendedDeviceID, data_type)).innerHTML = Math.round(sensor_json.sensorData[data_type]);
            // Check if unit is recognized and add it to its container
            var unitContainer = document.getElementById(dashboardIdUnit(sensor_json.extendedDeviceID, data_type))
            if(unitContainer){
                if(data_type_units[data_type]){
                    unitContainer.innerHTML = data_type_units[data_type]
                }
            }
            // Replace device id by rider name if device is assigned to rider
            if (assigned_sensors[sensor_json.extendedDeviceID]) {
                document.getElementById("sensor_container_header_attached_rider_"+sensor_json.extendedDeviceID).innerHTML = "<i class='fas fa-user'></i> "+(assigned_sensors[sensor_json.extendedDeviceID]?assigned_sensors[sensor_json.extendedDeviceID].rider:"no rider attached");
            }
        } 
    }
}

/**
 * Terminate plot updates each second
 */
function stopPlots() {
    plot_intervals.forEach(plot_interval => {
        clearInterval(plot_interval);
    });
    plot_intervals = [];
}

/**
 * Assign device to a rider by mapping the device ID to the riders' name
 */
function assignSensor() {
    // Update mapping if it already exists
    if (assigned_sensors[elements.sensor_input.value]) {
        // Update device ID in mapping table
        document.getElementById(assigned_sensors[elements.sensor_input.value].sensor_cell).innerHTML = elements.sensor_input.value;
        // Update rider name in mapping table
        document.getElementById(assigned_sensors[elements.sensor_input.value].rider_cell).innerHTML = elements.rider_input.value;

        // Update rider name in mapping object
        assigned_sensors[elements.sensor_input.value].rider = elements.rider_input.value;
    }
    // Add new mapping to mapping object
    else {
        assigned_sensors[elements.sensor_input.value] = {
            rider: elements.rider_input.value, // Name of rider
            type: "", // Type of device (will be updated on first received message from device)
            sensor_cell: "td-sensor-" + elements.sensor_input.value, // ID of device ID cell in mapping table
            rider_cell: "td-rider-" + elements.sensor_input.value, // ID of rider name cell in mapping table
            type_cell: "td-type-" + elements.sensor_input.value // ID of device type cell in mapping table
        };

        // Create new row in mapping table
        const table_body = elements.mapping_table.getElementsByTagName('tbody')[0];
        const row = table_body.insertRow();
        row.id = "sensor-"+elements.sensor_input.value;

        // Add device id, rider name and device type cells to table
        function insertCell(text, id) {
            const cell = row.insertCell();
            cell.id = id;
            cell.innerHTML = text;
        }
        insertCell("", "td-type-" + elements.sensor_input.value);
        insertCell(elements.sensor_input.value, "td-sensor-" + elements.sensor_input.value);
        insertCell(elements.rider_input.value, "td-rider-" + elements.sensor_input.value);
        insertCell("<span class='remove-button' data-sensor_id='"+elements.sensor_input.value+"'></span>", "td-remove-"+elements.sensor_input.value);
    }
}

function removeRow(id){
    var element = document.getElementById("sensor-"+id);
    element.parentNode.removeChild(element);
}

$(document).on('click', 'span.remove-button', function(){
    var id = $(this).data('sensor_id');
    removeRow(id);
    delete assigned_sensors[id]
});

/**
 * Remove all plots
 */
function removePlots() {
    while (elements.plot_container_value.firstChild) {
        elements.plot_container_value.removeChild(elements.plot_container_value.firstChild);
    }
    while (elements.dashboard_container.firstChild) {
        elements.dashboard_container.removeChild(elements.dashboard_container.firstChild);
    }
}

/**
 * Create websocket and assign listeners
 */
function openWebSocket()
{
    websocket = new WebSocket(wsUri);
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };
}

/**
 * Close websocket and terminate plot updates
 */
function closeWebSocket() {
    websocket.close();
    stopPlots();
}

/**
 * Terminate plot updates when websocket connection is closed
 */
function onClose(evt)
{
    stopPlots();
}

/**
 * Handle received messages from websocket
 */
function onMessage(evt)
{  
    // Update plots and dashboard
    updatePlot(JSON.parse(evt.data));
}

function onError(evt)
{
    writeToScreen('<span style="color: red;">ERROR:</span> ' + evt.data);
}

/**
 * Write a message to the output element
 */
function writeToScreen(message)
{
    var pre = document.createElement("p");
    pre.style.wordWrap = "break-word";
    pre.innerHTML = message;
    elements.output.appendChild(pre);
}

function createSensorContainer(sensor_json){
    var container = document.createElement("div")
    container.setAttribute("id", "sensor_container_"+sensor_json.extendedDeviceID)
    container.setAttribute("class", "card")
    var header = document.createElement("div")
    header.setAttribute("class", "d-flex sensor_container_header card-header justify-content-center")
    header.setAttribute("id", "sensor_container_header_"+sensor_json.extendedDeviceID)

    var extendedDeviceIdContainer = document.createElement("div")
    extendedDeviceIdContainer.setAttribute("class", "sensor_container_header_deviceid")
    extendedDeviceIdContainer.setAttribute("data-bs-toggle", "collapse")
    extendedDeviceIdContainer.setAttribute("aria-controls", "sensor_container_data_wrapper_"+sensor_json.extendedDeviceID)
    extendedDeviceIdContainer.setAttribute("data-bs-target", "#"+"sensor_container_data_wrapper_"+sensor_json.extendedDeviceID)
    extendedDeviceIdContainer.setAttribute("id", "sensor_container_header_deviceid_"+sensor_json.extendedDeviceID)
    extendedDeviceIdContainer.innerHTML = "<span class='badge bg-info text-dark'>"+sensor_json.extendedDeviceID+"</span>"
    header.appendChild(extendedDeviceIdContainer)

    var manufacturerContainer = document.createElement("div")
    manufacturerContainer.setAttribute("class", "sensor_container_header_manufacturer")
    manufacturerContainer.setAttribute("id", "sensor_container_header_manufacturer_"+sensor_json.extendedDeviceID)
    manufacturerContainer.innerHTML = '<i class="fas fa-industry"></i> '+(sensor_json.manufacturer_id?sensor_json.manufacturer_id:"unknown mfg.")
    header.appendChild(manufacturerContainer)

    var attachedRiderContainer = document.createElement("div")
    attachedRiderContainer.setAttribute("class", "sensor_container_header_attached_rider")
    attachedRiderContainer.setAttribute("id", "sensor_container_header_attached_rider_"+sensor_json.extendedDeviceID)
    attachedRiderContainer.innerHTML = "<i class='fas fa-user'></i> "+(assigned_sensors[sensor_json.extendedDeviceID]?assigned_sensors[sensor_json.extendedDeviceID]:"no rider attached")
    header.appendChild(attachedRiderContainer)

    var dataContainer = document.createElement("div")
    dataContainer.setAttribute("data-parent", "#dasboard-container")
    dataContainer.setAttribute("id", "sensor_container_data_wrapper_"+sensor_json.extendedDeviceID)
    dataContainer.setAttribute("class", "collapse show")
    var dataContainerWrapper = document.createElement("div")
    dataContainerWrapper.setAttribute("class", "card-body row sensor_container_data show d-flex justify-content-center");
    dataContainerWrapper.setAttribute("id", "sensor_container_data_"+sensor_json.extendedDeviceID)
    dataContainer.appendChild(dataContainerWrapper)

    container.appendChild(header)
    container.appendChild(dataContainer)

    elements.dashboard_container.appendChild(container)
}

function createSensorValueWidget(data, data_type){
    dashboard_element = document.createElement("div");
    dashboard_element.setAttribute("class", "col col-md-3 sensor-value-widget")
    dashboard_element_device_type = document.createElement("div");
    dashboard_element_device_type.setAttribute("class", "sensor-value-widget-item sensor-value-widget-type")
    dashboard_element_device_type.innerHTML = (fa_datatype_class[data_type]?"<div class='sensor-value-logo'>"+fa_datatype_class[data_type]+"</div>":"")+"<div class='sensor-value-value'>"+data_type+"</div>";
    
    dashboard_element_value = document.createElement("div");
    dashboard_element_value.setAttribute("class","sensor-value-widget-item sensor-value-widget-value");
    unit = document.createElement("div")
    unit.setAttribute("class", "sensor-value-widget-value-unit")
    unit.id = dashboardIdUnit(data.extendedDeviceID, data_type);
    value = document.createElement("div")
    value.setAttribute("class", "sensor-value-widget-value-value")
    value.id = dashboardIdValue(data.extendedDeviceID, data_type);
    dashboard_element_value.appendChild(value)
    dashboard_element_value.appendChild(unit)

    dashboard_element.appendChild(dashboard_element_device_type);
    dashboard_element.appendChild(dashboard_element_value);

    return dashboard_element
}