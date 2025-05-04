from app.models import CustomUser


class CustomBackend:
    """
    Custom backend for a Custom User
    """
    def authenticate(self, request, email=None, password=None):
        """
        Custom authenticate,take email and return user
        if this email is exist in database
        :param request:
        :param email: valid email
        :return: user or None
        """
        try:
            user = CustomUser.objects.get(email=email, password=password)
        except CustomUser.DoesNotExist:
            return None
        else:
            return user

    def get_user(self, user_id):
        """
        Get user by user id
        :param user_id: int
        :return: CustomUser class instance
        """
        try:
            return CustomUser.objects.get(user_id=user_id)
        except CustomUser.DoesNotExist:
            return None