
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import col,explode,max,desc,countDistinct, monotonically_increasing_id,udf
# import os
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from pyspark.sql.functions import lit
import spacy
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.sql.types import StringType,DoubleType
# import subprocess

# import sys

spark = SparkSession.builder.getOrCreate()









        




if __name__ == "__main__":

    #File Path
    path = "newsarticle/*.csv"

    df1 =  spark.read.options(header=True, inferSchema=True).csv(path)

    embedded_features = df1.select([col(column).cast(DoubleType()) for column in df1.columns[30:]]) #taking the feature embedding
    # embedded_features = embedded_features.na.drop("all")
    vectorizer_assembler = VectorAssembler(inputCols=embedded_features.columns,outputCol="features")
    embedded_vectors = vectorizer_assembler.setHandleInvalid("skip").transform(embedded_features)

    silhouette_score=[]
    evaluator = ClusteringEvaluator(predictionCol='prediction', featuresCol='features', \
                                metricName='silhouette', distanceMeasure='cosine')

    KMeans_algo=KMeans(featuresCol='features', k=10,distanceMeasure="cosine")
    
    KMeans_fit=KMeans_algo.fit(embedded_vectors)

    output=KMeans_fit.transform(embedded_vectors)
    
    score=evaluator.evaluate(output)
    
    predictions = output.select("prediction")

    predictions = predictions.withColumn("id",monotonically_increasing_id())

    df2=df1.select("title","paper","ymd","doc_id")
    df2 = df2.withColumn("id",monotonically_increasing_id())

    final_prediction = predictions.join(df2,"id","inner").drop("id")

    def extract_text(text):

        final_text=[]
        for i in text:
            if i.pos_!="PRON":
                final_text.append(i.text)
        
        return " ".join([i for i in final_text])


    data = "en_core_web_sm"
    nlp = spacy.load(data)

    

    convertUDF = udf(lambda x: extract_text(nlp(str(x))),StringType())
    final_prediction = final_prediction.withColumn("processed_text",convertUDF(col("title"))).coalesce(5) 

    final_prediction.write.option("header",True).mode("overwrite").csv("output/")


   
