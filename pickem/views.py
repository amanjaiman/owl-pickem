from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Team, Game, UserProfile, Prediction

import csv
import json
import os
from datetime import datetime

current_week = 1
week_start = False

def error_404_view(request, exception):
    context = {

    }
    return render(request,'pickem/404.html', context)

def index(request):
    current_week_games = Game.objects.filter(week=current_week).order_by('game_number')

    games_dict = {}
    game_ids = []

    curr_date = ""
    for game in current_week_games:
        game_ids.append(game.game_id)
        game_date = game.date_time.strftime("%A %B %d")
        if game_date != curr_date:
            curr_date = game_date
            games_dict[curr_date] = []
        games_dict[curr_date].append(game)
    games_dict = sorted(games_dict.items())
    
    request.session['games'] = json.dumps(game_ids)
    request.session['week'] = current_week
    request.session['current_page'] = 'home'

    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        user_predictions = user_profile.prediction_set.filter(game__week=current_week).order_by('game__game_number')

        user_preds_dict = {}
        curr_date = ""
        for prediction in user_predictions:
            game_date = prediction.game.date_time.strftime("%A %B %d")
            if game_date != curr_date:
                curr_date = game_date
                user_preds_dict[curr_date] = []
            user_preds_dict[curr_date].append(prediction)
        user_preds_dict = sorted(user_preds_dict.items())
    else:
        user_profile = None
        user_preds_dict = None

    if 'User-Agent' in request.headers:
        if "iPhone" in request.headers['User-Agent'] or "Android" in request.headers['User-Agent']:
            agent = "mobile"
        else:
            agent = "web"
    else:
        agent = None

    login_message = request.session.get('login_message')
    if login_message:
        request.session['login_message'] = False

    prediction_message = request.session.get('prediction_message')
    if prediction_message:
        request.session['prediction_message'] = False

    context = {
        'current_week' : current_week,
        'current_week_games': games_dict,
        'user_profile': user_profile,
        'user_predictions': user_preds_dict,
        'week_start': week_start,
        'login_message': login_message,
        'prediction_message': prediction_message,
        'agent': agent
    }
    return render(request, 'pickem/index.html', context)

def leaderboard(request):
    request.session['current_page'] = 'leaderboard'
    
    users = UserProfile.objects.all().order_by('-points')

    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
    else:
        user_profile = None
    
    context = {
        'users': users,
        'user_profile': user_profile
    }

    return render(request, 'pickem/leaderboard.html', context)

def userhistory(request, username):
    request.session['current_page'] = 'history'

    request.session['week'] = current_week

    user = UserProfile.objects.get(user__username=username)
    user_week = user.latest_pred_week

    pred_list = []

    for i in range(1, user_week+1):
        week = user.prediction_set.filter(game__week=i).order_by('game__game_number')
        pred_list.append(week)

    if request.user.is_authenticated:
        auth_user = request.user
        user_profile = UserProfile.objects.get(user=auth_user)
    else:
        user_profile = None

    context = {
        'profile': user,
        'user_predictions': pred_list,
        'user_profile': user_profile
    }

    return render(request, 'pickem/userhistory.html', context)

def pastweeks(request):
    request.session['current_page'] = 'pastweeks'
    request.session['week'] = current_week

    if current_week == 1:
        week_list = None
    else:
        week_list = []
        for i in range(1, current_week):
            week_list.append(Game.objects.filter(week=i).order_by('game_number'))
    
    if request.user.is_authenticated:
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
    else:
        user_profile = None

    context = {
        'week_list': week_list,
        'last_week': current_week-1,
        'user_profile': user_profile
    }

    return render(request, 'pickem/pastweeks.html', context)


def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pickem:index', args=()))
    else:
        request.session['current_page'] = 'signup'
        return render(request, 'pickem/signup.html', {})

def signupaction(request):
    try:
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        #confirm_password = request.POST['confirm_password']
    except KeyError:
        return render(request, 'pickem/signup.html', {'error_message': "Not all required fields were provided."})
    else:
        if User.objects.filter(username=username).exists():
            return render(request, 'pickem/signup.html', {'error_message': "That username already exists!"})
        if User.objects.filter(email=email).exists():
            return render(request, 'pickem/signup.html', {'error_message': "That email already exists!"})
        if not username.isalnum():
            return render(request, 'pickem/signup.html', {'error_message': "Username cannot contain special characters!"})
        else:

            user = User.objects.create_user(username=username, password=password, email=email)
            new_user = UserProfile(user=user)
            new_user.save()
            return loginaction(request)

def loginview(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('pickem:index', args=()))
    else:
        request.session['current_page'] = 'login'
        return render(request, 'pickem/login.html', {})

def loginaction(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        return render(request, 'pickem/login.html', {'error_message': "Not all required fields were provided."})
    else:
        if not username.isalnum():
            if '@' in username:
                try:
                    validate_email(username)
                except ValidationError:
                    return render(request, 'pickem/signup.html', {'error_message': "Username cannot contain special characters!"})
                else:
                    u = User.objects.get(email=username)
                    user = authenticate(request, username=u.username, password=password)
                    if user is not None:
                        login(request, user)
                        request.session['login_message'] = True
                        return HttpResponseRedirect(reverse('pickem:index', args=()))
                    else:
                        return render(request, 'pickem/login.html', {'error_message': "That user does not exist!"})
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['login_message'] = True
                return HttpResponseRedirect(reverse('pickem:index', args=()))
            else:
                return render(request, 'pickem/login.html', {'error_message': "That user does not exist!"})

def logoutaction(request):
    logout(request)
    return HttpResponseRedirect(reverse('pickem:index', args=()))


def makepredictions(request):
    game_ids = json.loads(request.session.get('games'))

    predicted_teams = request.POST.dict()
    user_profile = UserProfile.objects.get(user=request.user)

    if len(predicted_teams) > 1:
        request.session['prediction_message'] = True
        user_profile.latest_pred_week = current_week
        user_profile.save()

    for game_id in game_ids:
        if game_id in predicted_teams:
            team_name = request.POST[game_id].split("-")[1]
            predicted_team = Team.objects.get(team_name=team_name)
        else:
            predicted_team = None

        game = Game.objects.get(game_id=game_id)
        
        if Prediction.objects.filter(user_profile=user_profile, game=game).exists():
            p = Prediction.objects.get(user_profile=user_profile, game=game)
            p.predicted_team = predicted_team
        else:
            p = Prediction(user_profile=user_profile, game=game, predicted_team=predicted_team)
        p.save()

    return HttpResponseRedirect(reverse('pickem:index', args=()))

def adminaction(request):
    if request.user.is_superuser:
        game_ids = json.loads(request.session.get('games'))

        for game_id in game_ids:
            game = Game.objects.get(game_id=game_id)
            game.has_occurred = True
            team_name = request.POST[game_id].split("-")[1]
            game.winning_team = Team.objects.get(team_name=team_name)

            winning_team = game.teams.get(team_name=game.winning_team.team_name)
            losing_team = game.teams.get(~Q(team_name=game.winning_team.team_name))
            winning_team.team_wins += 1
            losing_team.team_losses += 1

            winning_team.save()
            losing_team.save()
            game.save()

            give_points(game)
        
    return HttpResponseRedirect(reverse('pickem:index', args=()))

def give_points(game):
    for user in UserProfile.objects.all():
        if user.prediction_set.filter(game=game).exists():
            game_pred = user.prediction_set.get(game=game)
            if game_pred.predicted_team == game.winning_team:
                game_pred.correct = True
                user.points += 1
            game_pred.save()
        user.save()


def import_schedule(request):
    if request.user.is_superuser:
        if Game.objects.all().count() != 0:
            return HttpResponseRedirect(reverse('pickem:index', args=()))

        teams = {
            "HOU": "Houston Outlaws",
            "DAL": "Dallas Fuel",
            "GLA": "Los Angeles Gladiators",
            "SFS": "San Francisco Shock",
            "GZC": "Guangzhou Charge",
            "SHD": "Shanghai Dragons",
            "VAL": "Los Angeles Valiant",
            "CDH": "Chengdu Hunters",
            "PHI": "Philadelphia Fusion",
            "SEO": "Seoul Dynasty",
            "TOR": "Toronto Defiant",
            "VAN": "Vancouver Titans",
            "ATL": "Atlanta Reign",
            "FLA": "Florida Mayhem",
            "PAR": "Paris Eternal",
            "LDN": "London Spitfire",
            "NYE": "New York Excelsior",
            "HZS": "Hangzhou Spark",
            "BOS": "Boston Uprising",
            "WAS": "Washington Justice"
        }

        with open(os.path.join(settings.BASE_DIR, "pickem", 'schedule.csv')) as f:
            reader = csv.reader(f)
            curr_game = 1
            curr_week = 1
            for row in reader:
                week = row[0]
                time = datetime.strptime(row[1], "%A %B %d %H:%M")
                time = time.replace(year=2021)
                team1 = row[2]
                team2 = row[3]

                if week != curr_week:
                    curr_week = week
                    curr_game = 1
                
                g = Game(week=curr_week, game_number=curr_game, date_time=time)
                g.save()

                g.teams.add(Team.objects.get(team_name=teams[team1]))
                g.teams.add(Team.objects.get(team_name=teams[team2]))

                g.save()

                curr_game += 1

    return HttpResponseRedirect(reverse('pickem:index', args=()))

def add_teams(request):
    if request.user.is_superuser:
        if Team.objects.all().count() != 0:
            return HttpResponseRedirect(reverse('pickem:index', args=()))
        
        teams = {
            "outlaws": "Houston Outlaws",
            "fuel": "Dallas Fuel",
            "gladiators": "Los Angeles Gladiators",
            "shock": "San Francisco Shock",
            "charge": "Guangzhou Charge",
            "dragons": "Shanghai Dragons",
            "valiant": "Los Angeles Valiant",
            "hunters": "Chengdu Hunters",
            "fusion": "Philadelphia Fusion",
            "dynasty": "Seoul Dynasty",
            "defiant": "Toronto Defiant",
            "titans": "Vancouver Titans",
            "reign": "Atlanta Reign",
            "mayhem": "Florida Mayhem",
            "eternal": "Paris Eternal",
            "spitfire": "London Spitfire",
            "excelsior": "New York Excelsior",
            "spark": "Hangzhou Spark",
            "uprising": "Boston Uprising",
            "justice": "Washington Justice"
        }

        url_path = 'https://owlpickem.s3.us-east-2.amazonaws.com/'

        for team in teams.keys():
            team_name = teams[team]

            new_team = Team(team_name=team_name, team_logo=url_path+team+".png")

            new_team.save()

    return HttpResponseRedirect(reverse('pickem:index', args=()))