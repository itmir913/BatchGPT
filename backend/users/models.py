from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, verbose_name="Email Address")  # 로그인 ID로 사용
    username = models.CharField(max_length=255, verbose_name="Name")
    balance = models.IntegerField(default=0, verbose_name="Account Balance")  # 사용자 잔액
    is_active = models.BooleanField(default=True, verbose_name="Is Active")  # 계정 활성 상태
    is_staff = models.BooleanField(default=False, verbose_name="Is Staff")  # 관리자 여부
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def set_balance(self, amount):
        self.balance = amount
        self.save()

    def add_balance(self, amount):
        self.balance += amount
        self.save()

    def deduct_balance(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
        else:
            raise ValueError("Insufficient balance")
