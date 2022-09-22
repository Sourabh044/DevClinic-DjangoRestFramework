from django.contrib.auth.base_user import BaseUserManager


# class UserManager(BaseUserManager):
#     use_in_migrations = True

#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Email is Required')

#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError(('superuser must be staff'))

#         return self.create_user(email, password, **extra_fields)


class UserManager(BaseUserManager):
    def create_user(self, email, name, mobile, password=None):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            mobile = mobile,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, mobile=None):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            mobile=mobile,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
