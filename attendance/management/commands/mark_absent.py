from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_date

from attendance.services import mark_absent_employees


class Command(BaseCommand):
    help = "Automatically mark employees absent when they have no punch or approved leave."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            help="Attendance date to process in YYYY-MM-DD format. Defaults to yesterday.",
        )

    def handle(self, *args, **options):
        target_date = parse_date(options["date"]) if options.get("date") else None
        if options.get("date") and target_date is None:
            self.stderr.write(self.style.ERROR("Invalid --date. Use YYYY-MM-DD."))
            return

        target_date = target_date or (timezone.localdate() - timedelta(days=1))
        records = mark_absent_employees(target_date)
        self.stdout.write(
            self.style.SUCCESS(
                f"Marked {len(records)} employee(s) absent for {target_date}."
            )
        )
