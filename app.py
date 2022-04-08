from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url) #requesting the web page from the flipkart website of the url
            flipkartPage = uClient.read() #reading the web page or the same html page which u see when u right click the page into its page source
            uClient.close() #closing the connection to the web server so that error doesnt arise
            flipkart_html = bs(flipkartPage, "html.parser") #beautiful soup parses the web page as HTML(structured) from the original byte format data
            # which can accessed using tags(like dictionary). u can call the html tags for which the data would be available
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"}) #searching for appropriate tag to redirect to the product link
            del bigboxes[0:3] #deleting the first 3 products of the list
            box = bigboxes[0] #accessing the the 3rd product of the list

            productLink = "https://www.flipkart.com" + box.div.div.div.a['href'] # check the website for the orientation of the html ot know the how much
            # div and a class are required to access a product. all the html classes give the area of the wesite if u rover over the inspect page of the right click of
            #  the page. u can use the library but for knowing the basics it is being hard coded intially later u  dont need to to do this as its the same
            #  for every search result.href contain the url of the specific product when u hover the mouse over that product
            #  flipkart is added to the url as it doesnt contain the flipkart website name.

            prodRes = requests.get(productLink) #gets the product page from the product url
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")# parsed into structured html of the particular product page from the byte type of the inspect right click of page
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})# finding the html page where there is the comment section

            #saving the already saved and searched ones in the file named the product name
            #it will save in the form dictionary

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
