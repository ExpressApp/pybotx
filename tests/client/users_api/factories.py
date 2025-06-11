from factory import DictFactory, Faker  # type: ignore


class CsvUserResponseValues(DictFactory):
    """Factory for generating CSV user response data.

    This factory creates dictionaries that simulate user data as it would appear
    in a CSV response from the BotX API.

    """

    HUID = Faker("uuid4")  # type: ignore
    AD_Login = Faker("user_name")  # type: ignore
    Domain = "cts.example.com"
    AD_E_mail = Faker("email")  # type: ignore
    Name = Faker("name")  # type: ignore
    Sync_source = "ad"
    Active = "true"
    Kind = "cts_user"
    User_DN = Faker("name")  # type: ignore
    Company = Faker("company")  # type: ignore
    Department = Faker("catch_phrase")  # type: ignore
    Position = Faker("job")  # type: ignore
    Manager = Faker("name")  # type: ignore
    Manager_HUID = ""
    Manager_DN = ""
    Personnel_number = ""
    Description = Faker("sentence")  # type: ignore
    IP_phone = Faker("phone_number")  # type: ignore
    Other_IP_phone = Faker("phone_number")  # type: ignore
    Phone = Faker("phone_number")  # type: ignore
    Other_phone = Faker("phone_number")  # type: ignore
    Avatar = Faker("file_name", category="image")  # type: ignore
    Office = Faker("city")  # type: ignore
    Avatar_preview = Faker("file_name", category="image")  # type: ignore

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
