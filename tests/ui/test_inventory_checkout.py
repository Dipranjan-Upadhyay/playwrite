import allure
import pytest
from playwright.sync_api import expect

from utils.data_loader import as_params

pytestmark = [pytest.mark.ui, pytest.mark.regression]

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"


@allure.feature("UI - Inventory")
class TestInventory:
    @pytest.mark.parametrize(
        "option, attribute, reverse",
        [
            pytest.param("az", "names", False, id="name_a_to_z"),
            pytest.param("za", "names", True, id="name_z_to_a"),
            pytest.param("lohi", "prices", False, id="price_low_to_high"),
            pytest.param("hilo", "prices", True, id="price_high_to_low"),
        ],
    )
    def test_products_can_be_sorted(self, inventory_page, option, attribute, reverse):
        inventory_page.sort_by(option)
        values = getattr(inventory_page, attribute)()
        assert values == sorted(values, reverse=reverse)

    @pytest.mark.smoke
    def test_add_and_remove_items_updates_cart_badge(self, inventory_page):
        inventory_page.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
        expect(inventory_page.cart_badge).to_have_text("2")
        inventory_page.remove_from_cart(BACKPACK)
        expect(inventory_page.cart_badge).to_have_text("1")
        inventory_page.remove_from_cart(BIKE_LIGHT)
        expect(inventory_page.cart_badge).to_have_count(0)


@allure.feature("UI - Checkout")
class TestCheckout:
    @pytest.mark.smoke
    def test_end_to_end_checkout(self, inventory_page, cart_page, checkout_page):
        inventory_page.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
        inventory_page.go_to_cart()
        expect(cart_page.cart_items).to_have_count(2)
        assert sorted(cart_page.item_names()) == sorted([BACKPACK, BIKE_LIGHT])

        cart_page.checkout()
        checkout_page.fill_details("Jane", "Doe", "12345")
        expect(checkout_page.total_label).to_contain_text("Total: $")
        checkout_page.finish()
        expect(checkout_page.complete_header).to_have_text("Thank you for your order!")

    @pytest.mark.security
    @pytest.mark.parametrize("case", as_params("ui_users.json", "checkout_validation"))
    def test_checkout_requires_all_fields(self, inventory_page, cart_page, checkout_page, case):
        inventory_page.add_to_cart(BACKPACK)
        inventory_page.go_to_cart()
        cart_page.checkout()
        checkout_page.fill_details(case["first"], case["last"], case["postal"])
        expect(checkout_page.error_message).to_contain_text(case["error"])
