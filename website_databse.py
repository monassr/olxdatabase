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
    
    user_select=st.sidebar.selectbox('Options',('Seller Rating', 'Ads', 'Reviews', 'Used Cars','Ads From Seller', 'Top 5 Locations', 'Top 5 Sellers','Top 5 Brand/Models'), index=1)
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
                    output = pd.DataFrame(mycursor.fetchall())
                    
                    if output.shape[1] == 3:
                        output.columns = ['Name', 'Average Rating', 'Number of Reviews']
                    
                    
                    
                    st.subheader('Found '+ str(len(output)) + ' Entries')
                    
                    st.write(output)
                except:
                    st.subheader('No Ratings Exist For This Seller')
    elif((user_select== 'Ads')):
        
        query = q_adds()
        mycursor = mydb.cursor()
        mycursor.execute(query)
        output = pd.DataFrame(mycursor.fetchall())
        
        if output.shape[1] == 3:
            output.columns = ['Model', 'Number Of Listings', 'Average Price']


        st.subheader('Found '+ str(len(output)) + ' Entries')
        
        st.write(output)
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
                output = pd.DataFrame(mycursor.fetchall())
                output.columns = ['Price', 'Buyer Email', 'Ad Number', 'Description', 'Rating']
                output = output.drop('Ad Number', axis=1)


                st.subheader('Found '+ str(len(output)) + ' Entries')
                st.write(output)
            except:
                st.subheader('No Reviews For Given Ad')
                
    elif (user_select== 'Used Cars'):
                
        
        location = st.text_input("Enter Location")
        upper_price = st.text_input("Enter Max Price")
        lower_price = st.text_input("Enter Min Price")
        features = st.text_input("Enter Features seperated by Commas").split(',')
        
        query =  """
            SELECT Agent_Number, Ad_ID, Payment_options, Transmission_type,Brand,Model, Color, Fuel_Type, Year_model, Lower_Engine_Capacity, Upper_Engine_Capacity, Lower_Kilometer, Upper_Kilometer, Price
            FROM ad
            WHERE ad.Location = '{}'
            AND ad.Price BETWEEN '{}' AND '{}'
            """.format(location,lower_price,upper_price)
        
        for feature in features:
            query += "AND EXISTS (SELECT 1 FROM adfeatures WHERE adfeatures.AdID = ad.Ad_ID AND adfeatures.features LIKE '{}%')\n".format(feature)
        
        if st.button('Submit'):
            
            mycursor = mydb.cursor()
            mycursor.execute(query)
            output = pd.DataFrame(mycursor.fetchall())
            
            if output.shape[1] > 0:
                
                output.columns = ["Agent_Number", "Ad_ID",  "Payment_options", "Transmission_type",  "Brand", "Model",  "Color", "Fuel_Type", "Year_model", "Lower_Engine_Capacity", "Upper_Engine_Capacity", "Lower_Kilometer", "Upper_Kilometer", "Price"]
                
                output['Agent_Number'] = output['Agent_Number'].astype(str)
                output['Agent_Number'] = output['Agent_Number'].str.replace(',', '')
                
                output['Ad_ID'] = output['Ad_ID'].astype(str)
                output['Ad_ID'] = output['Ad_ID'].str.replace(',', '')
                
            st.subheader('Found '+ str(len(output)) + ' Entries')
            st.write(output)
    
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
            output = pd.DataFrame(mycursor.fetchall())
            
            if output.shape[1] > 0:
                
                output.columns = ["Ad_ID",  "Payment_options", "Transmission_type",  "Brand", "Model",  "Color", "Fuel_Type", "Year_model", "Lower_Engine_Capacity", "Upper_Engine_Capacity", "Lower_Kilometer", "Upper_Kilometer", "Price"]
                
                output['Ad_ID'] = output['Ad_ID'].astype(str)
                output['Ad_ID'] = output['Ad_ID'].str.replace(',', '')
                
            st.subheader('Found '+ str(len(output)) + ' Entries')
            st.write(output)
            
    elif(user_select == 'Top 5 Locations'):
        
        brand = st.text_input("Enter Brand: ")
        model = st.text_input("Enter Model: ")
        
        query = """  
        SELECT Location, COUNT(Ad_ID) as Total_Ads, AVG(Price) as Average_Price
        FROM ad
        WHERE Brand = '{}' AND Model = '{}'
        GROUP BY Location
        ORDER BY Total_Ads DESC, Average_Price 
        LIMIT 5;
        """.format(brand,model)
        
        try:
            if st.button('Submit'):
            
                mycursor = mydb.cursor()
                mycursor.execute(query)
                output = pd.DataFrame(mycursor.fetchall())
                
                if output.shape[1] > 0:
                    output.columns = ["Location", "Number of Invetory", "Average Price"]
                
                output['Average Price'] = output['Average Price'].astype(str)
                output['Average Price'] = output['Average Price'].str.replace(',', '')
                
                st.subheader('Found '+ str(len(output)) + ' Entries')
                st.write(output)
        except:
                st.subheader('ERROR')
                
    elif(user_select == 'Top 5 Sellers'):
        
        query = f"""
            SELECT AD.Agent_Number, agent.name, COUNT(AD.Ad_ID) as Total_Listings, AVG(AD.Price) as Avg_Price
            FROM ad AD
            JOIN agent ON AD.Agent_Number = agent.Phone_Number
            GROUP BY AD.Agent_Number, agent.name
            ORDER BY Total_Listings DESC, Avg_Price 
            LIMIT 5;
            """

        mycursor = mydb.cursor()
        mycursor.execute(query)
        output = pd.DataFrame(mycursor.fetchall())
        
        if output.shape[1] > 0:
            output.columns = ["Phone Number", "Name", "Total Listings", "Average Price"]
        
        output['Average Price'] = output['Average Price'].astype(str)
        output['Average Price'] = output['Average Price'].str.replace(',', '')
        
        output['Phone Number'] = output['Phone Number'].astype(str)
        output['Phone Number'] = output['Phone Number'].str.replace(',', '')
        
        st.subheader('Found '+ str(len(output)) + ' Entries')
        st.write(output)
    
    elif(user_select == 'Top 5 Brand/Models'):
                
        upper = st.text_input("Enter Max Year: ")
        lower = st.text_input("Enter Min Year: ")
        
        query = """
            SELECT Brand, Model, COUNT(Ad_ID) as Total_Inventory, AVG(Price) as Average_Price
            FROM ad
            WHERE Year_model BETWEEN '{}' AND '{}'
            GROUP BY Brand, Model
            ORDER BY Total_Inventory DESC, Average_Price
            LIMIT 5;
            """.format(lower,upper)

        try:
            if st.button('Submit'):
            
                mycursor = mydb.cursor()
                mycursor.execute(query)
                output = pd.DataFrame(mycursor.fetchall())
                
                if output.shape[1] > 0:
                    output.columns = ["Brand", "Model", "Number of Invertory", 'Average Price']
                
                output['Average Price'] = output['Average Price'].astype(str)
                output['Average Price'] = output['Average Price'].str.replace(',', '')
                
                st.subheader('Found '+ str(len(output)) + ' Entries')
                st.write(output)
        except:
                st.subheader('ERROR')
         
        
        
       
        
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


