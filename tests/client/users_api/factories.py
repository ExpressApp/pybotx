from random import choice

import factory  # type: ignore


class CsvUserResponseValues(factory.DictFactory):  # type: ignore[misc]
    """Factory for generating CSV user response data.

    This factory creates dictionaries that simulate user data as it would appear
    in a CSV response from the BotX API.

    """

    HUID = factory.Faker("uuid4")
    AD_Login = factory.Faker("user_name")
    Domain = "cts.example.com"
    AD_E_mail = factory.Faker("email")
    Name = factory.Faker("name")
    Sync_source = "ad"
    Active = factory.LazyFunction(lambda: choice(["true", "false"]))  # noqa: S311
    Kind = "cts_user"
    User_DN = factory.Faker("uuid4")
    Company = factory.Faker("company")
    Department = factory.Faker("catch_phrase")
    Position = factory.Faker("job")
    Manager = factory.Faker("name")
    Manager_HUID = ""
    Manager_DN = ""
    Personnel_number = ""
    Description = factory.Faker("sentence")
    IP_phone = factory.Faker("phone_number")
    Other_IP_phone = factory.Faker("phone_number")
    Phone = factory.Faker("phone_number")
    Other_phone = factory.Faker("phone_number")
    Avatar = factory.Faker("file_name", category="image")
    Office = factory.Faker("city")
    Avatar_preview = factory.Faker("file_name", category="image")

    class Meta:
        rename = {
            "AD_Login": "AD Login",
            "AD_E_mail": "AD E-mail",
            "Sync_source": "Sync source",
            "IP_phone": "IP phone",
            "Other_IP_phone": "Other IP phone",
            "Other_phone": "Other phone",
            "Avatar_preview": "Avatar preview",
            "Manager_HUID": "Manager HUID",
            "Manager_DN": "Manager DN",
            "Personnel_number": "Personnel number",
            "User_DN": "User DN",
        }
