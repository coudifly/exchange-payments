import hmac
import requests
import uuid
from django.conf import settings


ACCOUNT_ID_KEY_NAME = 'bepay_account_id'

def hash_256(string):
    return hmac.new(settings.BEPAY_SECRET_KEY.encode(), msg=string.encode(), digestmod='sha256').hexdigest()


class Gateway:
    def raise_if_error(self, response):
        if 'error' in response:
            raise Exception(response['error']['description'])
        return response

    def create_account(self, account):
        data = {
            'externalIdentifier': str(account.pk),
            'sharedAccount': False,
            'client': {
                'name': account.user.name,
                'socialName': account.user.name,
                'taxIdentifier': {
                    'taxId': account.user.document_1,
                    'country': 'BRA'
                },
                'mobilePhone': {
                    'phoneNumber': account.user.mobile_phone,
                    'country': 'BRA'
                },
                'email': account.user.email
            }
        }

        tx_hash = hash_256(str(account.pk) + account.user.document_1)
        headers = {'Api-Access-Key': settings.BEPAY_API_ACCESS_KEY, 'Transaction-Hash': tx_hash}
        response = requests.post(settings.BEPAY_SERVER_URL + '/accounts', json=data, headers=headers).json()
        self.raise_if_error(response)

        user = account.user
        account_id = response['data']['account']['accountId']
        user.profile[ACCOUNT_ID_KEY_NAME] = account_id
        user.save()

        return account_id

    def get_account_id(self, account):
        user = account.user
        if not ACCOUNT_ID_KEY_NAME in user.profile:
            return self.create_account(account)
        return user.profile[ACCOUNT_ID_KEY_NAME]

    def get_account(self, account):
        account_id = self.get_account_id(account)
        headers = {'Api-Access-Key': settings.BEPAY_API_ACCESS_KEY}
        response = requests.get(settings.BEPAY_SERVER_URL + f'/accounts/{account_id}', headers=headers).json()
        return self.raise_if_error(response)

    def get_balance(self, account):
        account_id = self.get_account_id(account)
        tx_hash = hash_256(account_id)
        headers = {'Api-Access-Key': settings.BEPAY_API_ACCESS_KEY, 'Transaction-Hash': tx_hash}
        response = requests.get(settings.BEPAY_SERVER_URL + f'/accounts/{account_id}/balance', headers=headers).json()
        return self.raise_if_error(response)

    def get_statement(self, account):
        account_id = self.get_account_id(account)
        tx_hash = hash_256(account_id)
        headers = {'Api-Access-Key': settings.BEPAY_API_ACCESS_KEY, 'Transaction-Hash': tx_hash}
        response = requests.get(settings.BEPAY_SERVER_URL + f'/accounts/{account_id}/statement', headers=headers).json()
        return self.raise_if_error(response)

    def transfer_money(self, account, amount):
        account_id = self.get_account_id(account)
        data = {'totalAmount': amount,
            'currency': 'BRL',
            'externalIdentifier': uuid.uuid4().hex,
            'sender': {'account': {'accountId': settings.BEPAY_MASTER_ACCOUNT_ID}},
            'paymentInfo':{'transactionType': 'InternalTransfer'},
            'recipients': [{'account':{'accountId': f'{account_id}'},
                'amount': amount,
                'currency': 'BRL',
                'senderComment': 'Transfer for bank withdraw',
                'recipientComment': 'Receive transfer for bank withdraw'
            }]
        }

        tx_hash = hash_256(settings.BEPAY_MASTER_ACCOUNT_ID + str(amount) + account_id + str(amount))
        headers = {'Api-Access-Key': settings.BEPAY_API_ACCESS_KEY, 'Transaction-Hash': tx_hash}
        response = requests.post(settings.BEPAY_SERVER_URL + '/payments', json=data, headers=headers).json()
        return self.raise_if_error(response)


    def can_deposit(self, account, data):
        pass

    def to_withdraw(self, withdraw):
        amount = str(int(withdraw.net_amount))
        external_identifier = str(withdraw.pk)
        account_type = 1 if withdraw.account_type == 'checking' else 2

        data = {
            'totalAmount': amount,
            'currency': 'BRL',
            'withdrawInfo': {
                'withdrawType': 'BankTransfer',
                'bankTransfer': {
                    'bankDestination': withdraw.bank,
                    'branchDestination': withdraw.agency,
                    'accountDestination': withdraw.account_number,
                    'taxIdentifier': {
                        'taxId': withdraw.account.user.document_1,
                        'country': 'BRA'
                    },
                    'personType': 'PERSON',
                    'name': withdraw.account.user.name,
                    'accountTypeDestination': str(account_type)
                }
            },
            'externalIdentifier': external_identifier
        }

        account_id = self.get_account_id(withdraw.account)
        tx_hash = hash_256(amount + account_id + withdraw.bank + withdraw.agency + withdraw.account_number)
        headers = {'Api-Access-Key': settings.BEPAY_API_ACCESS_KEY, 'Transaction-Hash': tx_hash}
        response = requests.post(settings.BEPAY_SERVER_URL + f'accounts/{account_id}/withdraw', json=data, headers=headers).json()
        valid_response = self.raise_if_error(response)
        return valid_response['data']['transactionId']
