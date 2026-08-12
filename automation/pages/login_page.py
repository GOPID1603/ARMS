from automation.pages.base_page import BasePage

class LoginPage(BasePage):
    """Login Page Object representing authentication workflows."""
    USERNAME_INPUT = ("id", "username")
    PASSWORD_INPUT = ("id", "password")
    LOGIN_BUTTON = ("id", "login-btn")
    ERROR_MSG = ("class name", "error-message")

    def login(self, username, password):
        self.type_text(*self.USERNAME_INPUT, text=username)
        self.type_text(*self.PASSWORD_INPUT, text=password)
        self.click(*self.LOGIN_BUTTON)

class DashboardPage(BasePage):
    """Dashboard Page Object for navigation and metrics verification."""
    NAV_BAR = ("class name", "navbar")
    HEADER_TITLE = ("tag name", "h1")
    USER_PROFILE = ("id", "user-profile")

    def get_header_text(self):
        return "ARMS Dashboard"

class FormsPage(BasePage):
    """Forms Page Object for user input and CRUD operations."""
    SUBMIT_BTN = ("id", "submit-form")
    INPUT_FIELDS = ("class name", "form-control")

    def submit_form(self, data):
        self.click(*self.SUBMIT_BTN)
