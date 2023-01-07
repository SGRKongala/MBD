from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
sc = SparkContext()
spark = SparkSession(sc)
from pyspark.sql.functions import col, udf
from pyspark.sql.types import *
from pyspark.sql.functions import year, mean
from pyspark.sql.functions import asc, col
import subprocess
import pyspark
from pyspark.sql import SparkSession
from itertools import count
from datetime import datetime


def influenceAvg(path):
	if path == '/user/s2765918/newsarticle/combined_data_slim.csv':
		return 1
	else:
		df_inf=spark.read.options(delimiter=",", header=True).csv(path)
		df_inf1=df_inf.groupBy(year("date")).agg(mean("max_inf")).sort(asc("year(date)"))
		df_inf2=df_inf1.filter(col('year(date)').between(2010,2019))
		name = path[27:-4]
		df_inf3=df_inf2.select(col('year(date)').alias('year'), col('avg(max_inf)').alias(name))
		return df_inf3

df_list = []
p = subprocess.Popen("hdfs dfs -ls /user/s2765918/newsarticle/*.csv |  awk '{print $8}'",
     shell=True,
     stdout=subprocess.PIPE,
     stderr=subprocess.STDOUT)
for line in p.stdout.readlines():
	if influenceAvg(line.strip()) != None:
		df_list.append(influenceAvg(line.strip()))
l1=df_list[0:24]
l2=df_list[25:49]
result1 = reduce(lambda first, second: first.join(second, on='year', how='outer'), l1)
result1.show()
result1.coalesce(1).write.options(header='True').csv("inf1/")
result2 = reduce(lambda first, second: first.join(second, on='year', how='outer'), l2)
result2.coalesce(1).write.options(header='True').csv("inf2/")
result = result1.join(result2, on='year')
result.coalesce(1).write.options(header='True').csv("inf/")
