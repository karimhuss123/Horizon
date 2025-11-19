class ErrorMessages:
    def __init__(self):
        self.total_holding_weights_not_100 = "Holdings weight must sum to 100."
        self.duplicate_tickers = "Ticker '{ticker}' appears more than once in the basket."
        self.auth_invalid_email_or_code = "Invalid or expired code. Please try again or request a new one."
        self.auth_resend_code_success = "A new code has been sent to your email."
        self.exception_validation_default_message = "Some fields are invalid. Please review your inputs."

messages = ErrorMessages()