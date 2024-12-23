# accounts/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import RevokedToken  # Ensure your revoked token model is imported

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that checks whether a token has been revoked.
    """
    def decode(self, token):
        """
        Decodes the token and checks if it has been revoked by verifying the jti.
        """
        # Decode the token using the default method
        decoded_token = super().decode(token)
        
        # Extract the jti (JWT ID) from the decoded token
        jti = decoded_token.get('jti')
        
        # Check if the jti is found in the RevokedToken table, meaning it has been revoked
        if jti and RevokedToken.objects.filter(jti=jti).exists():
            raise AuthenticationFailed("Token has been revoked.")

        return decoded_token
