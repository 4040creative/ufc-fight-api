from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Fighter(models.Model):

    name = models.CharField(max_length=255)
    birthday = models.CharField(max_length=255)
    dt_birthday = models.DateTimeField(null=True, blank=True)
    height = models.CharField(max_length=255)
    weight = models.CharField(max_length=255)
    sh_url = models.CharField(max_length=255, unique=True)

    country = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)
    camp = models.CharField(max_length=255, null=True, blank=True)

    def fights_on_date(self, d):
        """
        For determining how many fights a fighter had prior to a given date.
        :param d: Datetime object.
        :return: A count of fights prior to that date.
        """
        fights = self.winners.all() | self.losers.all()
        priors = fights.filter(event__dt_date__lt=d)
        return priors.count()

    def age_on_date(self, d):
        """
        :param d: A datetime object.
        :return: Number of years old a fighter is on a certain date.
        """
        if self.dt_birthday:
            days = (d - self.dt_birthday).days
            float_days = days / 365
            int_days = int(float_days)
            return float_days, int_days
        else:
            return None, None

    @property
    def fight_count(self):
        return self.winners.count() + self.losers.count()

    @property
    def decision_rate(self):
        """
        :return: The rate (from 0 to 1) that their fights result in a decision.
        """
        decisions = self.winners.filter(
            method__icontains='Decision').count() + self.losers.filter(
            method__icontains='Decision'
        ).count()
        return decisions / self.fight_count

    @property
    def finish_rate(self):
        """
        :return: The rate (from 0 to 1) that their fights result in a finish.
        """
        finishes = self.winners.exclude(
            method__icontains='Decision').count() + self.losers.exclude(
            method__icontains='Decision'
        ).count()
        return finishes / self.fight_count

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    date_string = models.CharField(max_length=50)
    dt_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    sh_url = models.CharField(max_length=255, null=True, blank=True,
                                   unique=True)

    def __str__(self):
        return self.title


class Fight(models.Model):
    winner = models.ForeignKey(Fighter, null=True, blank=True,
                               related_name='winners')
    winner_name = models.CharField(max_length=255)
    winner_url = models.CharField(max_length=255)
    winner_experience = models.IntegerField(null=True, blank=True)
    winner_age = models.FloatField(null=True, blank=True)
    winner_int_age = models.IntegerField(null=True, blank=True)
    winner_streak = models.IntegerField(null=True, blank=True)

    loser = models.ForeignKey(Fighter, null=True, blank=True,
                              related_name='losers')
    loser_name = models.CharField(max_length=255)
    loser_url = models.CharField(max_length=255)
    loser_experience = models.IntegerField(null=True, blank=True)
    loser_age = models.FloatField(null=True, blank=True)
    loser_int_age = models.IntegerField(null=True, blank=True)
    loser_streak = models.IntegerField(null=True, blank=True)

    event = models.ForeignKey(Event, null=True, blank=True)
    method = models.CharField(max_length=255)
    finish_type = models.CharField(max_length=50, null=True, blank=True)

    referee = models.CharField(max_length=255)
    round = models.CharField(max_length=255)
    time = models.CharField(max_length=255)

    def get_finish_type(self):
        finish_types = ['submission', 'ko', 'decision', 'draw', 'nc']
        method = self.method.lower()

        for finish in finish_types:
            if finish in method:
                return finish
        return None

    def set_fighter_ages(self):
        """
        Set the ages of the winning and losing fighters at the time of the
        fight.
        """
        d = self.event.dt_date
        self.winner_age, self.winner_int_age = self.winner.age_on_date(d)
        self.loser_age, self.loser_int_age = self.loser.age_on_date(d)

    def get_streak(self, fighter):
        """
        Determine the streak of a fighter prior to this bout.
        """
        fights = fighter.winners.all() | fighter.losers.all()
        fights = fights.filter(event__dt_date__lt=self.event.dt_date)
        if not fights:
            return 0

        fights = fights.order_by('-event__dt_date')
        winning = fights[0].winner == fighter
        count = 0
        if winning:
            for fight in fights:
                if fight.winner == fighter:
                    count += 1
                else:
                    break
        else:
            for fight in fights:
                if fight.loser == fighter:
                    count -= 1
                else:
                    break
        return count

    def set_fighter_streaks(self):
        """
        Set the streaks for both fighters entering this bout.
        """
        self.winner_streak = self.get_streak(self.winner)
        self.loser_streak = self.get_streak(self.loser)

    def calc_stats(self):
        self.finish_type = self.get_finish_type()
        self.winner_experience = self.winner.fights_on_date(self.event.dt_date)
        self.loser_experience = self.loser.fights_on_date(self.event.dt_date)
        self.set_fighter_ages()
        self.set_fighter_streaks()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.calc_stats()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '{} defeated {}'.format(self.winner_name, self.loser_name)

    class Meta:
        unique_together = ('winner', 'loser', 'event')


class FightQuery(models.Model):
    """
    A user generated search query. This model tracks search parameters and the accompanying results.
    """
    # Search parameters
    win_loss_streak = models.IntegerField(null=True, blank=True)
    min_age = models.PositiveIntegerField(null=True, blank=True)
    max_age = models.PositiveIntegerField(null=True, blank=True)
    min_experience = models.IntegerField(null=True, blank=True)
    max_experience = models.IntegerField(null=True, blank=True)

    search_count = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        values = []
        if self.win_loss_streak is not None:
            values.append('Streak: {}'.format(self.win_loss_streak))
        if self.min_age is not None or self.max_age is not None:
            values.append('Age: {}-{}'.format(self.min_age, self.max_age))
        if self.min_experience is not None or self.max_experience is not None:
            values.append('Exp: {}-{}'.format(self.min_experience, self.max_experience))

        if values:
            value = ', '.join(values)
            return value.replace('None', 'any')
        else:
            return 'All of them'

    def get_query_filters(self):
        query_filters = {
            'streak': self.win_loss_streak,
            'age__gte': self.min_age,
            'age__lte': self.max_age,
            'experience__gte': self.min_experience,
            'experience__lte': self.max_experience
        }
        return {k: v for k, v in query_filters.items() if v is not None}

    def get_wins_losses(self):

        query_filters = self.get_query_filters()
        win_filter = {'winner_{}'.format(k): v for k, v in query_filters.items()}
        loss_filter = {'loser_{}'.format(k): v for k, v in query_filters.items()}

        wins = Fight.objects.filter(**win_filter)
        losses = Fight.objects.filter(**loss_filter)

        return wins, losses
