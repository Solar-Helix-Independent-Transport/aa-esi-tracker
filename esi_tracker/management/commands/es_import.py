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
        count_new_ep = 0
        count_data = 0
        count_new_data = 0

        with open("esit-e.csv", 'r') as myfile:
            wr = csv.DictReader(myfile)
            for row in wr:
                _ep, _ep_created = ESIEndpoint.objects.get_or_create(
                    pk=row["pk"],
                    endpoint=row["endpoint"],
                    method=row["method"],
                    route=row["route"],
                    tag=row["tag"]
                )
                count_ep += 1
                if _ep_created:
                    count_new_ep += 1

        self.stdout.write(
            (
                f"imported ep:{count_ep:,} new:{count_new_ep} successfully from esit-e.csv!"
            )
        )

        with open("esit-s.csv", 'r') as myfile:
            wr = csv.DictReader(myfile)
            total = 0
            for r in wr:
                total += 1

            myfile.seek(0)
            wr = csv.DictReader(myfile)

            self.stdout.write(f"Total Rows to import {total}")
            updated = 0

            for row in wr:
                _eps, _eps_created = ESIEndpointStatus.objects.get_or_create(
                    endpoint_id=row["epid"],
                    date=datetime.fromisoformat(row["date"]),
                    status=row["status"]
                )
                count_data += 1
                if _eps_created:
                    count_new_data += 1
                if count_data > updated+4999:
                    self.stdout.write(f"Completed: {count_data}({count_new_data})/{total}")
                    updated = count_data


        self.stdout.write(
            (
                f"imported data:{count_data:,} new:{count_new_data:,}"
                " rows successfully to esit-s.csv!"
            )
        )
