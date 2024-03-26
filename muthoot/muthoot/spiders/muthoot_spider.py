import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains

class MuthootSpiderSpider(scrapy.Spider):
    name = "muthoot_spider"
    allowed_domains = ["www.muthootfinance.com"]
    start_urls = ["https://www.muthootfinance.com/branch-locator"]

    def parse(self, response):
                        driver=webdriver.Chrome()

                        driver.get('https://www.muthootfinance.com/branch-locator')

                        driver.fullscreen_window()
                        time.sleep(20)

                        # -----------------------------Clearing out pop-ups------------------------------
                        popup1_path='//*[@id="sf-bot-toaster"]/div[1]/img'
                        popup2_path='//*[@id="helpform"]/div/div[2]/a/img'
                        popup3_path='//*[@id="sf-chatbot-container"]/div/div[2]/div[1]/div/div[3]/div[3]/img'
                        popup1=driver.find_element(By.XPATH,popup1_path)
                        popup2=driver.find_element(By.XPATH,popup2_path)
                        popup3=driver.find_element(By.XPATH,popup3_path)
                        popup1.click()
                        popup2.click()
                        time.sleep(25)
                        popup3.click()
                        

                        # -----------------------Filtering on the basis of states-----------------------
                        for i in range(1,31):
                            x_path=f'//*[@id="state_branch_list"]/li[{i}]'
                            state=driver.find_element(By.XPATH,x_path)
                            actions = ActionChains(driver)
                            actions.move_to_element(state).perform()
                            state.click()

                            time.sleep(2)

                            targets=driver.find_elements(By.TAG_NAME,'tr')
                            targets_length=len(targets)

                            # ------Traversing to  the end of the page to get all the branches----------
                            while(True):
                                targets=driver.find_elements(By.TAG_NAME,'tr')
                                targets_length=len(targets)
                                if targets_length>10:
                                    more=driver.find_element(By.ID,'load_more')
                                    actions = ActionChains(driver)
                                    actions.move_to_element(more).perform()
                                    more.click()
                                    time.sleep(2)
                                    new_targets=driver.find_elements(By.TAG_NAME,'tr')
                                    new_targets_length=len(new_targets)
                                    if new_targets_length==targets_length:
                                        break
                                else:
                                    break
                            state=driver.find_element(By.CLASS_NAME,'label')
                            state=state.get_attribute("innerHTML")        
                            branches=driver.find_elements(By.TAG_NAME,'tr')
                            details=[]
                            for branch in branches:
                                details.append(str(branch.get_attribute("outerHTML")))

                                # ---------Gettting details for each branch in a particular state--------
                            for branch in details[1:]:
                                Name=branch.split('<td>')[1].split('>')[1].rstrip('</strong')
                                address=branch.split('<td>')[2].strip('</td>')
                                phone=branch.split('<td>')[3].split('"')
                                if len(phone)>1:
                                    phone=phone[1].lstrip('tel:')
                                else:
                                    phone='Not available'
                                
                                # ---------------------------Getting coordinates-------------------------
                                coords=branch.split('<td>')[4].replace(" ",'')
                                if '*' in coords:
                                    lat=coords.split('/')[6].split(',')[0][:-2]
                                    degrees=int(lat[:2])
                                    minutes=int(lat[3:5])
                                    seconds=int(lat[6:8])
                                    lat=degrees+minutes/60+seconds/3600

                                    lon=coords.split('/')[6].split(',')[1][:8]
                                    degrees=int(lon[:2])
                                    minutes=int(lon[3:5])
                                    seconds=int(lon[6:8])
                                    lon=degrees+minutes/60+seconds/3600
                                else:
                                    lat=coords.split('/')[6].split(',')[0]
                                    lon=coords.split('/')[6].split(',')[1].split('"')[0]
                                    if len(lat)<5 and len(lon)<5:
                                        lat='Not available'
                                        lon='Not available'

                            yield{    
                                "Name":Name,
                                "Address":address,
                                "State":state,
                                "Phone":phone,
                                "lat":lat,
                                "lon":lon,
                            }
 
                        driver.close()
