import time
from token import tok_name

from s3p_sdk.plugin.payloads.parsers import S3PParserBase
from s3p_sdk.types import S3PRefer, S3PDocument
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
import datetime
from selenium.webdriver.remote.webelement import WebElement


class EPIParser(S3PParserBase):
    """
    Парсер, использующий базовый класс парсера S3P
    """

    def __init__(self, refer: S3PRefer, driver: WebDriver, urls: list, timeout: int = 20, max_count_documents: int = None,
                 last_document: S3PDocument = None):
        super().__init__(refer, max_count_documents, last_document)

        # Тут должны быть инициализированы свойства, характерные для этого парсера. Например: WebDriver
        self.URLs = urls
        self._driver = driver
        self._timeout = timeout
        self.is_cookie_checked = False
        self._wait = WebDriverWait(self._driver, timeout=self._timeout)

    def _parse(self) -> None:
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self._refer.to_logging}")
        for url in self.URLs:
            self._driver.get(url)
            self._cookie_accepter()

            list_of_news = self._driver.find_elements(By.CLASS_NAME, 'news__list-item')
            list_of_links = [news.find_element(By.CLASS_NAME, 'news__list-item-buttons-holder').find_element(By.TAG_NAME, 'a').get_attribute('href') for news in list_of_news]

            print(list_of_links)
            for link in list_of_links:
                self._driver.get(url=link)
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                date_news = datetime.datetime.strptime(
                    self._driver.find_element(By.CLASS_NAME, 'news-detail__hero-date.subtitle').text, '%B %d, %Y')
                news_name = self._driver.find_element(By.CLASS_NAME, 'news-detail__hero-title.news-article-title').text

                news_text_web_element = self._driver.find_element(By.CLASS_NAME, 'pagebuilder').find_elements(By.CLASS_NAME,'title-text')

                news_text = ''
                if news_text_web_element:
                    for web_element in news_text_web_element:
                        tags_p = web_element.find_elements(By.TAG_NAME, 'p')
                        news_text += " ".join([tag.text for tag in tags_p])
                else:
                    news_text = self._driver.find_element(By.CLASS_NAME, 'pagebuilder').find_element(
                        By.CLASS_NAME, 'simple-text__text.body-text.redactor').text

                annotation_text = self._checking_for_annotation()

                document = S3PDocument(
                    title=news_name,
                    abstract=annotation_text if annotation_text else None,
                    link=link,
                    text=news_text,
                    other=None,
                    loaded=datetime.datetime.now(),
                    id=None,
                    published=date_news,
                    storage=None
                )
                self._find(document=document)

    def _cookie_accepter(self):
        try:
            some = self._driver.find_element(By.CLASS_NAME, 'CybotCookiebotDialogContentWrapper')\
                    .find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
            some.click()
        except Exception:
            self.logger.warn(f'There is no need to accept cookie')


    def _checking_for_annotation(self):
        try:
            result = self._driver.find_element(By.CLASS_NAME, 'news-detail__intro-text.body-text')
            if result.text == '':
                return None
            else:
                return result.text
        except Exception:
            self.logger.warn(f'There is no annotation')
            return None

    def _parse_page(self, url: str) -> S3PDocument:
        doc = self._page_init(url)
        return doc

    def _page_init(self, url: str) -> S3PDocument:
        self._initial_access_source(url)
        return S3PDocument()

    def _encounter_pages(self) -> str:
        """
        Формирование ссылки для обхода всех страниц
        """
        _base = self.URL
        _param = f'&page='
        page = 0
        while True:
            url = str(_base) + _param + str(page)
            page += 1
            yield url

    def _collect_doc_links(self, _url: str) -> list[str]:
        """
        Формирование списка ссылок на материалы страницы
        """
        try:
            self._initial_access_source(_url)
            self._wait.until(ec.presence_of_all_elements_located((By.CLASS_NAME, '<class контейнера>')))
        except Exception as e:
            raise NoSuchElementException() from e
        links = []

        try:
            articles = self._driver.find_elements(By.CLASS_NAME, '<class контейнера>')
        except Exception as e:
            raise NoSuchElementException('list is empty') from e
        else:
            for article in articles:
                try:
                    doc_link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
                except Exception as e:
                    raise NoSuchElementException(
                        'Страница не открывается или ошибка получения обязательных полей') from e
                else:
                    links.append(doc_link)
        return links

    def _initial_access_source(self, url: str, delay: int = 2):
        self._driver.get(url)
        self.logger.debug('Entered on web page ' + url)
        time.sleep(delay)
