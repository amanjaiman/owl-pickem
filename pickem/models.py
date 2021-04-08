from django.contrib.auth.models import User
from django.db import models

class Team(models.Model):
    team_name = models.CharField(max_length=50)
    team_logo = models.CharField(max_length=100)
    team_wins = models.IntegerField(default=0)
    team_losses = models.IntegerField(default=0)

    def __str__(self):
        return self.team_name

    def print_win_loss(self):
        return self.team_wins + "-" + self.team_losses

class Game(models.Model):
    week = models.IntegerField(default=0)
    game_number = models.IntegerField(default=0)
    date_time = models.DateField()
    teams = models.ManyToManyField(Team, related_name='teams')

    has_occurred = models.BooleanField(default=False)
    winning_team = models.ForeignKey(Team, default=None, on_delete=models.CASCADE, blank=True, null=True, related_name='winning_team')

    game_id = models.CharField(max_length=50, default='w0g0')

    def save(self, *args, **kwargs):
        self.game_id = "w"+str(self.week)+"g"+str(self.game_number)
        super(Game, self).save(*args, **kwargs)

    def __str__(self):
        if self.teams.exists():
            return ' vs. '.join([a.team_name for a in self.teams.all()])
        else:
            return "Week "+str(self.week)+", "+" Game "+str(self.game_number)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    latest_pred_week = models.IntegerField(default=0)
    twitter = models.CharField(max_length=50, blank=True, null=True)
    favorite_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Prediction(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    predicted_team = models.ForeignKey(Team, blank=True, null=True, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.user_profile.user.username + " - " + self.game.game_id
    