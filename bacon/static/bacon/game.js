document.addEventListener('DOMContentLoaded', function() { 

    // Initialize variables
    const players = JSON.parse(document.querySelector("#gameData").getAttribute('players'));
    var timer = Number(JSON.parse(document.querySelector("#gameData").getAttribute('timer')));
    const TIMER = timer;
    var turn = Math.floor(Math.random() * 10);;
    var score = 0;
    var id;
    var api_ids;
    var mode = 'initial';
    var active = false;
    var pass = false;
    var game_over = false;
    const guessed = []
    
    function guess(api_data) {
        // GET request to /game_api
        fetch(`/game_api/${api_data}`)
        .then(response => response.json())
        .then(data => {

            // Handle pass/fail states
            pass = data.pass;
            if (pass == true) {
                id = data.id;
                api_ids = data.ids;
                turn++;
                score++
                timer = TIMER;
                guessed.push(data.successful_guess);

                document.querySelector("#guess_text").value = '';
                document.querySelector("#score").innerHTML = 'Score: ' + String(score - 1);
                document.querySelector("#current-player").innerHTML = players[turn % players.length] + "'s turn";
            } 

            // Assign html
            document.querySelector("#time").innerHTML = timer;
            document.querySelector("#instruction").innerHTML = data.instruction;

            // Incorrect guess
            if (data.instruction == 'Incorrect') {
                if (data.mode == 'work_to_actor') {
                    document.querySelector("#instruction").innerHTML = 'I don\'t think ' + guessed[guessed.length - 1] + ' was in ' + document.querySelector("#guess_text").value + '. Try another movie/tv show'
                } else {
                    document.querySelector("#instruction").innerHTML = 'I don\'t think ' + guessed[guessed.length - 1] + ' featured ' + document.querySelector("#guess_text").value + '. Try another actor'
                }
            }

        })
    }

    // Check for game over
    setInterval(function() {
        if (timer == 0) {
            guess(['game_over', (score - 1), players]);

            game_over = true;
            timer = -1;
            document.querySelector("#guess_form").style.display = 'none';
            document.querySelector("#instruction").style.display = 'none';
            document.querySelector("#time").style.display = 'none';
            document.querySelector("#play-again").style.display = 'block';
            document.querySelector("#current-player").innerHTML = 'Game over!';
        }
    }, 1000);

    // Call guess function when guess is submitted
    document.querySelector('#guess_button').onclick = function() {
        
        // Get user input/answer
        answer = document.querySelector('#guess_text').value;

        // Handle repeated answers
        if (guessed.includes(answer)) {
            document.querySelector("#instruction").innerHTML = 'Already used!';
            return
        }

        // Set mode
        if (pass == true) {
            if (mode == 'initial' || mode == 'work_to_actor') {
                mode = 'actor_to_work';
            } else {
                mode = 'work_to_actor';
            }
        }

        // Call game_api
        const api_data = [mode, answer, id, api_ids]
        guess(api_data);

        // Decrement timer
        if (active == false) {
            setInterval(function() {
                if (game_over == false) {
                    --timer;
                    document.querySelector("#time").innerHTML = timer;
                }
            }, 1000);
            active = true;
        }
        
    }

      // Initial load
      const api_data = ['initial']
      guess(api_data);

    // Restart game
    document.querySelector("#play-again").style.display = 'none';
    document.querySelector('#play-again').onclick = function() {
        location.reload();
    }
            
});

