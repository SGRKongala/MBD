path="/user/s2765918/newsarticle/combined_data_slim.csv"
df =spark.read.options(header=True, inferSchema=True).option("multiline",'true').csv(path)
df1 = df.select(lower(col("title")), year("date").alias("year"))
text_df = df1.withColumn("processed_text", regexp_replace("title", "[^a-zA-Z_\-]+", " "))
text_df=text_df.select(col("year"), lower(col("processed_text")))
df2=text_df.select(split(col("processed_text"), "\s+").alias("words"), col("year"))
df3=df2.select(df2.year, explode(lower(df2.words)).alias("words"))
df4=df4.select(df4.year, lower(df4.words).alias("word"))
df5=df4.groupBy(df4.word).pivot("year").agg(count("word"))
df6=df5.fillna(0)
df7=df6.withColumn("total", sum(df6[col] for col in df6.columns[1:]))
df7=df7.sort(df7.total.desc())
from pyspark.ml.feature import StopWordsRemover
stopwordList = ["word1","word2","word3"]
stopwordList.extend(StopWordsRemover().getStopWords())
df8=df7.filter(~df7.word.isin(stopwordList))
df8.repartition(1).write.options(header='True').csv("word")