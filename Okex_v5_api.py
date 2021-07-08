from requests import Request, Session
from typing import Any
from datetime import datetime
import hmac
import base64
okex_url = 'https://www.okex.com'


class UnifiedAccount:
    def __init__(self, api_key=None, api_secret=None, passphrase=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._passphrase = passphrase
        self._endpoint = okex_url

    def _get(self, path, params=None):
        return self._request('GET', path, params=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._endpoint + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        if 'data' in response.json():
            return response.json()['data']
        else:
            return 'Invalid Response: %s' % response.text

    def _sign_request(self, request: Request) -> None:
        ts = datetime.utcnow().isoformat()[:-3]+'Z'
        prepared = request.prepare()
        signature_payload = ts + prepared.method + prepared.path_url
        if prepared.body:
            signature_payload += prepared.body
        mac = hmac.new(
            bytes(self._api_secret, encoding='utf8'),
            bytes(signature_payload, encoding='utf-8'),
            digestmod='sha256')
        d = mac.digest()
        signature = base64.b64encode(d)
        request.headers['OK-ACCESS-KEY'] = self._api_key
        request.headers['OK-ACCESS-SIGN'] = signature
        request.headers['OK-ACCESS-TIMESTAMP'] = str(ts)
        request.headers['OK-ACCESS-PASSPHRASE'] = self._passphrase

    def _get_params(data):
        """Convert params to ordered string for signature
        :param data:
        :return: ordered parameters like amount=10&price=1.1&type=BUY
        """
        return '&'.join(["{}={}".format(k, data[k])for k in data])

    # Account
    def get_balances(self):
        return self._get('/api/v5/account/balance')[0]['details']

    def get_positions(self, **kwargs):
        endpoint = '/api/v5/account/positions?'
        if kwargs:
            for k in kwargs:
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)

    def get_fills(self, **kwargs):
        endpoint = '/api/v5/trade/fills?'
        if kwargs:
            for k in sorted(kwargs):
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)

    def get_bills_details_last_7days(self, **kwargs):
        endpoint = '/api/v5/account/bills?'
        if kwargs:
            for k in sorted(kwargs):
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)

    def get_bills_details_last_3months(self, **kwargs):
        endpoint = '/api/v5/account/bills-archive?'
        if kwargs:
            for k in sorted(kwargs):
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)

    def get_interest_accrued(self, **kwargs):
        endpoint = '/api/v5/account/interest-accrued?'
        if kwargs:
            for k in sorted(kwargs):
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)

    # Funding
    def get_asset_bills_details(self, **kwargs):
        endpoint = '/api/v5/asset/bills?'
        if kwargs:
            for k in sorted(kwargs):
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)

    # Public Data
    def get_instruments(self, insttype, **kwargs):
        endpoint = '{}{}'.format('/api/v5/public/instruments?instType=', insttype)
        if kwargs:
            for k in kwargs:
                endpoint = '{}{}&{}={}'.format('/api/v5/public/instruments?instType=', insttype, k, kwargs[k])
        return self._get(endpoint)

    def get_deposit(self, **kwargs):
        endpoint = '/api/v5/asset/deposit-history'
        if kwargs:
            for k in sorted(kwargs):
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)

    def get_withdrawal(self, **kwargs):
        endpoint = '/api/v5/asset/withdrawal-history'
        if kwargs:
            for k in sorted(kwargs):
                endpoint += '{}={}&'.format(k, kwargs[k])
        return self._get(endpoint)
