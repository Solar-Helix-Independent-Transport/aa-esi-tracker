import csv

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from esi_tracker.models import ESIEndpointStatus
class Command(BaseCommand):
    help = 'EXport esit from esi'

    def handle(self, *args, **options):
        self.stdout.write("Exporting All of ESIT updates to CSV")
        count = 0
        with open("esit.csv", 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(["date", "status", "endpoint", "method", "route", "tag"])
            for es in ESIEndpointStatus.objects.all().select_related("endpoint"):
                wr.writerow(
                    [
                        es.date,
                        es.status,
                        es.endpoint.endpoint,
                        es.endpoint.method,
                        es.endpoint.route,
                        es.endpoint.tag
                    ]
                )
                count += 1

        self.stdout.write(f"exported {count} rows successfully to esit.csv!")
