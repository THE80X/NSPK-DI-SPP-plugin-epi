# NSPK-DI-SPP-plugin-epi

## Написанные методы

### _checking_for_annotation
```python
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
```
Данный метод был написан для того чтобы отдельно выделять аннотацию новости, которую впоследствии программа будет помещать в abstract.

### _cookie_accepter
```python
def _cookie_accepter(self):
    try:
        some = self._driver.find_element(By.CLASS_NAME, 'CybotCookiebotDialogContentWrapper')\
                .find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
        some.click()
    except Exception:
        self.logger.warn(f'There is no need to accept cookie')
```
Данный метод был написан для того, чтобы при каждом открытии страницы проверять необходимость принятия куков и в случае необходимости - принимать.