class ErrorMessages:
    def __init__(self):
        self.auth_invalid_email_or_code = "Invalid or expired code. Please try again or request a new one."
        self.auth_resend_code_success = "A new code has been sent to your email."
        self.auth_too_many_login_codes = "You’ve requested too many login codes today. Please try again tomorrow."
        self.total_holding_weights_not_100 = "Holdings weight must sum to 100."
        self.duplicate_tickers = "Ticker '{ticker}' appears more than once in the basket."
        self.exception_validation_default_message = "Some fields are invalid. Please review your inputs."
        self.meaningless_user_prompt = "Your prompt couldn’t be understood. Please enter a clear investment instruction."
        self.user_not_found = "User not found."
        self.baskets_generation_daily_limit = "You’ve reached your daily limit for creating new baskets. Please try again tomorrow."
        self.baskets_regeneration_daily_limit = "You’ve reached your daily limit for regenerating baskets. Please try again tomorrow."
        self.jobs_basket_generation_unexpected_error = "An unexpected error occurred while generating your basket. Please try again."
        self.jobs_basket_generation_already_in_progress = "You already have a basket generation in progress. Please wait until it is complete before submitting a new prompt."
        self.job_not_found = "Job not found."

messages = ErrorMessages()