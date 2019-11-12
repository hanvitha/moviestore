
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
import warnings; warnings.simplefilter('ignore')
import random
import traceback


def weighted_rating(row, m, C):
    vtct = row['vote_count']
    avg = row['vote_avg']
    # Calculation based on the IMDB formula
    return (vtct / (vtct + m) * avg) + (m / (m + vtct) * C)

class Recommendation:

    def __init__(self, db):
        self.titles = pd.DataFrame()
        self.indices = pd.DataFrame()
        self.cosine_sim = None
        self.db = db
        self.prepareContentBasedRecomm()
        self.md = pd.DataFrame()

    def prepareContentBasedRecomm(self):
        try:
            # md = pd.read_csv('data/movies_metadata.csv')
            query = "select * from movies limit 5000;"
            self.md = pd.read_sql(query, self.db)
            print(self.md.shape)
            self.md['overview'] = self.md['overview'].fillna('')
            tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
            tfidf_matrix = tf.fit_transform(self.md['overview'])
            tfidf_matrix.shape
            self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
            print(self.cosine_sim[0])
            # md = md.reset_index()
            print(self.md.head(5))
            # md.set_index('id')
            print(self.md.head(5))
            self.titles = self.md['title']
            self.indices = pd.Series(self.md.index, index=self.md['title'])
            print(self.indices.head(5))
        except Exception as e:
            print("DB emoty")
            return pd.DataFrame()

    def getContentBasedRecomm(self, title):
        try:
            print("In get content based recomm" + title)
            idx = self.indices[title]
            sim_scores = list(enumerate(self.cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:31]
            indices = [i[0] for i in sim_scores]
            recommendedMovies = self.md.iloc[indices]
            recommendedMovies = recommendedMovies[['id', 'title']]
            print(recommendedMovies.head(5))
            # recommendedMovies = recommendedMovies.join(self.md, )
            return recommendedMovies
        except Exception as e:
            traceback.print_exc()
            return pd.DataFrame()

    # Simple Recommendation
    def getTrendingRecommendations(self):
        try:
            # md = 155514
            # pd.read_csv('data/movies_metadata.csv')
            # query = "select * from movies;"
            # md = pd.read_sql(query, self.db)
            # md.head()
            print("GEtting trending recomm")
            vote_counts = self.md[self.md['vote_count'].notnull()]['vote_count'].astype('int')
            vote_avgs = self.md[self.md['vote_avg'].notnull()]['vote_avg'].astype('int')
            C = vote_avgs.mean()
            random_quantile = random.randint(79, 99) / 100
            print(random_quantile)
            m = vote_counts.quantile(random_quantile)
            qualified = \
            self.md[(self.md['vote_count'] >= m) & (self.md['vote_count'].notnull()) & (self.md['vote_avg'].notnull())][
                ['id', 'title', 'releasedate', 'vote_count', 'vote_avg']]
            qualified['vote_count'] = qualified['vote_count'].astype('int')
            qualified['vote_avg'] = qualified['vote_avg'].astype('int')
            qualified.shape
            qualified['wr'] = qualified.apply(weighted_rating, args=(m, C), axis=1)
            qualified = qualified.sort_values('wr', ascending=False).head(250)
            trending = qualified.head(20)
            trending = trending.values.tolist()
            # print(md.head())
            return trending
        except Exception as e:
            traceback.print_exc()
            return pd.DataFrame()

    def getMoviesByGenre(self, genreid, cursor):
        try:
            cursor.execute(f"select movieid from  movie_genres where genreid='{genreid}' limit 30;")
            movieids = cursor.fetchall()
            # print(movieids)
            allmovieids = list()
            for (i,) in movieids:
                allmovieids.append(i)
            allmovieids = tuple(allmovieids)
            # print(allmovieids)
            moviesquery = f"select id, title from  movies where id in {allmovieids} ORDER BY  vote_avg DESC limit 30;"
            df = pd.read_sql(moviesquery, self.db)
            return df.values.tolist()
        except Exception as e:
            traceback.print_exc()
            return pd.DataFrame()