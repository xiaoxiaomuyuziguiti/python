import requests
import re
from html.parser import HTMLParser
import mysql.connector
import json
import traceback


# 定义解析主页面【https://www.imdb.com/chart/top?ref_=nv_mv_250】的触发器
class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.movieflag = 0
        self.yearflag = 0
        self.movies = []
        self.movie = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'td' and attrs and attrs[0][1] == 'posterColumn':
            self.movieflag = 1
        if self.movieflag == 1 and tag == 'span':
            # 获取到电影评分值
            if attrs[0][1] == 'ir':
                self.movie['rating'] = attrs[1][1]
            # 获取到参与电影评分的人数
            elif attrs[0][1] == 'nv':
                self.movie['rating_people_nums'] = attrs[1][1]
            # 获取到电影的imdb总排名
            elif attrs[0][1] == 'rk':
                self.movie['rank'] = attrs[1][1]
        if self.movieflag == 1 and tag == 'a' and len(attrs) == 2:
            self.movie['url'] = attrs[0][1]

    def handle_endtag(self, tag):
        if tag == 'tr' and self.movieflag == 1 :
            self.movies.append(self.movie)
            self.movie = {}
            self.movieflag = 0

    def handle_data(self, data):
        # 获取到电影名字
        if self.lasttag == 'a' and self.movieflag == 1 and re.search(r'\w+', data):
            self.movie['nameEn'] = data


# 定义解析每部电影的分页面的触发器
class MovieDetailHTMLParser(HTMLParser):
    def __init__(self):
        self.json_flag = 0
        self.country_flag = 0
        self.movie_detail = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'script' and attrs and attrs[0] == ('type', 'application/ld+json'):
            self.json_flag = 1
        if tag == 'a' and attrs and re.match(r'/search/title\?country_of_origin=', attrs[0][1]):
            self.country_flag = 1

    def handle_endtag(self, tag):
        if tag == 'a' and self.country_flag == 1:
            self.country_flag = 0
        if tag == 'script' and self.json_flag == 1:
            self.json_flag = 0

    def handle_data(self, data):
        # 获取到电影所属国家
        if self.country_flag == 1:
            if data == 'Hong Kong' or data == 'Taiwan':
                self.movie_detail['country'] = 'China'
            else:
                self.movie_detail['country'] = data
        # 获取其他详细信息
        if self.json_flag == 1:
            # 对获取到的数据进行json反序列化
            data_json = json.loads(data)
            # 获取电影类别信息
            self.movie_detail['genres'] = data_json['genre'] if isinstance(data_json['genre'], str) else '#'.join(data_json['genre'])
            # 获取演员信息
            people_actor = []
            for people in data_json['actor']:
                people_actor.append(people['name'])
            self.movie_detail['allstar'] = '#'.join(people_actor)
            # 获取导演信息
            if isinstance(data_json['director'], list):
                people_director = []
                for people in data_json['director']:
                    people_director.append(people['name'])
                self.movie_detail['director'] = '#'.join(people_director)
            else:
                self.movie_detail['director'] = data_json['director']['name']
            # 获取电影上映年份
            self.movie_detail['year'] = re.match(r'^(\d+)-', data_json['datePublished']).group(1)
            # 获取电影简要描述
            self.movie_detail['description'] = data_json['description']
            # 获取电影时长，以分钟作为单位
            matches = re.match(r'\w\w(\d*)H?(\d*)M?', data_json['duration'])
            if matches.group(1) != '' and matches.group(2) != '':
                self.movie_detail['runtime'] = int(matches.group(1))*60+int(matches.group(2))
            elif matches.group(1) != '' and matches.group(2) == '':
                self.movie_detail['runtime'] = int(matches.group(1)) * 60
            elif matches.group(1) == '' and matches.group(2) != '':
                self.movie_detail['runtime'] = int(matches.group(2))
            else:
                self.movie_detail['runtime'] = 0
            # 获取电影的第一条评论
            self.movie_detail['first_review'] = data_json['review']['reviewBody']


# 获取主页面html并调用触发器解析，返回包含250个电影基本信息的列表
def get_top250_movies_list():
    url = 'https://www.imdb.com/chart/top?ref_=nv_mv_250'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
    # response = requests.get(url)
        if response.status_code == 200:
            print('Get Top250 mainpage success!!')
            parser = MyHTMLParser()
            parser.feed(response.text)
            return parser.movies
        else:
            print('Response status is not OK!')
            raise Exception
    except Exception as e:
        traceback.print_exc()


# 基于获取到的电影基本信息，通过单个电影的详情页获取更详细的信息，以字典形式返回
def get_movie_detail(movie):
    url = 'https://www.imdb.com' + movie['url']
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (K'
                                                            'HTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
    # response = requests.get(url)
        if response.status_code == 200:
            print('Rank.', movie['rank'], '【', movie['nameEn'], '】', 'detail page get success!!')
            parser = MovieDetailHTMLParser()
            parser.feed(response.text)
            # 将获取到的详细信息和入参movie的基本信息合并到同一个dict
            for key, value in parser.movie_detail.items():
                movie[key] = value
            return movie
        else:
            print('Response status is not OK!')
            raise Exception
    except Exception as e:
        traceback.print_exc()


# 将单部电影的详细信息计入数据库
def write_movie(movie):
    try:
        # 连接数据库
        conn = mysql.connector.connect(user='root', password='XXY@mima123', database='testbyxxy')
        cursor = conn.cursor()
        # 查询相同排名的数据是否已存在，若已存在先删除后插入，若不存在直接插入
        cursor.execute('select count(*) from t_movie_info where ranking = %s', [movie['rank']])
        values = cursor.fetchall()
        if values == 0 :
            cursor.execute('insert into t_movie_info (name_en,genres,rating,allstar,rating_people_nums,year,country,director,runtime,first_review,ranking,description) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            [movie['nameEn'], movie['genres'], movie['rating'], movie['allstar'], int(movie['rating_people_nums']), movie['year'], movie['country'], movie['director'], movie['runtime'], movie['first_review'], movie['rank'], movie['description']])
        else:
            cursor.execute('delete from t_movie_info where ranking =%s',[movie['rank']])
            cursor.execute('insert into t_movie_info (name_en,genres,rating,allstar,rating_people_nums,year,country,director,runtime,first_review,ranking,description) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            [movie['nameEn'], movie['genres'], movie['rating'], movie['allstar'], int(movie['rating_people_nums']), movie['year'], movie['country'], movie['director'], movie['runtime'], movie['first_review'], movie['rank'], movie['description']])
        conn.commit()
    except Exception as e:
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


# 获取电影基本信息列表
movies = get_top250_movies_list()
# 遍历每一部电影，抓取详细信息并计入数据库
for movie in movies:
    movie_detail = get_movie_detail(movie)
    write_movie(movie_detail)

# movie = movies[71]
# movie_detail = get_movie_detail(movie)
# write_movie(movie_detail)
#
# movie1 = movies[149]
# movie_detail1 = get_movie_detail(movie1)
# write_movie(movie_detail1)
#
# movie2 = movies[236]
# movie_detail2 = get_movie_detail(movie2)
# write_movie(movie_detail2)
