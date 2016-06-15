from django.db import models


class Fighter(models.Model):
    # Later add bio data and overall meta stats
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Fight(models.Model):
    fighter = models.ForeignKey(Fighter)
    opponent = models.CharField(max_length=255)
    win = models.BooleanField()
    date = models.DateField()

    finish = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    weight = models.CharField(max_length=255)
    moneyline = models.CharField(max_length=10)

    nationality = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "{} vs {}".format(self.fighter, self.opponent)


# TO DO
# Save processed df to csv file
# create fighters from unique list
# Load all of the fights

