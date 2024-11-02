import csv

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from esi_tracker.models import ESIEndpoint, ESIEndpointStatus
class Command(BaseCommand):
    help = 'Export esit from esi'

    def handle(self, *args, **options):
        self.stdout.write("Exporting All of ESIT updates to CSV")
        count_ep = 0
        with open("esit-e.csv", 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(["pk", "endpoint", "method", "route", "tag"])
            for es in ESIEndpoint.objects.all():
                wr.writerow(
                    [
                        es.pk,
                        es.endpoint,
                        es.method,
                        es.route,
                        es.tag
                    ]
                )
                count_ep += 1

        count_s = 0
        with open("esit-s.csv", 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(["epid", "date", "status"])
            for es in ESIEndpointStatus.objects.all():
                wr.writerow(
                    [
                        es.endpoint_id,
                        es.date,
                        es.status
                    ]
                )
                count_s += 1

        self.stdout.write(f"Exported ep:{count_ep} s:{count_s} Rows successfully to csv!")
