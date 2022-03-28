import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import math
def saveInJson(data, title):
    fileName= title+ ".json"
    # if os.path.exists(fileName):
    #     os.remove(fileName)
    f= open(fileName, 'a', encoding='utf-8-sig')
    f.write(json.dumps(data, ensure_ascii=False, indent= 4))
    f.close()
    print('Saved successfully into json!')

class ProductScraper():
    def __init__(self):
        self.base_url = "http://okinawa.bookoo.com"
    def onePageScrape(self, pageUrl, category):
        imgBase= 'https://s3item-bookooinc.netdna-ssl.com/s640_'
        newPage= []
        response= requests.get(pageUrl)
        soup= BeautifulSoup(response.text, 'html.parser')
        products= soup.select('a[class*="card searchitem"]')
        try:
            category= category[1:]
        except:
            pass
        for product in products:
            listing_number= product['href']
            res1= requests.get(self.base_url+ listing_number)
            soup1= BeautifulSoup(res1.text, 'html.parser')
            itemDetails= soup1.find('div', attrs= {'id': 'itemDetails'})
            try:
                listing_number= listing_number[3:]
            except:
                pass
            name= ''
            try:
                name= itemDetails.find('h1').text
            except:
                pass
            price= ''
            try:
                price= itemDetails.find('div', attrs= {'class': 'subTitle clearFix'}).find('span', attrs= {'class': 'price'}).text
            except:
                pass
            listing_date= ''
            owner_address= ''
            try:
                temp= itemDetails.find('div', attrs= {'class': 'subTitle clearFix'}).text.rsplit(',', 1)
                listing_date= temp[1]
                owner_address= temp[0].rsplit(' in ', 1)[1]
            except:
                pass
            owner_name= ''
            owner_id= ''
            try:
                owner_name= itemDetails.find('a', attrs= {'class': 'itemOwner'}).text
                owner_id= itemDetails.find('a', attrs= {'class': 'itemOwner'})['href']
            except:
                pass
            owner_phone= ''
            try:
                owner_phone= itemDetails.find('a', attrs= {'class': 'phoneContents'}).text.split(':')[1]
            except:
                pass
            pictures= []
            try:
                itemImageHolder= itemDetails.find('div', attrs= {'id': 'itemImageHolder'})
                pictures_tmp= itemImageHolder.find_all('img')
                for picture_tmp in pictures_tmp:
                    try:
                        pictures.append(imgBase+ picture_tmp['guid']+ '.jpg')
                    except:
                        pass
            except:
                pass
            description= ''
            try:
                description= itemDetails.find('p', attrs= {'id': 'description'}).text
            except:
                pass
            
            # here owner part
            follower_count= ''
            owner_reputation= ''
            sells_mostly= ''
            about_owner= ''
            if owner_id:
                ownerRes= requests.get(self.base_url+ owner_id)
                ownerSoup= BeautifulSoup(ownerRes.text, 'html.parser')
                try:
                    follower_count= ownerSoup.find('div', attrs= {'class': 'followers'}).find('span', attrs= {'class': 'count'}).text
                except:
                    pass
                try:
                    owner_reputation= ownerSoup.find('div', attrs= {'class': 'option response'}).text
                except:
                    pass
                try:
                    sells_mostly= ownerSoup.find('div', attrs= {'class': 'sellsMostly'}).text
                except:
                    pass
                try:
                    about_owner= ownerSoup.find('div', attrs= {'class': 'description'}).text
                except:
                    pass
            new = {'category': category, 'name': name, 'price': price, 'listing_date': listing_date, 'listing_number': listing_number, 'pictures': pictures, 'description': description, 'owner_name': owner_name, 'owner_address': owner_address, 'owner_phone': owner_phone, 'follower_count': follower_count, 'owner_reputation': owner_reputation, 'sells_mostly': sells_mostly, 'about_owner': about_owner }
        
            newPage.append(new)
        print("One page scraped!")
        saveInJson(newPage, "bookoo")
    def oneCategoryScrape(self, category):
        categoryUrl= self.base_url+category
        response= requests.get(categoryUrl)
        soup= BeautifulSoup(response.text, 'html.parser')
        pageCount= 1
        try:
            pageCount= soup.find('input', attrs= {'class': 'page'})['value']
            pageCount= int(pageCount.split(' ')[-1])
        except:
            pass
        for page in range(pageCount):
            pageUrl= categoryUrl+"/page"+str(page+1)
            self.onePageScrape(pageUrl, category)

        
    def scrape(self):
        # write csv headers
        # if os.path.exists('result.csv'):
        #     os.remove('result.csv')
        # columns=['Forum', 'Name', 'Post_Title', 'Post', 'Replies']
        # df = pd.DataFrame(columns = columns)
        # df.to_csv('result.csv', mode='x', index=False, encoding='utf-8')

        # get forum urls
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        categoryContainer= soup.find('ul', attrs= {'id': 'categoryContainer'})
        # print('categoryContainer', categoryContainer)
        categorys= categoryContainer.find_all('a')
        # print('categorys', categorys)
        categorys= list(map(lambda x: x['href'], categorys))
        # print("categorys===", categorys)
        for category in categorys:
            self.oneCategoryScrape(category)
        # for item in soup.find_all('ul', attrs= {'id': 'categoryContainer'}):
        #     tmp = item.find('a')
        #     if tmp != None:
        #         url= tmp.attrs['href'].strip()
        #         forum_name= self.get_forum_name(url)
        #         print(forum_name)
        #         page_num= self.page_num(url)
        #         print(page_num)
        #         for page in range(1, page_num+1):
        #             page_url= url+'/p'+str(page)
        #             response1= requests.get(page_url)
        #             soup1= BeautifulSoup(response1.text, 'html.parser')
        #             tmp1= soup1.find('ul', attrs= {'class': 'DataList Discussions'})
        #             for topic_title_url_tmp in tmp1.find_all('li'):
        #                 topic_title_url= topic_title_url_tmp.find_all('a')[1].attrs['href'].strip()
        #                 new= self.scrape_post(topic_title_url)
        #                 new.update({'Forum': forum_name})
        #                 print("I have inserted one column to csv now")
        #                 items= []
        #                 items.append(new)
        #                 # save datas in csv
        #                 df = pd.DataFrame(items, columns = columns)
        #                 df.to_csv('result.csv', mode='a', header=False, index=False, encoding='utf-8')
        #         print('I have inserted one forum now')
        print('done')
                    
    
    def get_forum_name(self, url):
        response = requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('section', attrs= {'class': 'Content'})
        if tmp != None:
            forum_name= tmp.find('h1').text
            return forum_name
        return ""

    def page_num(self, url):
        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('div', attrs= {'class': 'Pager'})
        page_num= 1
        if tmp!= None:
            tmp1= tmp.find_all('a')
            tmp2= tmp1[-3].text.strip()
            page_num= int(tmp2)
        return page_num

    def reply_page_num(self, url):
        reply_page_num= 1
        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        tmp= soup.find('span', attrs= {'class': 'Pager'})
        if tmp!= None:
            tmp1= tmp.find_all('a')
            tmp2= tmp1[-3].text.strip()
            reply_page_num= int(tmp2)
        return reply_page_num

    def scrape_post(self, url):
        response= requests.get(url)
        soup= BeautifulSoup(response.text, 'html.parser')
        post_title= soup.find('h1').text
        name = soup.find('a', attrs= {'class':'Username js-userCard'}).text
        print(name)
        tmp= soup.find('div', attrs= {'class': 'Message userContent'})
        post= " "
        if tmp != None:
            post= tmp.text.replace('<br>', '\n')
        replies= ""
        reply_page_num= self.reply_page_num(url)
        for reply_page in range(1, reply_page_num+1):
            page_url= url+'/p'+str(reply_page)
            response_page= requests.get(page_url)
            soup_page= BeautifulSoup(response_page.text, 'html.parser')
            tmp2= soup_page.find('ul', attrs= {'class': 'MessageList DataList Comments'})
            if tmp2 != None:
                for reply in tmp2.find_all('li'):
                    tmp4= " "
                    if reply.find('a', attrs= {'class':'Username js-userCard'}):
                        tmp4= reply.find('a', attrs= {'class':'Username js-userCard'}).text
                    tmp5= " "
                    if reply.find('div', attrs={'class': 'Message userContent'}):
                        tmp5= reply.find('div', attrs={'class': 'Message userContent'}).text.replace('<br>', '\n')
                    tmp3= " "
                    if reply.find('div', attrs={'class': 'Signature UserSignature userContent'}):
                        tmp3= reply.find('div', attrs={'class': 'Signature UserSignature userContent'}).text.replace('<br>', "\n")
                    replies+= tmp4 + '\n'+tmp5+'\n'+tmp3+'\n'+ '@messages@'+'\n'
        new= {'Name': '', 'Post_Title': '', 'Post': '', 'Replies': ''}
        new['Name']= name
        new['Post_Title']= post_title
        new['Post']= post
        new['Replies']= replies
        return new

if __name__ == '__main__':
    scraper = ProductScraper()
    scraper.scrape()