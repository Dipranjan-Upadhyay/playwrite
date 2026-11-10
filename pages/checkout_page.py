import allure

from pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.cart_items = page.locator('[data-test="inventory-item"]')
        self.checkout_button = page.locator('[data-test="checkout"]')

    def item_names(self) -> list[str]:
        return self.cart_items.locator('[data-test="inventory-item-name"]').all_inner_texts()

    def checkout(self):
        self.checkout_button.click()


class CheckoutPage(BasePage):
    path = "/checkout-step-one.html"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.first_name = page.locator('[data-test="firstName"]')
        self.last_name = page.locator('[data-test="lastName"]')
        self.postal_code = page.locator('[data-test="postalCode"]')
        self.continue_button = page.locator('[data-test="continue"]')
        self.finish_button = page.locator('[data-test="finish"]')
        self.error_message = page.locator('[data-test="error"]')
        self.complete_header = page.locator('[data-test="complete-header"]')
        self.total_label = page.locator('[data-test="total-label"]')

    def fill_details(self, first: str, last: str, postal: str):
        with allure.step(f"Fill checkout details ({first!r}, {last!r}, {postal!r})"):
            self.first_name.fill(first)
            self.last_name.fill(last)
            self.postal_code.fill(postal)
            self.continue_button.click()
        return self

    def finish(self):
        with allure.step("Finish order"):
            self.finish_button.click()
        return self
