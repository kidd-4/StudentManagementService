import pandas as pd

r_cols = ['user_id','movie_id','rating']
ratings = pd.read_csv('/Users/grey/Documents/Big Data/project/files/ratings_small.csv',
                      sep=',', names=r_cols, usecols=range(3), encoding="utf-8")
# print ratings
l_cols = ['movie_id','tmdb_id']
links = pd.read_csv('/Users/grey/Documents/Big Data/project/files/links_small.csv',
                     sep=',', names=l_cols, usecols=[0,2], encoding="utf-8")

m_cols = ['tmdb_id','title']
movies = pd.read_csv('/Users/grey/Documents/Big Data/project/files/movies_metadata.csv',
                      sep=',', names=m_cols,usecols=[5,20], encoding="utf-8")
# print movies
movies = pd.merge(movies,links)
ratings = pd.merge(movies,ratings)
ratings['user_id'] = ratings['user_id'].astype('int64')
ratings['rating'] = ratings['rating'].astype('float64')
# ratings['title'] = ratings['title'].astype('object')
# ratings = ratings.drop_duplicates(['title'])
# print(ratings['title'][0])
# print(type(ratings['title']))
# print(type("Toy Story"))
# if "Harry Potter and the Chamber of Secrets" in ratings['title'].values:
#     print ("-----------")
# else:
#     print("Nothing exists")
# print(ratings)

userRatings = ratings.pivot_table(index=['user_id'],columns=['title'],values='rating')
# print (userRatings.head())

corrMatrix = userRatings.corr(method='pearson',min_periods =100)
# print (corrMatrix.head())


'''let's produce some movie recommendations for user ID 0, who I manually added to the data set as a test case.'''
# myRatings = userRatings.loc[1].dropna()
# print (myRatings)
userProfile = [['Toy Story', 4.0], ['Spider-Man', 3.0], ["Harry Potter and the Deathly Hallows: Part 1", 5.0]]
# myRatings = pd.Series(userProfile)
# print(myRatings.index)
# print(myRatings[0])

simCandidates = pd.Series()
for i in range(0,len(userProfile)):
    print ("Adding sims for " + userProfile[i][0] + "...")
    # Retrieve similar movies to this one that I rated
    sims = corrMatrix[userProfile[i][0]].dropna()
    # print(sims)
    # Now scale its similarity by how well I rated this movie
    sims = sims.map(lambda x: x*userProfile[i][1])
    # Add the score to the list of similarity candidates
    simCandidates = simCandidates.append(sims)

# print ("sorting...")

# print(simCandidates.head(10))

simCandidates = simCandidates.groupby(simCandidates.index).sum()
simCandidates.sort_values(inplace=True, ascending=False)
# print (simCandidates.head(10))

# '''The last thing we have to do is filter out movies I've already rated,
# as recommending a movie I've already watched isn't helpful'''
for i in range(0,len(userProfile)):
    if userProfile[i][0] in simCandidates.index:
        simCandidates = simCandidates.drop(userProfile[i][0])
print (simCandidates.head(10))
