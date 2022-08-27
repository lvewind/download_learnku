# -\*- coding: UTF-8 -\*-
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
import selenium.common
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from copy import deepcopy
import os
import pdfkit


class EarthDriver(Chrome):
    def __init__(self, user_data_dir=""):
        options = ChromeOptions()
        options.add_argument('window-size=2560,1440')
        self.user_data_dir = user_data_dir
        self.street_view_on = False
        if self.user_data_dir:
            options.add_argument('user-data-dir=' + self.user_data_dir)

        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # options.add_argument('--headless')

        try:
            super(EarthDriver, self).__init__(service=Service(ChromeDriverManager().install()), options=options)
        except selenium.common.exceptions.SessionNotCreatedException as e:
            print(e)
        except selenium.common.exceptions.InvalidArgumentException:
            print("请关闭浏览器再使用本工具")
        except selenium.common.exceptions.WebDriverException:
            print("请重新设置浏览器用户目录后重新启动本软件")

        self.index_page_list = []
        self.chapter_page_list = []
        self.css = ["vendors.css", "app.css"]
        self.pdfkit_options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }

    def get_index_page(self):
        try:
            url = "https://learnku.com/laravel/courses"
            self.get(url)
            self.switch_to.default_content()
            container = self.find_element(By.CLASS_NAME, "container")
            index_urls_el = container.find_elements(By.CLASS_NAME, "button")
            for a in index_urls_el:
                href = a.get_attribute("href")
                self.index_page_list.append(href)
            self.index_page_list = self.index_page_list[1: 7]
            print(self.index_page_list)
        except selenium.common.WebDriverException:
            pass

    def get_chapter_page_list(self):
        for url in self.index_page_list:
            chapter_list = []
            self.get(url)
            self.switch_to.default_content()
            chapter_name = self.find_element(By.CLASS_NAME, "body > div.pusher > div.main.container > div > div > div > div > div.book.header > div > div > div.content > div.header").text
            chapter_container_el = self.find_element(By.CLASS_NAME, "sorted_table")
            if chapter_container_el:
                chapter_list_el = chapter_container_el.find_elements(By.TAG_NAME, "a")
                if chapter_list_el:
                    for a in chapter_list_el:
                        chapter_list.append({"name": a.get_attribute("innerText"), "url": a.get_attribute("href")})
                    self.chapter_page_list.append({"chapter_name": chapter_name,
                                                   "chapter": deepcopy(chapter_list)})
                    print(self.chapter_page_list[-1])

    def print_chapter_page(self):
        for chapter in self.chapter_page_list:
            chapter_dir = os.path.join(os.getcwd(), chapter.get("chapter_name"))
            chapter_list = chapter.get("chapter")
            if not os.path.exists(chapter_dir):
                os.mkdir(chapter_dir)

            if chapter_list:
                for page in chapter_list:
                    self.get(page.get("url"))
                    self.switch_to.default_content()
                    try:
                        self.del_el("body > div.ui.vertical.sidebar.menu.accordion.following.visible.wikis.book-sidemenu.pb-5")
                        self.del_el("#topnav")
                        self.del_el("body > div.pusher > div.main.container > div.toc-wrapper.content.active")
                        self.del_el("body > div.pusher > div.main.container > div.ui.centered.grid.container.stackable.docs-article > div > div:nth-child(2)")
                        self.del_el("body > div.pusher > div.main.container > div.ui.centered.grid.container.stackable.docs-article > div > div.ui.message.basic.share-wrap")
                        self.del_el("body > div.pusher > div.main.container > div.ui.centered.grid.container.stackable.docs-article > div > div.ui.segment.two.column.grid.doubling.hide-on-mobile.stackable.extra-padding.book-ads")
                        # self.del_el("#topics-list")
                        self.del_el("body > div.pusher > div.ui.inverted.vertical.footer.segment")
                        self.del_el("#scrollUp")
                        self.del_el("body > div.pusher > div.main.container > div.ui.centered.grid.container.stackable.docs-article > div > div.wiki.navigator.hide-on-mobile")
                    except selenium.common.exceptions.InvalidElementStateException as e:
                        print(e)
                    except selenium.common.exceptions.NoSuchElementException as e:
                        print(e)
                    file_name = os.path.join(chapter_dir, page.get("name") + ".pdf")
                    # self.execute_script('document.title=arguments[0];window.print();', file_name)
                    print(file_name)
                    pdfkit.from_string(self.page_source, output_path=file_name, options=self.pdfkit_options)

    def del_el(self, selector):
        self.execute_script("""
                var element = document.querySelector('""" + selector + """');
            if (element)
                element.parentNode.removeChild(element);
        """, selector)


if __name__ == "__main__":
    download_learn_ku = EarthDriver(user_data_dir="C:\\Users\\Cat\\AppData\\Local\\Google\\Chrome\\User Data")
    download_learn_ku.get_index_page()
    download_learn_ku.get_chapter_page_list()
    download_learn_ku.print_chapter_page()
    download_learn_ku.quit()
