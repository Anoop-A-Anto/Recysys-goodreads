 

import streamlit as st
import numpy as np
import pandas as pd

import sqlite3
conn=sqlite3.connect('data.db')
c=conn.cursor()

import os
import warnings
warnings.filterwarnings('ignore')

import tensorflow.keras as tf
import joblib

import base64
from io import BytesIO

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    #Generates a link allowing the data in a given panda dataframe to be downloaded
    #in:  dataframe
    #out: href string
    
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc

##df = ... # your dataframe
##st.markdown(get_table_download_link(df), unsafe_allow_html=True)



new_model=tf.models.load_model("modelrecsys.h5")
co=joblib.load("contentsfile.joblib")
titlefile=joblib.load('title.joblib')




def create_usertable():
  c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')

def add_userdata(username,password):
  c.execute('INSERT INTO userstable(username, password) VALUES(?,?)',(username,password))
  conn.commit()

def login_user(username,password):
  c.execute('SELECT * FROM userstable WHERE username=? AND password=?',(username,password))
  data=c.fetchall()
  return data

def view_all_users():
  c.execute('SELECT * FROM userstable')
  data=c.fetchall()
  return data


st.title("...WELCOME...")
st.title("HYBRID BOOK RECOMMENDATION SYSTEM")
menu=["Home","Login", "Sign up","Book"]
choice=st.sidebar.selectbox("Menu",menu)

if choice=="Home":
  st.subheader("HOME")

elif choice=="Login":
  st.subheader("Login Section")
  
  username=st.sidebar.text_input("username")
  password=st.sidebar.text_input("password",type='password')
  
  if st.sidebar.checkbox("Login"):
    
    # if password=="12345":
    create_usertable()
    result=login_user(username,password)
    if result:

      st.success("LOGGED IN SUCCESSFULLY AS {}".format(username))
      
      task=st.selectbox("Task",["Add task","Analytics","Profile"])
      
      if task=="Add task":
        st.subheader("Add your task")
      elif task=="Analytics":
        st.subheader("Top N number of Book Recommondations predicted realtime")
        user_id = st.number_input('user_id',  min_value=1, max_value=53424, value=1)

        us_id_temp=[user_id for i in range(len(co['book_id']))]


        reccom = new_model.predict([pd.Series(us_id_temp),co['book_id'],co.iloc[:,1:]])
        recc_df=pd.DataFrame(reccom,columns=["rating"])
        recc_df["book_id"]=co['book_id'].values
        recc_df.sort_values(by="rating",ascending=False,inplace=True)
        num= st.number_input('required_reccomondation_count',  min_value=1, max_value=500, value=5)
        recc_df_table=recc_df[:num]
        recc_df_table=pd.merge(recc_df_table,titlefile,left_on="book_id",right_on="book_id")
        st.write(recc_df_table.iloc[:,:6])

        st.markdown(get_table_download_link(recc_df_table.iloc[:,:6]), unsafe_allow_html=True)




        
      elif task=="Profile":
        st.subheader("User Profiles")
        user_result=view_all_users()
        clean_db=pd.DataFrame(user_result,columns=["Username","Password"])
        st.dataframe(clean_db)

    else:
      st.warning("Incorrect password/username")

elif choice=="Sign up":
  st.subheader("Create New Account")
  newuser=st.sidebar.text_input("username")
  newpassword=st.sidebar.text_input("password",type='password')

  if st.button("Sign up"):
    create_usertable()
    add_userdata(newuser,newpassword)
    st.success("You have successfully created a valid account")
    st.info("Goto Login menu")

elif choice=="Book":
  st.subheader("Enter Details...")
  userid=st.sidebar.text_input("userid")
  bookid=st.sidebar.text_input("bookid")
  st.button("SUBMIT")
  

