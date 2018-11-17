import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask,jsonify
from flask import abort
from flask import request

#------------------------------------------------------------------------Content Based
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

#------------------------------------------------------------------------Item Based Collaborative Filtering
r_cols = ['user_id','movie_id','rating']
ratings = pd.read_csv('/Users/grey/Documents/Big Data/project/files/ratings_small.csv',
                      sep=',', names=r_cols, usecols=range(3), encoding="utf-8")
# print ratings
l_cols = ['movie_id','tmdb_id']
links_movies = pd.read_csv('/Users/grey/Documents/Big Data/project/files/links_small.csv',
                     sep=',', names=l_cols, usecols=[0,2], encoding="utf-8")

m_cols = ['tmdb_id','title']
movies = pd.read_csv('/Users/grey/Documents/Big Data/project/files/movies_metadata.csv',
                      sep=',', names=m_cols,usecols=[5,20], encoding="utf-8")
# print movies
movies = pd.merge(movies,links_movies)
ratings = pd.merge(movies,ratings)
ratings['user_id'] = ratings['user_id'].astype('int64')
ratings['rating'] = ratings['rating'].astype('float64')

userRatings = ratings.pivot_table(index=['user_id'],columns=['title'],values='rating')
# print (userRatings.head())

corrMatrix = userRatings.corr(method='pearson',min_periods =100)
# print (corrMatrix.head())


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
    if isinstance(moviesName, str) and isinstance(moviesRating, str) and len(moviesRating) != len(moviesName):
         abort(400)
	#TODO send a list of movies and send just one movie or movies that don't exist

    userProfile = []
    for i in range(0,len(moviesName)):
        userProfile.append([moviesName[i],moviesRating[i]])

    # for i in range(0,len(userProfile)):
    #      print(userProfile[i])
    recommendations_content_based = get_recommendation_content_based(userProfile)
    # for i in range(0,len(recommendations_content_based)):
    #     print(recommendations_content_based[i][0] + str(recommendations_content_based[i][1]))
    recommendations_item_based = get_recommendation_CF(userProfile)

    movie_dictionary = dict()
    for i in range(0,len(recommendations_content_based)):
        movie_dictionary[recommendations_content_based[i][0]] = recommendations_content_based[i][1] * 4
    for i in range(0,len(recommendations_item_based.index)):
        if recommendations_item_based.index[i] not in movie_dictionary:
            movie_dictionary[recommendations_item_based.index[i]] = recommendations_item_based[i]
        else:
            movie_dictionary[recommendations_item_based.index[i]] += recommendations_item_based[i]
    # for key,value in movie_dictionary.items():
    #     print(key + "---" + str(value))

    movies = []
    for key,value in sorted(movie_dictionary.items(), key=lambda dictionary: dictionary[1], reverse=True):
        # print(key + "---" + value)
        movies.append(key)

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
    sim_scores = sim_scores[1:15]
    movie_indices = [i[0] for i in sim_scores]
    movies = list(titles.iloc[movie_indices])
    result = []
    for i in range(0, len(sim_scores)):
        result.append([movies[i], sim_scores[i][1]])
        # print(titles.iloc[movie_indices])
    return result



def get_recommendation_content_based(userProfile):
	res = get_recommendations(userProfile)
	# res = list(res)
	recommendMoveis = []
	for i in range(0, len(res)):
		flag = 0
		for j in range(0, len(userProfile)):
			if res[i][0] == userProfile[j][0]:
				flag = 1
		if flag == 0:
			# print(res[i])
			recommendMoveis.append(res[i])
	return recommendMoveis


def get_recommendation_CF(userProfile):
    simCandidates = pd.Series()
    for i in range(0, len(userProfile)):
        # print("Adding sims for " + userProfile[i][0] + "...")
        # Retrieve similar movies to this one that I rated
        sims = corrMatrix[userProfile[i][0]].dropna()
        # print(sims)
        # Now scale its similarity by how well I rated this movie
        sims = sims.map(lambda x: x * userProfile[i][1])
        # Add the score to the list of similarity candidates
        simCandidates = simCandidates.append(sims)

    # print(simCandidates.head(10))

    simCandidates = simCandidates.groupby(simCandidates.index).sum()
    simCandidates.sort_values(inplace=True, ascending=False)
    # print (simCandidates.head(10))

    # '''The last thing we have to do is filter out movies I've already rated,
    # as recommending a movie I've already watched isn't helpful'''
    for i in range(0, len(userProfile)):
        if userProfile[i][0] in simCandidates.index:
            simCandidates = simCandidates.drop(userProfile[i][0])
    # print(simCandidates.head(10))
    return simCandidates.head(10)

if __name__ == '__main__':
    app.run(host= '172.30.63.71')