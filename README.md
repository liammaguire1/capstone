# CS50w Capstone - Bacon.io

## Description

Bacon.io is an adaptation of a game I play with my family, the objective being to string together as many actors and movies/tv shows as possible. The first person names an actor, the second person names a movie or tv show featuring that actor, the third person names a different actor in that movie or tv show, etc. The group collectively scores points for each link added to the chain. Play continues until a player can not think of a valid submission and the timer runs out.

## Distinctiveness and Complexity

In terms of the distinctiveness and complexity requirements outlined in the instructions page for this project, I built my web application utilizing a combination of the concepts and techniques taught in this course as well as self-guided exploration into further topics as needed. In order to avoid creating anything similar to the projects in this course, I opted to make a game for my capstone project, a concept we did not previously explore in lecture.

Initially, I set to work building out the front-end of Bacon.io to allow players to log in to the site and configure their game settings. I used JavaScript to allow customization of player numbers, player names, and the timer setting. Once the user makes these selections, this data is passed to views.py on the back-end before loading the main gameplay view.

I used JavaScript on the front-end to handle much of the functionality of the game itself. Storing variables such as the current player, the score, and the timer in the browser allowed me to quickly manipulate the DOM without requiring a full page reload. Events such as decrementing the timer and checking for an endgame state were handled via timed intervals, while requests to my own API to handle player submissions was triggered by submission of text data.

The bulk of my time spent building Bacon.io was devoted to integrating a third-party API from The Movie Database (TMDB) into my web application. I needed access to a large database of actors, movies, and tv shows, so TMDB's free API allowed me to make requests to various routes to query and validate user input. Essentially, after some formatting, the user's submission is passed to my "find" function where I make requests to TMDB. The first request returns the id of the current actor or movie/tv show. The second request returns the next set of credits for the id returned from the first request. Then, back in the main API route, these returned ids are validated to determine if the user's submission is true and a json response is returned.

After the timer reaches 0, the DOM is changed to display a "Game Over" message, prompting the user to play again. Additionally, a query is made to either update or create the user's Score object in a Django model. These objects are displayed in the leaderboard tab of Bacon.io.

## Other Information

The file structure of my project mirrors that of any other project in this course with CSS and Javascript files in a static folder, HTML in a templates folder, and most of the back-end Python in views.py. My application can be run with the command 'python manage.py runserver'.