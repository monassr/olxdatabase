import mysql.connector
import streamlit as st
import pandas as pd
import datetime
import re

pattern = r'\d{4}-\d{2}-\d{2}'

def connect_to_database():
    
    mydb = mysql.connector.connect(
    host = "db4free.net",
    user = "monasr",
    password = "monasr1658",
    database = "olxxdatabase",
    )
    
    return mydb


def register_user(mydb):
    
    user_email = st.text_input("Enter User Email:")
    user_dob = st.text_input("Enter DOB: YYYY-MM-DD")
    user_name = st.text_input("Enter User Name:")
    gender = st.text_input("Enter Gender: M or F")
    
    pattern = r'\d{4}-\d{2}-\d{2}'

    match = re.match(pattern, user_dob)


    if(match):
        dob_date = datetime.datetime.strptime(user_dob, '%Y-%m-%d')

        today = datetime.date.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    
    try:
        if st.button("Submit"):
            
            query= """
                INSERT INTO user VALUES (\'"""+user_email+"""\', \'"""+user_dob+ """\', \'"""+user_name+"""\',\'"""+str(age)+"""\', \'"""+gender+"""\')
                """
            
            try:
                mycursor = mydb.cursor()
                mycursor.execute(query)
                mydb.commit()
                st.subheader('User Added Succesfully!')
            except:
                st.subheader('ERROR')
    except:
        st.subheader('ERROR')

            
    
    return 

def add_review(mydb):

    price = st.text_input("Enter Selling Price")
    email_add = st.text_input("Enter Your Email Address")
    ad = st.text_input("Enter Ad Number")
    description = st.text_input("Add Description")
    rating = st.text_input("Rating: 1-5")

    if st.button("Submit"):
        
        query= """
            INSERT INTO review VALUES (\'"""+price+"""\', \'"""+email_add+ """\', \'"""+ad+"""\',\'"""+description+"""\', \'"""+rating+"""\')
            """
        
        try:
            mycursor = mydb.cursor()
            mycursor.execute(query)
            mydb.commit()
            st.subheader('Review Added Succesfully!')
        except:
            st.subheader('ERROR')

    
    return

def search(mydb):

    st.sidebar.header("Search For")
    
    user_select=st.sidebar.selectbox('Options',('Seller Rating', 'Ads', 'Reviews', 'Used Cars','Ads From Seller'), index=1)
    sql=""

    if((user_select== 'Seller Rating')):
        
        
        user_input = st.text_input("Enter Seller Number: ")
        
        if st.button("Submit"):
            
                query = """
                    SELECT agent.name, AVG(review.rating) AS Avg_Rating, COUNT(*) AS Number_Reviews
                    FROM agent
                    JOIN ad ON agent.Phone_Number = ad.Agent_Number
                    JOIN review ON review.Ad_ID = ad.Ad_ID
                    WHERE agent.Phone_Number = '{}'
                    GROUP BY agent.name
                    """.format(user_input)
                
                try:
                    mycursor = mydb.cursor()
                    mycursor.execute(query)
                    result = pd.DataFrame(mycursor.fetchall())
                    
                    if result.shape[1] == 3:
                        result.columns = ['Name', 'Average Rating', 'Number of Reviews']
                    
                    st.subheader('Result:')
                    st.write(result)
                except:
                    st.subheader('No Ratings Exist For This Seller')
            
        
        
    elif((user_select== 'Ads')):
        
        query = q_adds()
        mycursor = mydb.cursor()
        mycursor.execute(query)
        result = pd.DataFrame(mycursor.fetchall())
        
        if result.shape[1] == 3:
            result.columns = ['Model', 'Number Of Listings', 'Average Price']


        st.subheader('Result:')
        st.write(result)
    elif (user_select== 'Reviews'):


        user_input = st.text_input("Enter Ad Number:")

        if st.button("Submit"):
            
            try:
                sql = """
                Select * 
                FROM review
                where Ad_id = """+user_input+""";
                """
                mycursor = mydb.cursor()
                mycursor.execute(sql)
                result = pd.DataFrame(mycursor.fetchall())
                result.columns = ['Price', 'Buyer Email', 'Ad Number', 'Description', 'Rating']
                result['Ad Number'] = result['Ad Number'].astype(str)
                result['Ad Number'] = result['Ad Number'].str.replace(',', '')

                st.subheader('Result:')
                st.write(result)
            except:
                st.subheader('No Reviews For Given Ad')
                
    elif (user_select== 'Used Cars'):
                
        
        location = st.text_input("Enter Location")
        upper_price = st.text_input("Enter Upper Price range")
        lower_price = st.text_input("Enter Lower Price range")
        features = st.text_input("Enter Features seperated by Commas").split(',')
        
        query =  """
            SELECT Agent_Number, Ad_ID, Payment_options, Transmission_type,Brand,Model, Color, Fuel_Type, Year_model, Lower_Engine_Capacity, Upper_Engine_Capacity, Lower_Kilometer, Upper_Kilometer, Price
            FROM ad
            WHERE ad.Location = '{}'
            AND ad.Price BETWEEN '{}' AND '{}'
            """.format(location,lower_price,upper_price)
        
        for feature in features:
            query += f"AND EXISTS (SELECT 1 FROM adfeatures WHERE adfeatures.AdID = ad.Ad_ID AND adfeatures.features LIKE '{feature}%')\n"
        
        if st.button('Submit'):
            
            mycursor = mydb.cursor()
            mycursor.execute(query)
            result = pd.DataFrame(mycursor.fetchall())
            
            if result.shape[1] > 0:
                
                result.columns = ["Agent_Number", "Ad_ID",  "Payment_options", "Transmission_type",  "Brand", "Model",  "Color", "Fuel_Type", "Year_model", "Lower_Engine_Capacity", "Upper_Engine_Capacity", "Lower_Kilometer", "Upper_Kilometer", "Price"]
                
                result['Agent_Number'] = result['Agent_Number'].astype(str)
                result['Agent_Number'] = result['Agent_Number'].str.replace(',', '')
                
                result['Ad_ID'] = result['Ad_ID'].astype(str)
                result['Ad_ID'] = result['Ad_ID'].str.replace(',', '')
                
            st.subheader('Result:')
            st.write(result)
    
    elif(user_select == 'Ads From Seller'):
        
        
         
        phone = st.text_input("Enter Seller Phone Number: ")
        
        query =  """
         SELECT Ad_ID, Payment_options, Transmission_type,Brand,Model, Color, Fuel_Type, Year_model, Lower_Engine_Capacity, Upper_Engine_Capacity, Lower_Kilometer, Upper_Kilometer, Price
         FROM ad
         JOIN agent ON ad.Agent_Number = agent.Phone_Number
         WHERE ad.Agent_Number = '{}'
         """.format(phone)
        
        if st.button('Submit'):
            
            mycursor = mydb.cursor()
            mycursor.execute(query)
            result = pd.DataFrame(mycursor.fetchall())
            
            if result.shape[1] > 0:
                
                result.columns = ["Ad_ID",  "Payment_options", "Transmission_type",  "Brand", "Model",  "Color", "Fuel_Type", "Year_model", "Lower_Engine_Capacity", "Upper_Engine_Capacity", "Lower_Kilometer", "Upper_Kilometer", "Price"]
                
                result['Ad_ID'] = result['Ad_ID'].astype(str)
                result['Ad_ID'] = result['Ad_ID'].str.replace(',', '')
                
            st.subheader('Result:')
            st.write(result)
            
         
        
        
       
        
    return
    
def q_adds():
    
    query = """
    Select *
    FROM ad
    WHERE Model = 'TEMP';
    """
    
    user_brand = st.text_input("Enter Brand:")
    user_bt = st.text_input("Enter Body Type:")
    user_year = st.text_input("Enter Year:")
    user_location = st.text_input("Enter Location:")
    
    if st.button("Submit"):
        query ="""
            SELECT
                Model,
                COUNT(*) AS num_listings,
                AVG(Price) AS average_price
            FROM
                ad
            WHERE
                Brand = '{}' AND
                Body_Type = '{}' AND
                Year_model = {} AND
                Location = '{}'
            GROUP BY
                Model
            """.format(user_brand, user_bt, user_year, user_location)
    
    return query
    
def q_reviews():

    
    
    user_input = "900"
    user_input = st.text_input("Enter Ad Number:")

    if st.button("Submit"):
        sql = """
        Select * 
        FROM review
        where Ad_id = """+user_input+""";
        """
        
    return sql
    
mydb = connect_to_database()

st.write ('''
# OLX Database
''')

st.sidebar.header("What would you like to do?")

nav=st.sidebar.selectbox('Choose',  ('Register a user', 'Add Review For Ad', 'Search'), index=1)

if nav =='Register a user':
    register_user(mydb)
elif nav =='Add Review For Ad':
    add_review(mydb)
elif nav =='Search':
    search(mydb)


