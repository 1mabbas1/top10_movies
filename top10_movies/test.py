import requests

API_key  = '56d007c31ed986ca2947af65179cca97'
url = 'https://api.themoviedb.org/3/search/movie/'

response = requests.get(url, params={"api_key": API_key, "query": 'fight club'})
data = response.json()["results"]
print(data)

# movie_api_url = f"{url}/{movie_api_id}"
# # The language parameter is optional, if you were making the website for a different audience
# # e.g. Hindi speakers then you might choose "hi-IN"
# response = requests.get(movie_api_url, params={"api_key": API_key, "language": "en-US"})
# data = response.json()
