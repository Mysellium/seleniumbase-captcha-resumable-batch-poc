import json
import os
import time
from seleniumbase import SB

STATE_FILE = "download_state.json"
ITEMS_TO_DOWNLOAD = [f"graphic_asset_{i}.png" for i in range(1, 11)]


def load_completed_items():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_completed_item(item_name, completed_set):
    completed_set.add(item_name)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(completed_set), f, indent=2)


def is_captcha_present(sb):
    captcha_selectors = [
        "iframe[src*='recaptcha']",
        "iframe[src*='turnstile']",
        "#captcha-container",
        ".cf-challenge",
    ]
    for selector in captcha_selectors:
        if sb.is_element_visible(selector):
            return True
    return False


def handle_captcha_in_new_tab(sb, verification_url):
    print("\n[WARNING] CAPTCHA detected! Opening verification in a new tab...")
    original_window = sb.driver.current_window_handle

    sb.driver.switch_to.new_window("tab")
    sb.open(verification_url)

    for sec in range(5, 0, -1):
        print(f"[WAITING] Verification tab active... {sec}s")
        time.sleep(1)

    print("[SUCCESS] Verification completed. Closing verification tab...")
    if len(sb.driver.window_handles) > 1:
        sb.driver.close()

    sb.driver.switch_to.window(original_window)
    sb.refresh()


def run_batch_downloader():
    completed = load_completed_items()
    print(f"System initialized. Previously completed items: {len(completed)}")

    try:
        with SB(uc=False) as sb:
            sb.open("https://example.com")

            for index, item in enumerate(ITEMS_TO_DOWNLOAD):
                if item in completed:
                    print(f"[SKIPPED] {item} already downloaded.")
                    continue

                print(f"[DOWNLOADING] ({index + 1}/{len(ITEMS_TO_DOWNLOAD)}) {item}...")

                simulated_captcha = index == 3
                if is_captcha_present(sb) or simulated_captcha:
                    handle_captcha_in_new_tab(sb, "https://example.com/verify")

                time.sleep(1)
                save_completed_item(item, completed)
                print(f"[COMPLETED] {item} saved to state.")

        print("\nAll batch items completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Batch interrupted: {e}\nProgress saved to state file.")


if __name__ == "__main__":
    run_batch_downloader()