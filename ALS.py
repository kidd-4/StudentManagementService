from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.recommendation import ALS
from pyspark.sql import Row, SparkSession
import sys
import csv

spark = SparkSession \
    .builder \
    .appName("ALS") \
    .getOrCreate()
# "/Users/grey/Desktop/sample_movielens_ratings.txt"
sc = spark.sparkContext

lines = sc.textFile("/Users/grey/Documents/Big Data/project/files/ratings_small.csv")
linesRdd = lines.mapPartitions(lambda x: csv.reader(x))
ratingheader = linesRdd.first()
linesRdd = linesRdd.filter(lambda x: x != ratingheader)
# parts = lines.map(lambda row: row.value.split("::"))
ratingsRDD = linesRdd.map(lambda p: Row(userId=int(p[0]), movieId=int(p[1]),
                                     rating=float(p[2])))
ratings = spark.createDataFrame(ratingsRDD)
(training, test) = ratings.randomSplit([0.8, 0.2],int(sys.argv[1]))

# Build the recommendation model using ALS on the training data
# Note we set cold start strategy to 'drop' to ensure we don't get NaN evaluation metrics
als = ALS(maxIter=5, regParam=0.01, userCol="userId", itemCol="movieId", ratingCol="rating",
          coldStartStrategy="drop",rank=70)
als.setSeed(int(sys.argv[1]))
# Fits a model to the input dataset with optional parameters.
# Returns:	fitted model(s)
model = als.fit(training)

# # Evaluate the model by computing the RMSE on the test data
# # transform()    Transforms the input dataset with optional parameters.
# predictions = model.transform(test)
# # Evaluator for Regression, which expects two input columns: prediction and label.
# evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating",
#                                 predictionCol="prediction")
# # evaluate()  Returns: metric
# rmse = evaluator.evaluate(predictions)
# print(str(rmse))

# Generate top 10 movie recommendations for each user
userRecs = model.recommendForAllUsers(10)
userRecs.show(truncate=False)
# Generate top 10 user recommendations for each movie
# movieRecs = model.recommendForAllItems(10)
