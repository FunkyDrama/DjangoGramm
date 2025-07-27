"""
Command for generating fake users and their profiles.

This module contains a Django management command that generates a specified
number of fake user accounts and their associated profiles. The command
utilizes the Faker library for generating random user data and, optionally,
profile avatars. It is designed for testing or populating development
databases with sample data.
"""

from typing import Any
from django.core.management import CommandParser
from django.core.management.base import BaseCommand
import requests
from faker import Faker
from django.contrib.auth import get_user_model
from accounts.models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class Command(BaseCommand):
    """
    Handles the generation of fake users along with their profiles.

    This command utilizes the Faker library to create fake user accounts, and
    optionally, generates profile avatars for those users. It provides the
    flexibility to specify the number of users to generate and whether avatars
    should be skipped. This functionality is useful for testing and populating
    development databases with sample user data.

    :ivar help: Description of the command's purpose displayed in the command-line interface.
    :type help: str
    """

    help = "Generates fake users with profiles"

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Add command-line arguments to the parser for user creation.

        This method modifies a `CommandParser` instance to include arguments
        required for creating users. It provides options to specify the number
        of users to create and determine whether avatar generation should be
        included.

        :param parser: The command-line parser to which the arguments will
            be added.
        :type parser: CommandParser
        :return: None
        """
        parser.add_argument("count", type=int, help="Number of users to create")
        parser.add_argument(
            "--no-avatar", action="store_true", help="Skip avatar generation"
        )

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """
        Executes the command to generate a specified number of fake user accounts and their profiles.
        The command uses Faker to create random user and profile data. Optionally, it adds avatar
        images to the profiles.

        :param args: Positional arguments passed to the command.
        :param kwargs: Keyword arguments. Expected keys are:

            - '--count' (int): The number of users to be created.
            - '--no-avatar' (bool): If False, no avatars will be added to profiles.

        :return: None

        """
        fake = Faker()
        count = kwargs.get("--count")
        with_avatar = kwargs.get("--no-avatar")

        for _ in range(count):
            email = fake.email()
            password = fake.password()
            user = User.objects.create_user(
                username=fake.user_name(),
                email=email,
                password=password,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True,
            )

            profile = Profile.objects.get(user=user)
            profile.bio = fake.text(max_nb_chars=200)

            if with_avatar:
                image_url = (
                    f"https://placehold.co/150x150/{fake.hex_color()[1:]}/ffffff.png"
                )
                profile.avatar.save(
                    f"avatar_{user.username}.png",
                    SimpleUploadedFile(
                        name=f"avatar_{user.username}.png",
                        content=requests.get(image_url).content,
                        content_type="image/png",
                    ),
                )

            profile.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
