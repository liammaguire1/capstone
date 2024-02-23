document.addEventListener('DOMContentLoaded', function() { 

    // Initialize variables
    const players = JSON.parse(document.querySelector("#gameData").getAttribute('players'));
    var timer = Number(JSON.parse(document.querySelector("#gameData").getAttribute('timer')));
    var turn = 0;
    var id;
    var api_ids;
    var mode = 'initial';
    
    function guess(api_data) {
        // GET request to /game_api
        fetch(`/game_api/${api_data}`)
        .then(response => response.json())
        .then(data => {
            
            // Establish intial html
            document.querySelector("#time").innerHTML = timer;
            document.querySelector("#current-player").innerHTML = players[turn] + ",";
            document.querySelector("#instruction").innerHTML = data.instruction;

            // Store data from game_api call
            id = data.id;
            api_ids = [data.ids];

        })
    }

    // Call guess function when guess is submitted
    document.querySelector('#guess_button').onclick = function() {
        
        // Set mode based on instruction HTML
        if (mode == 'initial' || mode == 'work_to_actor') {
            mode = 'actor_to_work';
        } else {
            mode = 'work_to_actor';
        }

        // Get user input/answer
        answer = document.querySelector('#guess_text').value;

        // Call game_api
        console.log(id);
        const api_data = [mode, answer, id, api_ids]
        guess(api_data);

        // Decrement timer
        setInterval(function() {
            --timer;
            document.querySelector("#time").innerHTML = timer;
        }, 1000);
    }

      // Initial load
      const api_data = ['initial']
      guess(api_data);
            
});

