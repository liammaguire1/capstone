import requests
import random

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

def game(request):
    
    # Submission from menu view
    if request.method == 'POST':

        # Set timer value
        timer = int(request.POST.get('time'))

        # Create dict of players
        players = request.POST.getlist("player_names")

    return render(request, "bacon/game.html", {
        'final': 2
    })
    

def placeholder(request, mode=None):
    final = ''

    # Set initial mode
    if mode == None:
        mode = random.randint(0, 1)

    # User submitted text
    if request.method == "POST":
        
        # Search movie/tv show from actor
        if request.POST['mode'] == 'actor':
            mode = actor_to_work(request)
            works = Score.objects.get(user=request.user).query
            final = []
            for work in works['cast']:
                for w in work:
                    if 'original_title' in w:
                        final.append(w['original_title'])

        # Search actor from movie/tv show
        else:
            mode = work_to_actor(request)
        
    # GET request
    elif request.method == 'GET':

        # Query for current game
        try:
            score = Score.objects.get(user=request.user)
            score.streak = 0
            score.query = None
        except Score.DoesNotExist:
            score = Score(
                user = request.user,
                streak = 0,
                query = None
            )
        score.save()
    
    return render(request, "bacon/play.html", {
        "final": final,
        "mode": mode
    })

def actor_to_work(request):

    # Dynamically build url for API request
    url_one = 'https://api.themoviedb.org/3/search/person?query='
    url_two = '&include_adult=false&language=en-US&page=1'
    actor = request.POST['actor'].split()
    for i, a in enumerate(actor):
        url_one += a
        if i < len(actor) - 1:
            url_one += '%20'
    url_one += url_two

    # Make API request
    response = requests.get(url_one, headers=headers)

    # Handle request status
    if response.status_code == 200:
        if response.json()['results'] == []:
            display = 'Actor not found :('
        else:
            # Query all movies/tv shows the actor has been in
            actor_id = response.json()['results'][0]['id']
            actor_credit_url = f'https://api.themoviedb.org/3/person/{actor_id}/combined_credits'
            credit_response = requests.get(actor_credit_url, headers=headers)

            # Set current game json to all movies/tvs shows feauturing actor
            score = Score.objects.get(user=request.user)
            score.streak += 1
            score.query = credit_response.json()
            score.save()
            return False
    else:
        display = 'Request Failed'
    
    return True

def work_to_actor(request):
    return True

def leaderboard(request):
    return render(request, "bacon/leaderboard.html")