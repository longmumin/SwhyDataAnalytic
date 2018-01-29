import requests

class TYApi:


    def __init__(self):
        self.server_url = 'http://101.132.25.200:16016/'
        self.body = {
            'method': '',
            'params': {}
        }
        # log in first
        self.token = self.login('trader', '123')



    def call(self, service, method, params, token=None):
        """Call an API
        Usage: Provide the API name and arguments and the function will call
            the remote api through HTTP POST.

        Args:
            service (string): the service to call
            method (string): The API to be called
            params (dict): The API parameters as a dictionary
            token: login token (call login first to get a token)

        Returns:
            The result of the API call

        Raise:
            RuntimeError
        """
        url = self.server_url + service + '/api/rpc'
        self.body['method'] = method
        self.body['params'] = params
        headers = {}
        if token is not None:
            headers = {
                'Authorization': 'Bearer ' + token
            }
        try:
            res = requests.post(url, json=self.body, headers=headers)
            json = res.json()
            if 'error' in json:
                raise RuntimeError('error calling {service} method {method}: {msg}'.format(service=service, method=method,
                                                                                       msg=json['error']))
            return json['result']
        except:
            print('encountered error while contacting the service. network error?')
            raise



    def login(self, username, password):
        url = self.server_url + 'auth-service/users/login'
        body = {
            'userName': username,
            'password': password
        }
        try:
            res = requests.post(url, json=body)
            json = res.json()
            if 'error' in json:
                raise RuntimeError('error logging in: ' + json['error']['message'])
            return json['result']['token']
        except:
            print('encountered error while contacting the service. network error?')
            raise


    def TYMktQuoteGet(self, timestamp, instrument = '', timezone = 'Asia/Shanghai', instance = 'intraday', field = 'last'):

        #settle为价格
        settle = self.call('market-data-service', 'mktQuoteGet',
                  {'instrument_id': instrument,
                   'instance': instance,
                   'field': field,
                   'timestamp': timestamp,
                   'timezone': timezone},
                  self.token)
        return settle


    def TYPricing(self, forward, strike, vol, tau, r, type = 'call', request = 'price', method = 'qlBlack76Calc'):
        # method为估值方法
        price = self.call('quant-service', method,
                 {'request': request,
                  'forward': forward,
                  'strike': strike,
                  'vol': vol,
                  'tau': tau,
                  'r': r,
                  'type': type},
                 self.token)

        return price


    def TYMdload(self, timestamp, timezone = 'Asia/Shanghai', instance = 'close', model_name = 'VOL_BLACK_ATM_CF.CZC'):

        vs = self.call('model-service', 'mdlLoad',
              {'name': model_name,
               'instance': instance,
               'timestamp': timestamp,
               'timezone': timezone},
              self.token)

        return vs


    def TYVolSurfaceImpliedVolGet(self, forward, strike, expiry, vol):

        iv = self.call('quant-service', 'qlVolSurfaceImpliedVolGet',
              {'volSurface': vol,
               'forward': forward,
               'strike': strike,
               'expiry': expiry},
              self.token)

        return iv
