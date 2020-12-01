
function update_spacecraft_list(is_decommission) {
            $.ajax({
                url: "/get-all-payloads",
                type: "GET",
                beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
                success: function(val) {
                    console.log(val)

                    let select = document.getElementById("particular-aircraft")
                    if(is_decommission === true) {
                        Object.keys(val).forEach((name) => {
                            value = document.getElementById(name)
                            select.remove(value)
                        })
                        return select
                    }
                    else {
                        Object.keys(val).forEach((name) => {
                            let option = document.createElement("option");
                            option.text = name;
                            option.value = name;
                            select.appendChild(option);
                        })
                    }

                 return select;

         }
      });
}

function payload_start_data() {
    console.log(document.getElementById('p_name').value)
    $.ajax({
         url: "/payload/start-data",
         data: {name: document.getElementById('p_name').value},
         type: "GET",
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {  }
      });
}

function payload_stop_data() {
    $.ajax({
         url: "/payload/stop-data",
         data: {name:document.getElementById('p_name').value},
         type: "GET",
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {
            update_spacecraft_list()
         }
      });
}

function payload_decommission() {
    $.ajax({
         url: "/payload/decommission",
         type: "GET",
         data: {name:document.getElementById('p_name').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() { update_spacecraft_list(true) }
      });
}

function get_deploy_payload() {
       $.ajax({
         url: "/launch-vehicle/create-payload",
         type: "GET",
         data: {name:document.getElementById('p_name').value, type: document.getElementById('type').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {
            $.ajax({
         url: "/launch-vehicle/deploy-payload",
         type: "GET",
         data: {
            name: document.getElementById('fname').value
         },
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function(val) {
            if (val.error) {
                alert(val.error)
            }
        }
      });
         }
      });

}

function get_lv_start_telemetry() {
    $.ajax({
         url: "/launch-vehicle/start-telemetry",
         type: "GET",
         data: {name:document.getElementById('fname').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success:function(val) { console.log(val)}
      });
}

function get_lv_stop_telemetry() {
    $.ajax({
         url: "/launch-vehicle/stop-telemetry",
         type: "GET",
         data: {name:document.getElementById('fname').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {  }
      });
}

function get_capture_telemetry() {
    $.ajax({
         url: "/launch-vehicle/capture-telemetry",
         type: "GET",
         data: {name:document.getElementById('fname').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {  }
      });
}

function get_deorbit() {
    $.ajax({
         url: "/launch-vehicle/deorbit",
         type: "GET",
         data: {name:document.getElementById('fname').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {  }
      });
}

function capture_payload_data() {
    $.ajax({
         url: "/payload/capture-payload-data",
         type: "GET",
         data: {name:document.getElementById('p_name').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() { }
      });
}

function get_payload_data() {
    $.ajax({
         url: "/payload/get-data",
         type: "GET",
         data: {name:document.getElementById('particular-aircraft').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function(val) {
            document.getElementById("show-data").innerHTML = val.type
            if (val.type == 'Spy') {
               document.getElementById("show-data").innerHTML = '<img src="static/img/space.jpg" alt="Space">'
            }
         }
      });
}

function get_lv_create_payload_data() {
    $.ajax({
         url: "/launch-vehicle/create-payload",
         type: "GET",
         data: {name:document.getElementById('p_name').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {}
      });
}

function get_p_capture_telemetry() {
    $.ajax({
         url: "/payload/capture-telemetry",
         type: "GET",
         data: {name:document.getElementById('p_name').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() { }
      });
}

function get_p_start_telemetry() {
    $.ajax({
         url: "/payload/start-telemetry",
         type: "GET",
         data: {name:document.getElementById('p_name').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() {}
      });
}

function get_p_stop_telemetry() {
    $.ajax({
         url: "/payload/stop-telemetry",
         type: "GET",
         data: {name:document.getElementById('p_name').value},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function() { }
      });
}

function get_dashboard_metrics() {
    $.ajax({
         url: "/dashboard-metrics",
         type: "GET",
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function(val) {
            if (document.getElementById("show-dashboards").value == 'active-spacecrafts') {
                document.getElementById("counts").innerHTML = val.active_spacecrafts
            }
            if (document.getElementById("show-dashboards").value == 'spacecrafts-waiting')  {
                document.getElementById("counts").innerHTML = val.waiting_to_launch_spacecrafts
            }
            if (document.getElementById("show-dashboards").value == 'empty')  {
                document.getElementById("counts").innerHTML = ""
            }
         }
      });
}


function get_launch_vehicle() {
    $.ajax({
         url: "/launch-vehicle/deploy",
         type: "GET",
         data: {"config-file":document.getElementById("lv-upload").value.split("\\").pop()},
         beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
         success: function(val) {

            setTimeout(() => {
                $.ajax({
                url: "/launch-vehicle/update-status",
                type: "GET",
                data: {name:document.getElementById('fname').value},
                beforeSend: function(xhr){xhr.setRequestHeader('accept', 'application/json');},
                success: function(val1) {
                }
             });
            }, 12000)

         }
      });
}

