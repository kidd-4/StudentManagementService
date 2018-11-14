import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask,jsonify
from flask import abort
from flask import request

meta_data = pd.read_csv('/Users/grey/Documents/Big Data/project/files/movies_metadata.csv', encoding='mac_roman')
links = pd.read_csv('/Users/grey/Documents/Big Data/project/files/links_small.csv', encoding='mac_roman')
links = links[links['tmdbId'].notnull()]['tmdbId'].astype('int')

meta_data = meta_data.drop([4831, 19730, 29503, 35587])
meta_data = meta_data.drop_duplicates(['title'])
meta_data['id'] = meta_data['id'].astype('int')

lmd = meta_data[meta_data['id'].isin(links)]
lmd['description'] = lmd['overview']
lmd['description'] = lmd['description'].fillna('')

tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform(lmd['description'])
# print(tfidf_matrix)

lmd = lmd.reset_index()
titles = lmd['title']
indices = pd.Series(lmd.index, index=lmd['title'])


movies = [
]

# print(indices)

app = Flask(__name__)

@app.route('/RecommendMovies',methods=['POST'])
def get_recommendations():
    if not request.json or not 'moviesName' in request.json or not 'moviesRating' in request.json:
       	abort(400)
    moviesName = request.json.get('moviesName')
    moviesRating = request.json.get('moviesRating')
    if len(moviesRating) != len(moviesName):
         abort(400)

    userProfile = []
    for i in range(0,len(moviesName)):
        userProfile.append([moviesName[i],moviesRating[i]])

    # for i in range(0,len(userProfile)):
    #      print(userProfile[i])
    recommendations = print_res(userProfile)
    movies = []
    for i in range(0,len(recommendations)):
        movie = {
			'movieName': recommendations[i]
		}
        movies.append(movie)
    return jsonify({'movie':movies})

def get_recommendations(userProfile):
	t = tfidf_matrix[indices[userProfile[0][0]]] * userProfile[0][1]
	for i in range(1, len(userProfile)):
		t = t + tfidf_matrix[indices[userProfile[i][0]]] * userProfile[i][1]
	# print(t)
	cos = linear_kernel(t, tfidf_matrix)
	cos = cos[0]
	sim_scores = list(enumerate(cos))
	sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
	sim_scores = sim_scores[1:20]
	movie_indices = [i[0] for i in sim_scores]
	return titles.iloc[movie_indices]



def print_res(userProfile):
	res = get_recommendations(userProfile)
	res = list(res)
	recommendMoveis = []
	for i in range(0, len(res)):
		flag = 0
		for j in range(0, len(userProfile)):
			if res[i] == userProfile[j][0]:
				flag = 1
		if flag == 0:
			# print(res[i])
			recommendMoveis.append(res[i])
	return recommendMoveis

# userProfile = [['Spider', 4.0], ['The Matrix Revolutions', 3.0], ['Harry Potter and the Chamber of Secrets', 5.0]]
# print_res(userProfile)

if __name__ == '__main__':
    app.run(host= '172.30.107.196')