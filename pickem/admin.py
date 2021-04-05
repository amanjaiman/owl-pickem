from django.contrib import admin

from .models import Team, Game, UserProfile, Prediction

class PredictionInLine(admin.TabularInline):
    model = Prediction
    extra = 0

class UserProfileAdmin(admin.ModelAdmin):
    inlines = [PredictionInLine]

def make_all_not_complete(modeladmin, request, queryset):
    for game in queryset:
        game.has_occurred = False
        game.winning_team = None
        game.save()
make_all_not_complete.short_description = 'Reset game complete status'

class GameAdmin(admin.ModelAdmin):
    inlines = [PredictionInLine]
    actions = [make_all_not_complete, ]

admin.site.register(Team)
admin.site.register(Game, GameAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Prediction)