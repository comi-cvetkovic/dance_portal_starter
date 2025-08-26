from django.core.management.base import BaseCommand
from collections import defaultdict
from core.models import Participation, DancerParticipation

class Command(BaseCommand):
    help = "Merge duplicate Participation entries into grouped participations using DancerParticipation"

    def handle(self, *args, **kwargs):
        grouped = defaultdict(list)

        for p in Participation.objects.all():
            key = (
                p.event_id,
                p.style_id,
                p.group_type,
                p.age_group,
                p.difficulty,
                p.choreographer_name.strip().lower() if p.choreographer_name else '',
            )
            grouped[key].append(p)

        merged_count = 0

        for key, parts in grouped.items():
            if len(parts) < 2:
                continue

            primary = parts[0]
            duplicates = parts[1:]

            for dup in duplicates:
                dps = DancerParticipation.objects.filter(participation=dup)
                for dp in dps:
                    DancerParticipation.objects.get_or_create(participation=primary, dancer=dp.dancer)

                dup.delete()
                merged_count += 1

        self.stdout.write(self.style.SUCCESS(f"Merged and removed {merged_count} duplicate Participation objects."))
