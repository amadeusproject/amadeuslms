from django.core.mail.backends import EmailBackend
from app.models import EmailBackend as SmtpModal

class AmadeusEmailBackend(EmailBackend):
	"""docstring for AmadeusEmailBackend"""
	def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None,
                 **kwargs):
        super(AmadeusEmailBackend, self).__init__(fail_silently=fail_silently)
        try:
	        config = SmtpModal.objects.latest('id')
	        self.host = config.host or settings.EMAIL_HOST
	        self.port = config.port or settings.EMAIL_PORT
	        self.username = config.username or settings.EMAIL_HOST_USER if username is None else username
	        self.password = config.password or settings.EMAIL_HOST_PASSWORD if password is None else password
	        
	        if config.safe_conection == 2:
	        	self.use_tls = True
	        	self.use_ssl = False
	        elif config.safe_conection == 3:
	        	self.use_tls = False
	        	self.use_ssl = True
	        else:
	        	self.use_tls = False
	        	self.use_ssl = False

	        self.timeout = settings.EMAIL_TIMEOUT if timeout is None else timeout
	        self.ssl_keyfile = settings.EMAIL_SSL_KEYFILE if ssl_keyfile is None else ssl_keyfile
	        self.ssl_certfile = settings.EMAIL_SSL_CERTFILE if ssl_certfile is None else ssl_certfile
	        if self.use_ssl and self.use_tls:
	            raise ValueError(
	                "EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set "
	                "one of those settings to True.")
	        self.connection = None
	        self._lock = threading.RLock()
	    except:
	    	pass