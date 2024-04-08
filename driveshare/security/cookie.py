from fastapi.responses import RedirectResponse

class SessionHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance: 
            cls._instance = super(SessionHandler, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__() 
        return cls._instance

    def __init__(self):
        self.secret_key = "n688OMzRj1RkMeQuvo9P92bWO6eYEYXU"
        self.sessions = []
    
    def get_cookied_redirect(self, url: str, value: str) -> RedirectResponse:
        response = RedirectResponse(url=url)
        response.set_cookie(key=self.secret_key, value=value)
        self.sessions.append(value)
        return response
    
    def get_cookie(self, request) -> str:
        return request.cookies.get(self.secret_key)

    def remove_session(self, value: str) -> None:
        self.sessions.remove(value)