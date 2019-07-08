from selenium import webdriver

browser = webdriver.Remote(
    command_executor="http://polychrest.sean.zone:5122/wd/hub",
    desired_capabilities={"browserName": "chrome"}
)

browser.get("http://google.com")
print(browser.page_source)

browser.close()