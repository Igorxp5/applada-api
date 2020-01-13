from django.utils import timezone
from django.core.management.base import BaseCommand
from api_v1.models import User, Match, MatchCategory, MatchSubscription

# python manage.py seed --mode=refresh

""" Clear all data and creates addresses """
MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'

class Command(BaseCommand):
    help = "seed database for testing and development."

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'])
        self.stdout.write('done.')


def clear_data():
    """Deletes all the table data"""
    User.objects.all().delete()
    Match.objects.all().delete()
    MatchSubscription.objects.all().delete()

def run_seed(self, mode):
    """ Seed database based on mode

    :param mode: refresh / clear 
    :return:
    """
    # Clear data from tables
    clear_data()
    if mode == MODE_CLEAR:
        return

    igorxp5 = User(username='igorxp5', name='Igor Fernandes', email='rogixp5@gmail.com')
    igorxp5.set_password('1234')
    igorxp5.save()

    igorfc = User(username='igorfc', name='Igor Carneiro', email='igorfc@gmail.com')
    igorfc.set_password('1234')
    igorfc.save()
    
    match_1 = Match(title='Sunday Match', owner=igorxp5, 
                    date=timezone.now(), category=MatchCategory.SOCCER)
    match_1.save()

    MatchSubscription(user=igorfc, match=match_1).save()
    match_1.limit_participants = None
    match_1.save()