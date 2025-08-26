from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import (
    Event, DanceClub, Dancer, StyleCategory,
    Participation, DancerParticipation, JudgeScore
)
from datetime import date
import random

class Command(BaseCommand):
    help = "Populate a test event with 100-200 random participations and judges with scores."

    def add_arguments(self, parser):
        parser.add_argument('--entries', type=int, default=150, help="Number of participations to create")

    def handle(self, *args, **options):
        num_entries = options['entries']

        # --- Create or get test club ---
        user, _ = User.objects.get_or_create(
            username="testclub@example.com",
            defaults={"email": "testclub@example.com"}
        )
        club, _ = DanceClub.objects.get_or_create(user=user, defaults={
            "club_name": "Test Club",
            "country": "SE",
            "city": "Stockholm",
            "phone_number": "123456",
            "representative_name": "Test Rep",
            "confirmed": True,
        })

        # --- Create or get test event ---
        event, _ = Event.objects.get_or_create(
            name="Test Event",
            city="Stockholm",
            location="Sports Hall",
            date=date.today(),
        )

        # --- Ensure style categories ---
        styles = ["Hip Hop", "Jazz", "Ballet", "Show Dance", "Contemporary", "Disco"]
        style_objs = []
        for s in styles:
            sc, _ = StyleCategory.objects.get_or_create(event=event, name=s)
            style_objs.append(sc)

        # --- Create dancers for the club ---
        dancers = []
        for i in range(60):
            dancer, _ = Dancer.objects.get_or_create(
                first_name=f"Dancer{i}",
                last_name="Test",
                date_of_birth=date(2005, 1, (i % 28) + 1),
                club=club
            )
            dancers.append(dancer)

        # --- Group limits ---
        group_limits = {
            "Solo": (1, 1),
            "Duo": (2, 2),
            "Trio": (3, 3),
            "Group": (4, 9),
            "Formation": (10, 20),
        }

        # --- Weighted category pool ---
        age_groups = [c for c, _ in Participation.AGE_GROUP_CHOICES]
        difficulties = [c for c, _ in Participation.DIFFICULTY_CHOICES]

        common_category_pool = []
        for style in style_objs:
            for group_type in ["Solo", "Duo", "Trio", "Group"]:
                for age in ["Teen", "Youth", "Adult"]:
                    for diff in difficulties:
                        common_category_pool.extend([(style, group_type, age, diff)] * 5)

        rare_category_pool = []
        for style in style_objs:
            for group_type in group_limits.keys():
                for age in age_groups:
                    for diff in difficulties:
                        rare_category_pool.append((style, group_type, age, diff))

        # --- Create participations ---
        created = 0
        participations = []
        for n in range(num_entries):
            if random.random() < 0.75:
                style, group_type, age_group, diff = random.choice(common_category_pool)
            else:
                style, group_type, age_group, diff = random.choice(rare_category_pool)

            min_d, max_d = group_limits[group_type]
            num_dancers = random.randint(min_d, min(max_d, len(dancers)))

            part = Participation.objects.create(
                event=event,
                style=style,
                group_type=group_type,
                age_group=age_group,
                difficulty=diff,
                choreographer_name=f"Choreo {n}",
                choreography_name=f"Routine {n}",
                group_name=(f"Group{n}" if num_dancers >= 4 else ""),
                display_order=n,
                group_display_order=0,
            )

            chosen = random.sample(dancers, num_dancers)
            for d in chosen:
                DancerParticipation.objects.create(participation=part, dancer=d)

            participations.append(part)
            created += 1

        # --- Create judges ---
        judges = []
        for i in range(1, 6):  # 5 judges
            uname = f"judge{i}"
            judge, _ = User.objects.get_or_create(
                username=uname,
                defaults={"email": f"{uname}@example.com"}
            )
            judges.append(judge)

        # --- Give scores ---
        for part in participations:
            for judge in judges:
                technique = round(random.uniform(1, 10), 2)
                composition = round(random.uniform(1, 10), 2)
                image = round(random.uniform(1, 10), 2)
                show_value = None
                if part.style.name == "Show Dance":
                    show_value = round(random.uniform(1, 10), 2)

                JudgeScore.objects.update_or_create(
                    participation=part,
                    judge=judge,
                    defaults={
                        "technique": technique,
                        "composition": composition,
                        "image": image,
                        "show_value": show_value,
                    }
                )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Created {created} participations in {event.name}, with {len(judges)} judges and scores."
        ))
