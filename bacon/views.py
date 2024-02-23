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
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "bacon/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
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
        return JsonResponse({'instruction': 'Name an actor.',
                            'returned': ['initial']})

    # Convert answer elements to list of ids
    previous_ids = []
    if len(answer) > 4:
        i = 3
        while i < len(answer):
            previous_ids.append(int(answer[i]))
            i += 1
    
    # Use actor to find work
    if answer[0] == 'actor_to_work':
        
        # TMDB API call (actor -> work)
        works = actor_to_work(answer[1])

        # Nothing returned
        if works[0] == None or works[1] == None:
            return JsonResponse({'instruction': 'No work returned. Please try again',
                                'returned': answer[2]})
        
        # List of works featuring the actor for next guess
        ids = []
        
        # Add work ids to list
        for work in works[1]['cast']:
            if 'id' in work:
                ids.append(work['id'])

        # Validate
        if works[0] not in previous_ids and answer[2] != '':
            return JsonResponse({'instruction': 'Is that true? ACTOR TO WORK', 
                             'ids': ids})

        return JsonResponse({'instruction': f'Name a movie or tv show featuring {answer[1]}',
                             'id': works[0], 
                             'ids': ids})
    
    # Use work to find actor
    elif answer[0] == 'work_to_actor':
        
        # TMDB API call (work -> actor)
        works = work_to_actor(answer[1])

        # Nothing returned
        if works[0] == None and works[1] == None:
            return JsonResponse({'instruction': 'No actors returned. Please try again',
                                'returned': answer[2]})
        
        # List of actors featured in the work
        ids = []
        
        # Add movie and tv ids to list
        for i in range(2):
            if 'cast' in works[1][i]:
                for work in works[1][i]['cast']:
                    if 'id' in work:
                        ids.append(work['id'])

        # Validate
        print('NEW ID')
        if works[0] not in previous_ids and answer[2] != '':
            return JsonResponse({'instruction': 'Is that true? WORK TO ACTOR', 
                             'ids': ids})

        return JsonResponse({'instruction': f'Name an actor featured in {answer[1]}', 
                             'ids': ids})

def actor_to_work(actor):

    # Dynamically build url for API request
    url_one = 'https://api.themoviedb.org/3/search/person?query='
    url_two = '&include_adult=false&language=en-US&page=1'
    actor = actor.split()
    for i, a in enumerate(actor):
        url_one += a
        if i < len(actor) - 1:
            url_one += '%20'
    url_one += url_two

    # Make API request to get actor id
    response = requests.get(url_one, headers=headers)

    # Handle request status
    if response.status_code == 200:
        if response.json()['results'] == []:
            pass
        else:
            # Query all movies/tv shows the actor has been in
            actor_id = response.json()['results'][0]['id']
            actor_credit_url = f'https://api.themoviedb.org/3/person/{actor_id}/combined_credits'
            credit_response = requests.get(actor_credit_url, headers=headers)
            return actor_id, credit_response.json()
    else:
        return

def work_to_actor(work):
    
    # Dynamically build url for API request
    url_one = 'https://api.themoviedb.org/3/search/multi?query='
    url_two = '&include_adult=false&language=en-US&page=1'
    work = work.split()
    for i, a in enumerate(work):
        url_one += a
        if i < len(work) - 1:
            url_one += '%20'
    url_one += url_two

    # Make API request to get work id
    response = requests.get(url_one, headers=headers)

    # Handle request status
    if response.status_code == 200:
        
        if response.json()['results'] == []:
            pass

        else:
            work_id = response.json()['results'][0]['id']
            
            # Query credits for movie id
            movie_credit_url = f'https://api.themoviedb.org/3/movie/{work_id}/credits?language=en-US'
            movie_response = requests.get(movie_credit_url, headers=headers).json()

            # Query credits for tv id
            tv_credit_url = f'https://api.themoviedb.org/3/tv/{work_id}/credits?language=en-US'
            tv_response = requests.get(tv_credit_url, headers=headers).json()

            return work_id, [movie_response, tv_response]
    else:
        return

def leaderboard(request):
    return render(request, "bacon/leaderboard.html")