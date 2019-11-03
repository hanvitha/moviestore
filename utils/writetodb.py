import traceback, os
import mysql.connector
import pandas as pd
import csv

print("Praise God! ");

__author__ = 'hanvitha'

# DATA_SET = "/opt/app-root/src/dataset"
# POSTURES = "/opt/app-root/src/dataset/MLP-20M"
dataset = os.path.join(os.getcwd(), '..', 'dataset')
postures = os.path.join(dataset, 'MLP-20M')
# host="mysql.registration.svc"
host = "localhost"
port = '3306'
user = "root"
password = "rootpass"
database = "ms"


def writeUsers():
    try:
        db = mysql.connector.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database,
                                     port=port
                                     )
        print("YAYY")
        cursor = db.cursor(buffered=True)
        valuess = ""
        for i in range(1, 672):
            valuess = valuess + "(" + str(i) + ",'pass', 'user" + str(i) + "',  'user" + str(i) + "@gmail.com'),"

        insertquery = "insert into users (id, password, name, email) values {};".format(valuess[:-1])
        print(insertquery)
        cursor.execute(insertquery)
        db.commit()
        print("Done ")
        # print(allusers)

    except Exception as e:
        print(traceback.print_exc())
    finally:
        db.close()
        cursor.close()


def writeRatings():
    try:
        db = mysql.connector.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database,
                                     port=port
                                     )
        print("YAYY")
        cursor = db.cursor(buffered=True)
        # valuess = ""
        with open('/Users/hgavini/Documents/Redhat/workspaces/pycharm/moviestore/dataset/ratings_small.csv',
                  mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                valuess = f"({line_count}, {row['userId']}, {row['movieId']}, {row['rating']})"
                insertquery = "insert into ratings (id, userid, movieid, rating) values {};".format(valuess)
                print(insertquery)
                cursor.execute(insertquery)
                line_count += 1

            print(f'Processed {line_count} lines.')

        db.commit()
        print("Done ")


    except Exception as e:
        print(traceback.print_exc())
    finally:
        db.close()
        cursor.close()


# metadata
# adult,belongs_to_collection,budget,genres,homepage,id,imdb_id,original_language,original_title,overview,popularity,poster_path,production_companies,production_countries,release_date,revenue,runtime,spoken_languages,status,tagline,title,video,vote_average,vote_count
def writeMovies():
    try:
        db = mysql.connector.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database,
                                     port=port
                                     )
        print("YAYY")
        cursor = db.cursor(buffered=True)
        # valuess = ""
        # md = pd.read_csv('dataset/movies_metadata.csv')
        metadatapath = os.path.join(dataset, "movies_metadata.csv")
        moviespath = os.path.join(dataset, "movies.csv")
        line_count = 0
        mvs_df = pd.read_csv(moviespath)


        with open(metadatapath, 'r') as metafile:
            meta_csv_reader = csv.DictReader(metafile)
            l = 0
            for meta_row in meta_csv_reader:
                valuess = ""
                line_count += 1
                meta_row_moviename = meta_row['title'].lower()
                for mv in mvs_df.itertuples():
                    try:
                        movie_row_moviename = mv.title[:-6].strip().lower()
                        if (meta_row_moviename.startswith('the ') or meta_row_moviename.startswith(
                                'les ') or meta_row_moviename.startswith('la ') or meta_row_moviename.startswith(
                            'a ') or meta_row_moviename.startswith('an ') or meta_row_moviename.startswith('le ')):
                            meta_row_moviename = meta_row_moviename[meta_row_moviename.find(" "):]
                            # print("Meta Data name "+meta_row_moviename)
                        if movie_row_moviename.startswith(meta_row_moviename) or movie_row_moviename.startswith(meta_row['original_title'].lower()):
                            movieId = mv.movieId
                            title = meta_row['title']
                            releasedate = meta_row['release_date']

                            # print("Overview:::  " + meta_row['overview'])
                            overview = meta_row['overview'].replace('"', '').replace("'", " ").replace(",", " ").replace(")"," ").replace("(", " ")
                            vote_count = meta_row['vote_count']
                            vote_average = meta_row['vote_average']

                            if not title:
                                title = " "
                            posture = postures + "/" + str(movieId) + ".jpg"
                            if (not os.path.exists(posture)):
                                print("Posture not found" + "   " + title)
                                break
                            # if(row['title']!=None):
                            #     title=row['title'].strip()[:-6].strip().replace("\"", "")
                            # year = row['title'].strip()[-6:].replace("(","").replace(")","")
                            # if not year:
                            #     year = '2000'
                            valuess = f"(\"{movieId}\", \"{title}\",\"{releasedate}\",{meta_row['adult']}, \"{overview}\",{vote_count},{vote_average})"
                            # print(valuess)
                            insertquery = "insert into movies (id, title, releasedate,adult, overview, vote_count, vote_avg) values {};".format(
                                valuess)

                            # print("Insert Query : " + insertquery)


                            cursor.execute(insertquery)
                            line_count +=1
                            if(line_count>10):
                                db.commit()
                                cursor = db.cursor(buffered=True)
                            # print("Done  " + meta_row_moviename + "  :   " + movie_row_moviename)
                            # break coz you already found the movie
                            break

                    except Exception as e:
                        # print(traceback.print_exc())
                        # print(valuess)
                        break

    except Exception as e:
        print(traceback.print_exc())

    finally:
        db.close()
        cursor.close()


def writeGenres():
    try:
        db = mysql.connector.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database,
                                     port=port
                                     )
        print("YAYY")
        cursor = db.cursor(buffered=True)
        genres = {1: "Action", 2: "Adventure", 3: "Animation", 4: "Children's", 5: "Comedy", 6: "Crime",
                  7: "Documentary", 8: "Drama", 9: "Fantasy", 10: "Film-Noir", 11: "Horror", 12: "Musical",
                  13: "Mystery", 14: "Romance", 15: "Sci-Fi", 16: "Thriller", 17: "War", 18: "Western",
                  19: "(no genres listed)"}
        try:
            for gid, gname in genres.items():
                query = '''insert into genres (id, name) values ( %s, %s);'''
                print(query, (gid, gname))
                cursor.execute(query, (gid, gname))
            db.commit()
        except Exception as e:
            print(traceback.print_exc())
        print("Done ")


    except Exception as e:
        print(traceback.print_exc())
    finally:
        db.close()
        cursor.close()


def writeMovieGenres():
    try:
        db = mysql.connector.connect(host=host,
                                     user=user,
                                     password=password,
                                     database=database,
                                     port=port
                                     )
        print("YAYY")
        cursor = db.cursor(buffered=True)
        genres = {"Action": 1, "Adventure": 2, "Animation": 3, "Children": 4, "Comedy": 5, "Crime": 6, "Documentary": 7,
                  "Drama": 8, "Fantasy": 9, "Film-Noir": 10, "Horror": 11, "Musical": 12, "Mystery": 13, "Romance": 14,
                  "Sci-Fi": 15, "Thriller": 16, "War": 17, "Western": 18, "(no genres listed)": 19}

        # valuess = ""
        with open('/Users/hgavini/Documents/Redhat/workspaces/pycharm/moviestore/dataset/movies.csv',
                  mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                try:
                    if line_count == 0:
                        print(f'Column names are {", ".join(row)}')

                    genrenames = row['genres']
                    genreid = 19
                    if genrenames:
                        allgenres = genrenames.strip().split("|")

                        for g in allgenres:
                            genreid = genres.get(g)
                            insertquery = '''insert into movie_genres (id, movieid, genreid) values ( default, %s, %s);'''
                            # print(insertquery, genreid, g)
                            cursor.execute(insertquery, (row['movieId'], genreid))

                    else:
                        insertquery = '''insert into movie_genres (id, movieid, genreid) values ( default, %s, %s);'''
                        print(insertquery)
                        cursor.execute(insertquery, (row['movieId'], genreid))
                    if (line_count % 10000 == 0):
                        db.commit()
                        cursor = db.cursor(buffered=True)
                    line_count += 1

                except Exception as e:
                    print(traceback.print_exc())
                    print(insertquery)
            print(f'Processed {line_count} lines.')
        db.commit()

        print("Done ")


    except Exception as e:
        print(traceback.print_exc())
    finally:
        db.close()
        cursor.close()


# writeUsers()
# writeRatings()
writeMovies()
# writeGenres()
# writeMovieGenres()
