"""
SCB Morning Briefing Demo — Screen Capture for Figma
Run this script directly (double-click capture_screens.bat or run from terminal).
Captures all 17 demo screens as high-resolution PNGs.
"""
import os, sys, time

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figma_screens")
os.makedirs(OUT, exist_ok=True)

print("\n=== SCB Demo Screen Capture ===\n")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
except ImportError:
    print("Installing selenium...")
    os.system(f'"{sys.executable}" -m pip install selenium webdriver-manager --quiet')
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
except ImportError:
    pass

URL = "http://localhost:8888/SCB_Morning_Briefing_Demo.html"

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-gpu")
opts.add_argument("--window-size=1400,900")
opts.add_argument("--force-device-scale-factor=2")
opts.add_argument("--high-dpi-support=2")

print("Launching Chrome...")
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
except Exception:
    driver = webdriver.Chrome(options=opts)

driver.get(URL)
time.sleep(2)

def js(script):
    return driver.execute_script(script)

def shot(name):
    time.sleep(1)
    phone = driver.find_element(By.CSS_SELECTOR, ".phone")
    fp = os.path.join(OUT, f"{name}.png")
    phone.screenshot(fp)
    print(f"  > {name}.png")

print(f"\nCapturing 17 screens at 2x resolution...\n")

shot("01_Lock_Screen")

driver.find_element(By.CSS_SELECTOR, ".notification").click()
time.sleep(0.8)
shot("02_Home")

js("document.querySelector('#homeBody').scrollTop = document.querySelector('#homeBody').scrollHeight")
time.sleep(0.5)
shot("03_Home_Scrolled")
js("document.querySelector('#homeBody').scrollTop = 0")

js("navigate('briefing')")
time.sleep(1.5)
shot("04_Briefing_Top")

js("document.querySelector('#briefingBody').scrollTop = document.querySelector('#briefingBody').scrollHeight")
time.sleep(0.5)
shot("05_Briefing_Scrolled")
js("document.querySelector('#briefingBody').scrollTop = 0")

js("showWellness()")
time.sleep(1)
shot("06_Wellness")
js("hideWellness()")
time.sleep(0.5)

js("navigate('portfolio')")
time.sleep(1)
shot("07_Portfolio")

js("navigate('profile')")
time.sleep(1)
shot("08_Profile")

js("navigate('chat')")
time.sleep(2)
shot("09_Chat_Initial")

js("startChatFlow('bill')")
time.sleep(3)
shot("10_Chat_Bill_Options")

js("chatAction('payFull')")
time.sleep(2.5)
shot("11_Chat_Pay_Confirm")

js("chatAction('confirmPay')")
time.sleep(3.5)
shot("12_Chat_Pay_Success")

js("document.getElementById('chatMessages').innerHTML=''; chatInited=false;")
js("navigate('chat')")
time.sleep(2)
js("startChatFlow('insights')")
time.sleep(3)
shot("13_Chat_Insights")

js("document.getElementById('chatMessages').innerHTML='';")
js("startChatFlow('s2s_card')")
time.sleep(3.5)
shot("14_Chat_Card_Upgrade")

js("chatAction('applyCard')")
time.sleep(3.5)
shot("15_Chat_Card_Approved")

js("document.getElementById('chatMessages').innerHTML='';")
js("startChatFlow('pointx')")
time.sleep(3)
shot("16_Chat_PointX")

js("document.getElementById('chatMessages').innerHTML='';")
js("startChatFlow('portfolio')")
time.sleep(3)
shot("17_Chat_Portfolio")

driver.quit()

files = [f for f in os.listdir(OUT) if f.endswith('.png')]
print(f"\n{'='*40}")
print(f"Done! {len(files)} screens saved to:")
print(f"  {OUT}")
print(f"{'='*40}")
print("\nNext steps:")
print("  1. Open Figma -> New file")
print("  2. Drag all PNGs from figma_screens/ into the canvas")
print("  3. Select each -> Ctrl+Alt+G to frame it")
print("  4. Switch to Prototype tab and wire the flows\n")
input("Press Enter to close...")
