import contextvars

_current_user = contextvars.ContextVar("current_user", default=None)


def get_current_user():
  return _current_user.get()


def set_current_user(user):
  _current_user.set(user)
