document.addEventListener('DOMContentLoaded', function() {
    var players = 2;
    names(players);
});

function playerCount() {
    const playerCount = document.getElementById("player_count");
    players = Number(playerCount.options[playerCount.selectedIndex].value);
    names(players);
};

function names(players) {
    document.querySelector("#name_inputs").innerHTML = '';
    for (let i = 0; i < players; i++) {
        var name = document.createElement("input");
        name.type = "text";
        name.id = "player_" + (i + 1);
        name.name = "player_names"
        name.className = "player_input"
        
        var name_label = document.createElement("label");
        name_label.for = name.id;
        name_label.innerHTML = "Player " + (i + 1) + ":";
        document.querySelector("#name_inputs").append(name_label);
        document.querySelector("#name_inputs").append(name);
        
        var br = document.createElement("br");
        document.querySelector("#name_inputs").append(br);
      }
};