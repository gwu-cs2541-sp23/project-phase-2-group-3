from flask import Flask, session, render_template, redirect, url_for, request
import mysql.connector

app = Flask('app')
app.secret_key = 'this is super secret'

mydb = mysql.connector.connect(
  host = "group3phase2-taylor23.c71jatiazsww.us-east-1.rds.amazonaws.com",
  user = "admin",
  password = "marksheilazack",
  database = "university"
)