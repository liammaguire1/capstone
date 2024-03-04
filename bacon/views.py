import requests
import json
import re

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import *

API_KEY = 'ad78e1d83ebe751f92aa9fdf0b4ddfc7'

ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhZDc4ZTFkODNlYmU3NTFmOTJhYTlmZGYwYjRkZGZjNyIsInN1YiI6IjY1MzZlYjhiNDA4M2IzMDBjM2M5NGJlNiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.MszHpRZVMi_fhjggP1dv37zaY0_xyIk4eKrROezzk4w'

url = "https://api.themoviedb.org/3/authentication"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "bacon/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "bacon/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "bacon/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, password)
            user.save()
        except IntegrityError:
            return render(request, "bacon/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "bacon/register.html")
    
def index(request):
    return render(request, "bacon/index.html")

def menu(request):
    return render(request, "bacon/menu.html")

def game_load(request):
    
    # Submission from menu view
    if request.method == 'POST':

        # Set timer value
        timer = int(request.POST.get('time'))

        # Create dict of players
        players_raw = request.POST.getlist("player_names")
        players = json.dumps(players_raw)

        return render(request, "bacon/game.html", {
            'timer': timer,
            'players': players
        })


def game_api(request, answer):
    
    # Initial load
    answer = answer.split(',')
    if answer[0] == 'initial':
        return JsonResponse({'instruction': 'Name an actor',
                            'pass': True})
    
    # Game over
    if answer[0] == 'game_over':

        # Player list
        i = 2
        players = ''
        while i < len(answer):
            if i == len(answer) - 1:
                players += answer[i]
            else:
                players += answer[i] + ', '
            i += 1

        # Query for score
        try:
            score = Score.objects.get(user=request.user)
            high_score = max(score.score, int(answer[1]))
            if high_score > score.score:
                score.players = players
                score.score = high_score

        except Score.DoesNotExist:
            score = Score(user=request.user, score=int(answer[1]), players=players)
        
        score.save()
        return JsonResponse({'pass': False})


    # Convert answer elements to list of ids
    previous_ids = []
    if len(answer) > 4:
        i = 3
        while i < len(answer):
            previous_ids.append(int(answer[i]))
            i += 1
        
    # TMDB API request
    works = find(answer[1], 'actor_to_work') if answer[0] == 'actor_to_work' else find(answer[1], 'work_to_actor')

    # Failed TMDB request
    if works == False:
        return JsonResponse({'instruction': 'TMDB request failed',
                            'pass': False})

    # Nothing returned
    if works == None:
        return JsonResponse({'instruction': 'Nothing found. Please try another movie/tv show' if answer[0] == 'work_to_actor' else 'Nothing found. Please try another actor',
                            'pass': False})
    
    # List of works featuring the actor for next guess
    ids = []
    
    # Add work ids to list (actor to work mode)
    if answer[0] == 'actor_to_work':
        for work in works[1]['cast']:
            if 'id' in work:
                ids.append(work['id'])
    # Add movie and tv ids to list (work to actor mode)
    else:
        for i in range(2):
            if 'cast' in works[1][i]:
                for work in works[1][i]['cast']:
                    if 'id' in work:
                        ids.append(work['id'])

    # Validate
    if works[0] not in previous_ids and answer[2] != '':
        return JsonResponse({'instruction': 'Incorrect',
                            'id': answer[2],
                            'ids': ids,
                            'pass': False,
                            'mode': answer[0]})

    # Successful guess
    return JsonResponse({'instruction': f'Name a movie or tv show featuring {answer[1]}' if answer[0] == 'actor_to_work' else f'Name an actor featured in {answer[1]}',
                            'id': works[0], 
                            'ids': ids,
                            'pass': True,
                            'successful_guess': answer[1]})

def find(guess, mode):

    # Dynamically build url for API request
    url_one = 'https://api.themoviedb.org/3/search/person?query=' if mode == 'actor_to_work' else 'https://api.themoviedb.org/3/search/multi?query='
    url_two = '&include_adult=false&language=en-US&page=1'
    guess = guess.split()
    for i, a in enumerate(guess):
        url_one += a
        if i < len(guess) - 1:
            url_one += '%20'
    url_one += url_two

    # Make API request to get actor id
    response = requests.get(url_one, headers=headers)

    # Handle request status
    if response.status_code == 200:
        if response.json()['results'] == []:
            pass
        else:
            # Find id of guess
            id = response.json()['results'][0]['id']
            
            # Actor to work mode
            if mode == 'actor_to_work':
                # Query credits for actor
                actor_credit_url = f'https://api.themoviedb.org/3/person/{id}/combined_credits'
                credit_response = requests.get(actor_credit_url, headers=headers)
                return id, credit_response.json()

            # Work to actor mode
            else:
                # Query credits for movie id
                movie_credit_url = f'https://api.themoviedb.org/3/movie/{id}/credits?language=en-US'
                movie_response = requests.get(movie_credit_url, headers=headers).json()
                # Query credits for tv id
                tv_credit_url = f'https://api.themoviedb.org/3/tv/{id}/credits?language=en-US'
                tv_response = requests.get(tv_credit_url, headers=headers).json()
                return id, [movie_response, tv_response]
    else:
        return False

def leaderboard(request):
    return render(request, "bacon/leaderboard.html", {
        'scores': Score.objects.all()
    })