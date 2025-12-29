def extract_tickers_data(user_id, basket_id=None, basket_obj=None, basket_repo=None, securities_repo=None):
    if not any([basket_id, basket_obj]) or not basket_repo or not securities_repo:
        return
    if basket_id and not basket_obj:
        basket_obj = basket_repo.get(basket_id, user_id)
    return {holding.ticker: securities_repo.get_security_id_for_ticker(holding.ticker) for holding in basket_obj.holdings}
