from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CustomJWTAuthentication(JWTAuthentication):
    """JWT 认证，额外检查 token 是否已被吊销（token_revoked_at）。"""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if user is None:
            return None

        revoked_at = getattr(user, "token_revoked_at", None)
        if revoked_at is not None:
            iat = validated_token.get("iat")
            if iat is not None:
                import datetime
                token_iat = datetime.datetime.fromtimestamp(iat, tz=timezone.utc)
                if token_iat < revoked_at:
                    raise InvalidToken("Token has been revoked")

        return user
