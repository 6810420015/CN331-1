from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("debates", "0002_topic_end_date"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="comment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("side__isnull", False)),
                fields=("topic", "author"),
                name="unique_vote_per_user_topic",
            ),
        ),
    ]
