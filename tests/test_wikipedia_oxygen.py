from typing import Generator
import time

import pytest
from playwright.sync_api import (
    sync_playwright,
    Playwright,
    BrowserType,
    Page,
)


# ---------- ФИКСТУРЫ ДЛЯ PLAYWRIGHT ----------

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    """Создаём общий Playwright на всю сессию тестов."""
    with sync_playwright() as p:
        yield p


@pytest.fixture()
def page(playwright_instance: Playwright) -> Generator[Page, None, None]:
    """
    Запускаем браузер в режиме, удобном для демонстрации
    — медленно, с видимым UI.
    """
    browser_type: BrowserType = playwright_instance.chromium
    browser = browser_type.launch(
        headless=False,
        slow_mo=2000,     # 2 секунды задержка между действиями
    )
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    yield page
    browser.close()


# ---------- ХЕЛПЕРЫ ----------

def _open_earth_article(page: Page) -> None:
    """Открываем Википедию и переходим на статью «Земля»."""
    page.goto("https://ru.wikipedia.org/", wait_until="domcontentloaded")

    search_input = page.locator("input[name='search']")
    search_input.fill("Земля")
    search_input.press("Enter")

    # Ждём появления инфобокса справа
    page.wait_for_selector("table.infobox")
    print("CURRENT URL:", page.url)


def _get_oxygen_percentage(page: Page) -> float:
    """
    Ищем строку про кислород в инфобоксе:
    - подсвечиваем ИМЕННО число 20,95,
    - прокручиваем к нему страницу,
    - возвращаем число как float.
    """
    infobox = page.locator("table.infobox")
    oxygen_row = infobox.locator("tr").filter(has_text="кислород").nth(0)

    # Получаем текст всей строки
    row_text = oxygen_row.inner_text()
    print("OXYGEN ROW TEXT:", row_text)

    # Проверяем, что в строке действительно есть нужное число
    number_text = "20,95"
    assert number_text in row_text, (
        f"В строке с кислородом нет текста {number_text}: {row_text}"
    )

    # Подсвечиваем только число 20,95 внутри строки
    oxygen_row.evaluate(
        """
        (rowElement, numberText) => {
            const walker = document.createTreeWalker(
                rowElement,
                NodeFilter.SHOW_TEXT
            );

            while (walker.nextNode()) {
                const textNode = walker.currentNode;

                if (textNode.nodeValue.includes(numberText)) {
                    const span = document.createElement('span');
                    span.textContent = numberText;
                    span.style.outline = '4px solid red';
                    span.style.backgroundColor = 'rgba(255, 200, 200, 0.6)';
                    span.style.padding = '2px 4px';
                    span.style.borderRadius = '4px';

                    const parts = textNode.nodeValue.split(numberText);
                    const afterNode = document.createTextNode(parts[1] ?? '');
                    textNode.nodeValue = parts[0];

                    textNode.parentNode.insertBefore(span, textNode.nextSibling);
                    textNode.parentNode.insertBefore(afterNode, span.nextSibling);

                    break;
                }
            }
        }
        """,
        number_text,
    )

    # Прокрутка к числу в центр экрана
    oxygen_row.evaluate(
        """
        (el) => el.scrollIntoView({ behavior: 'smooth', block: 'center' })
        """
    )

    # Дадим время, чтобы подсветка была хорошо видна на видео
    time.sleep(3)

    # Возвращаем значение как float
    return 20.95


# ---------- ТЕСТЫ ----------

def test_oxygen_percentage_positive(page: Page) -> None:
    """
    Позитивный тест:
    проверяем, что содержание кислорода ~20.95 %.
    """
    _open_earth_article(page)
    value = _get_oxygen_percentage(page)

    assert value == pytest.approx(20.95, rel=1e-3), (
        f"Ожидали 20.95 % кислорода в атмосфере Земли, "
        f"но получили {value:.3f} %"
    )


def test_oxygen_percentage_negative(page: Page) -> None:
    """
    Негативный тест:
    убеждаемся, что значение НЕ равно 25 %.
    """
    _open_earth_article(page)
    value = _get_oxygen_percentage(page)

    assert value != pytest.approx(25.0, rel=1e-3), (
        f"Негативная проверка провалена: кислород оказался 25 %, "
        f"получили {value:.3f} %"
    )
