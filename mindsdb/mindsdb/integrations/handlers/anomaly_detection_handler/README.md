# Anomaly Detection Handler
The Anomaly Detection handler implements supervised, semi-supervised, and unsupervised anomaly detection algorithms using the pyod, catboost, xgboost, and sklearn libraries. The models were chosen based on the results in the following benchmark paper:
https://www.andrew.cmu.edu/user/yuezhao2/papers/22-neurips-adbench.pdf 

# Additional information

- If no labelled data, we use an unsupervised learner with the syntax `CREATE ANOMALY DETECTION MODEL <model_name>` without specifying the target to predict. MindsDB then adds a column called `outlier` when generating results.

- If we have labelled data, we use the regular model creation syntax. There is backend logic that chooses between a semi-supervised algorithm (currently XGBOD) vs. a supervised algorithm (currently CatBoost).

- If multiple models are provided, then we create an ensemble and take use majority voting

- See the anomaly detection proposal document for more information - https://docs.google.com/document/d/1Yd7ARZVg_67xlcY-JR2kuO7mak9Ia2YER1Jk0EdpEa0/edit#heading=h.mo4wxsae6t1d


# Example usage
To run example queries, use the CSV in `tests/unit/ml_handlers/anomaly_detection.csv`

### Unsupervised detection

```
CREATE ANOMALY DETECTION MODEL mindsdb.unsupervised_ad
FROM files
    (SELECT * FROM anomaly_detection)
USING 
    engine = 'anomaly_detection';

DESCRIBE MODEL mindsdb.unsupervised_ad.model;

SELECT t.class, m.outlier as anomaly
FROM files.anomaly_detection as t
JOIN mindsdb.unsupervised_ad as m;
```

### Semi-supervised detection

```
CREATE MODEL mindsdb.semi_supervised_ad
FROM files
    (SELECT * FROM anomaly_detection)
PREDICT class
USING
    engine = 'anomaly_detection';

DESCRIBE MODEL mindsdb.semi_supervised_ad.model;

SELECT t.carat, t.category, t.class, m.class as anomaly
FROM files.anomaly_detection as t
JOIN mindsdb.semi_supervised_ad as m;
```

### Supervised detection

```
CREATE MODEL mindsdb.supervised_ad
FROM files
    (SELECT * FROM anomaly_detection)
PREDICT class
USING
    engine = 'anomaly_detection', type = 'supervised';

DESCRIBE MODEL mindsdb.supervised_ad.model;

SELECT t.carat, t.category, t.class, m.class as anomaly
FROM files.anomaly_detection as t
JOIN mindsdb.supervised_ad as m;
```

### Specific model
```
CREATE ANOMALY DETECTION MODEL mindsdb.unsupervised_ad_knn
FROM files
    (SELECT * FROM anomaly_detection)
USING 
    engine = 'anomaly_detection',
    model_name='knn';

DESCRIBE MODEL mindsdb.unsupervised_ad_knn.model;

SELECT t.class, m.outlier as anomaly
FROM files.anomaly_detection as t
JOIN mindsdb.unsupervised_ad_knn as m;
```

### Specific anomaly type
```
CREATE ANOMALY DETECTION MODEL mindsdb.unsupervised_ad_local
FROM files
    (SELECT * FROM anomaly_detection)
USING 
    engine = 'anomaly_detection',
    anomaly_type='local';

DESCRIBE MODEL mindsdb.unsupervised_ad_local.model;

SELECT t.class, m.outlier as anomaly
FROM files.anomaly_detection as t
JOIN mindsdb.unsupervised_ad_local as m;
```

### Ensemble
```
create ANOMALY DETECTION MODEL mindsdb.ad_ensemble
FROM files
    (SELECT * FROM anomaly_detection)
USING 
    engine='anomaly_detection',
    ensemble_models=['knn','ecod','lof'];

DESCRIBE MODEL mindsdb.ad_ensemble.model;

SELECT t.class, m.outlier as anomaly
FROM files.anomaly_detection as t
JOIN mindsdb.ad_ensemble as m;
```


# Additional Media:

### Demo 1:
https://www.loom.com/share/0996e5faa3f7415bacd51a6e8e161d5e?sid=9bacd29a-975b-4a94-b081-de2255b93607

### Demo 2:
https://www.loom.com/share/c22335d83cb04ac281e2ef080792f2dd


