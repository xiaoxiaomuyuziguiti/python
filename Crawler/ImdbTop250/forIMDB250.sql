#影片排名-评分
SELECT a.* FROM t_movie a order by a.rating desc;
#上榜导演排名-上榜影片数量
select count(*) nums,director_name from t_director b group by b.director_name order by nums desc;
#上榜导演排名-上榜影片数量-基于评分加权
select t.director_name,sum(t.rating) total_rating from
(select a.*,b.* from t_director a inner join t_movie b on a.movie_id=b.id) as t 
group by t.director_name order by sum(t.rating) desc;
#上榜国家排名-上榜影片数量
select count(*) nums,country from t_country group by country order by nums desc;
#上榜类型排名-电影归属类型
select count(*) nums,genres from t_genres group by genres order by nums desc;
#上榜演员排名-上榜影片数量
select count(*) nums,actor_name from t_actor group by actor_name order by nums desc;
#按照评分人数排名
select * from t_movie order by rating_people_nums desc;
#按照年份排名
select count(*) nums,year from t_movie group by year order by nums desc;
#按照时长排名
select * from t_movie order by runtime desc;



select count(*) count,year from t_movie_info group by year order by count desc;

select * from t_movie_info where country like '%USA%';

show create table t_movie_info;