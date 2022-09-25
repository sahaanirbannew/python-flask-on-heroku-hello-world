from flask import Flask, request, render_template
ON_HEROKU = os.environ.get('ON_HEROKU')


@app.route('/') 
def hello_world():
  return "Hello World"


if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port = port)
