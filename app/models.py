from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class ProfileType(models.TextChoices):
    EMPLOYEE = 'EMP', 'Employee'
    COMPANY = 'COM', 'Company'

class TypeOfEmployment(models.TextChoices):
    OFFICE = "office", "Office"
    REMOTE = "remote", "Remote"
    MIX = "mix", "Mix"

class CustomUserManager(BaseUserManager):
    """
    This is Custom Manager for Custom User,
    used for create new interface for creating Custom User
    """

    def create_user(self, email: str, contact: str, first_name: str, last_name: str,country:str,profile_type: str,
                    password: str, company_name: str = None,
                    **extra_fields) -> 'CustomUser':
        """
        Used for create Custom User using custom fields
        :param email: user email
        :param extra_fields: something extra
        :return: instance of Custom User class
        """
        user = self.model(
            email=self.normalize_email(email),
            contact=contact,
            first_name=first_name,
            last_name=last_name,
            country=country,
            profile_type=profile_type,
            company_name=company_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    """
    Database model for custom users.
    Save all info about user account
    """

    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=32, unique=True)
    country = models.CharField(max_length=32)
    profile_type = models.CharField(
        max_length=16,
        choices=ProfileType.choices,
    )
    company_name = models.CharField(max_length=128, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    description = models.TextField()
    payload = models.FloatField()
    category = models.CharField(max_length=128)
    type_of_employment = models.CharField(
        max_length=16,
        choices=TypeOfEmployment.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner} {self.title}"

    @classmethod
    def create(cls, owner: CustomUser, title: str, description: str, category: str, type_of_employment: str,payload: float):
        try:
            if owner.profile_type != ProfileType.COMPANY:
                raise Exception("Order owner must be Company Profile")

            if type(payload) != float:
                payload = float(payload)

            if type_of_employment not in TypeOfEmployment.values:
                raise Exception(f"Type of Employment must be one of {TypeOfEmployment.values}")

            order = cls.objects.create(
                                    owner=owner, title=title,
                                    description=description,
                                    type_of_employment=type_of_employment,
                                    category=category, payload=payload
                                    )

            order.save()

            return order

        except Exception as e:
            return e

    @classmethod
    def get_all_with_filters(cls, min_price=None, max_price=None, country = None, category = None):
        try:
            filter_args = {}

            if min_price is not None:
                filter_args["payload__gte"] = min_price

            if max_price is not None:
                filter_args["payload__lte"] = max_price

            if category:
                filter_args["category__iexact"] = category

            if country:
                filter_args["owner__country__iexact"] = country

            return cls.objects.filter(**filter_args).order_by("-created_at")
        except Exception as e:
            return e
