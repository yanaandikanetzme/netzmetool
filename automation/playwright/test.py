from playwright.sync_api import sync_playwright

def run_browser(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()

    # Open a new page
    page = context.new_page()

    # Navigate to a website
    page.goto("https://www.example.com")

    # Find an element and click it
    page.click("text=Login")

    # Fill in an input field
    page.fill("#username", "myusername")
    page.fill("#password", "mypassword")

    # Click a button
    page.click("#submit")

    # Wait for a specific element to appear
    page.wait_for_selector("text=Welcome")

    # Close the browser
    context.close()
    browser.close()

def run_http_request(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context()

    # Membuat permintaan HTTP GET
    response = context.new_request().get("https://api.example.com/data")
    print(response.status_code)
    print(response.text())

    # Membuat permintaan HTTP POST
    payload = {"name": "John Doe", "email": "john@example.com"}
    response = context.new_request().post("https://api.example.com/submit", data=payload)
    print(response.status_code)
    print(response.text())

    context.close()
    browser.close()

def run_android(playwright):
    android_device = playwright.devices["Pixel 5"]
    browser = playwright.android.launch_browser(device=android_device)
    context = browser.new_context()

    # Buka aplikasi Android
    context.android.app.launch("com.example.myapp")

    # Interaksi dengan aplikasi
    app = context.android.app
    app.tap("text=Start")
    app.fill_text("#username_field", "myusername")
    app.fill_text("#password_field", "mypassword")
    app.tap("text=Login")

    # Tunggu hingga halaman berhasil dimuat
    app.wait_for_element("text=Welcome")

    # Tutup aplikasi dan browser
    app.close()
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run_browser(playwright)
    run_http_request(playwright)
    run_android(playwright)