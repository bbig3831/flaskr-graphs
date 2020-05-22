from blog import app


app.secret_key = 'secretkey'

if __name__ == '__main__':

    app.run(debug=True)