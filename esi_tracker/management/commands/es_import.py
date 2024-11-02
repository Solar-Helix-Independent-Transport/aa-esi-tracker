import csv
from datetime import datetime

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from esi_tracker.models import ESIEndpointStatus, ESIEndpoint
class Command(BaseCommand):
    help = 'Import data from csv'

    def handle(self, *args, **options):
        self.stdout.write("Importing All of ESIT updates to CSV from esit.csv")
        
        count_ep = 0
        count_data = 0
        count_new_data = 0

        with open("esit.csv", 'r') as myfile:
            wr = csv.DictReader(myfile)
            for row in wr:
                _ep , _ep_created = ESIEndpoint.objects.get_or_create(
                    endpoint=row["endpoint"],
                    method=row["method"],
                    route=row["route"],
                    tag=row["tag"]
                )
                count_ep += 1
                _eps , _eps_created = ESIEndpointStatus.objects.get_or_create(
                    endpoint=_ep,
                    date=datetime.fromisoformat(row["date"]),
                    status=row["status"]
                )
                count_data += 1
                if _eps_created:
                    count_new_data += 1


        self.stdout.write(
            (
                f"imported ep:{count_ep:,} data:{count_data:,} new:{count_new_data:,}"
                " rows successfully to esit.csv!"
            )
        )
