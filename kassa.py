from freekassa import FreeKassaApi
import random


class Kassa:
    def __init__(self):
        self.client = FreeKassaApi(
            first_secret=')*_wE9Pu=aalhWA',
            second_secret='@h!WTdW$mgv0,r}',
            merchant_id='40703',
            wallet_id='F112521799')

    def generate_link(self, payment_id: int, price: int, email ='', description='') -> str:
        payment_link = self.client.generate_payment_link(payment_id, price, email, description)
        return payment_link

    def get_payment_status(self, payment_id):
        payment_status = self.client.get_online_payment_status(payment_id)
        return payment_status

    def get_order_info(self, order_id: int, int_id: int):
        order = self.client.get_order(order_id, int_id)
        return order

    def money_transfer(self, purse, amount):
        transfer = self.client.transfer_money(purse, amount)
        return transfer

    def get_list_services(self):
        services = self.client.get_online_services()
        return services

    def create_invoice(self, email, amount, description):
        invoice = self.client.invoice(email, amount, description)
        return invoice

    def withdraw_money(self, amount, currency):
        withdraw = self.client.withdraw(amount, currency)
        return withdraw

    def withdraw_money_wallet(self, purse, amount, currency, description, disable_exchange):
        wallet_withdraw = self.client.wallet_withdraw(purse, amount, currency, description, disable_exchange)
        return wallet_withdraw

    def operation_status(self, payment_id):
        operation_status = self.client.get_operation_status(payment_id)
        return operation_status

    def get_balance(self):
        wallet_balance = self.client.get_wallet_balance()
        return wallet_balance




if __name__ == '__main__':
    k = Kassa()
    print(k.generate_link(9,0))