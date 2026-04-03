EMAIL_VISIBILITY_CHOICES = [
  (0, "Permitir todos a verem meu email"),
  (1, "Apenas meus colegas de classe podem ver meu email"),
  (2, "Ninguém pode ver meu email"),
]


def user_directory_path(instance, filename):
  # file will be uploaded to MEDIA_ROOT/users/<username>/avatars/<filename>
  return f"users/{instance.user.email}/avatars/{filename}"
