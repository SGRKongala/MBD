
from pyspark.sql import SparkSession
import pyspark.sql.functions as f

from pyspark.sql.functions import col,count,explode,max,desc,countDistinct, monotonically_increasing_id,udf,collect_list,array,when
# import os
from pyspark.sql.functions import concat_ws
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.clustering import LDA

from pyspark.sql.functions import lit
from pyspark.ml.feature import HashingTF, IDF, Tokenizer
from pyspark.ml.feature import NGram
from pyspark.sql.types import StringType
from pyspark.sql.functions import regexp_replace

spark = SparkSession.builder.getOrCreate()


if __name__ == "__main__":
    word_search="""murder|accidents|shootings|shot|mass shootings|crime reported|man shot|woman shot|man dies|woman dies|woman killed|man killed"""

    path = "newsarticle/plain_dealer_cleveland_data.csv"
    df1 =  spark.read.options(header=True, inferSchema=True).option("multiline",'true').csv(path)
    df1 = df1.select("title","paper",col("ymd").substr(0,4).alias("year"))
    
 
    text_df = df1.withColumn("processed_text", regexp_replace("title", "[^a-zA-Z_\-]+", " "))
    
    text_df = text_df.filter(col("processed_text").rlike(word_search))
    text_df = text_df.withColumn("id",monotonically_increasing_id())
    
    dropNa = text_df.na.drop("any")

    tokenizer = Tokenizer(inputCol="processed_text", outputCol="words")
    wordsData = tokenizer.transform(dropNa.select("processed_text"))


    ngram = NGram(n=2,inputCol="words",outputCol="words_ngram")

    wordsData = ngram.transform(wordsData)
    wordsData = wordsData.withColumn("id",monotonically_increasing_id())
    wordsData = wordsData.select("id","words_ngram")

    temp_df = text_df.select("id","year","title")
    final_df = temp_df.join(wordsData,"id","inner")

    

    word_count = final_df.select("year",explode("words_ngram").alias("flatten_words")).\
                                        groupBy("year","flatten_words").agg(count("flatten_words").alias("count")).\
                                        sort(col("count").desc())
    

    words_interest = ["man killed","woman killed","man dead","woman dead"]
    get_man_killed = word_count.filter(word_count.flatten_words.isin(words_interest))
    get_man_killed.show()
    # word_count = wordsData.select(explode("words_ngram").alias("words")).\
    #                             groupBy("words").count().sort(col("count").desc())

 
    # wordsInterest = "man dies|woman dies|woman killed|man killed"
    # getMassShooting = word_count.filter(col("words").rlike(wordsInterest))
    
    # word_count.show(100)

