import allure

from pages.base_page import BasePage


class InventoryPage(BasePage):
    path = "/inventory.html"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.page_title = page.locator('[data-test="title"]')
        self.items = page.locator('[data-test="inventory-item"]')
        self.item_names = page.locator('[data-test="inventory-item-name"]')
        self.item_prices = page.locator('[data-test="inventory-item-price"]')
        self.sort_dropdown = page.locator('[data-test="product-sort-container"]')
        self.cart_badge = page.locator('[data-test="shopping-cart-badge"]')
        self.cart_link = page.locator('[data-test="shopping-cart-link"]')
        self.menu_button = page.get_by_role("button", name="Open Menu")
        self.logout_link = page.locator('[data-test="logout-sidebar-link"]')

    def _item(self, name: str):
        return self.items.filter(has_text=name)

    def add_to_cart(self, name: str):
        with allure.step(f"Add '{name}' to cart"):
            self._item(name).get_by_role("button", name="Add to cart").click()
        return self

    def remove_from_cart(self, name: str):
        with allure.step(f"Remove '{name}' from cart"):
            self._item(name).get_by_role("button", name="Remove").click()
        return self

    def sort_by(self, option_value: str):
        with allure.step(f"Sort products by '{option_value}'"):
            self.sort_dropdown.select_option(option_value)
        return self

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def prices(self) -> list[float]:
        return [float(p.replace("$", "")) for p in self.item_prices.all_inner_texts()]

    def cart_count(self) -> int:
        return int(self.cart_badge.inner_text()) if self.cart_badge.count() else 0

    def go_to_cart(self):
        self.cart_link.click()

    def logout(self):
        with allure.step("Log out"):
            self.menu_button.click()
            self.logout_link.click()
