import numpy as np

from config import Config
from model_utils import dummy_tokenizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import FeatureUnion, Pipeline

class ItemSelector(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]

class Reshape(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self

    def transform(self, data):
        data = np.array(data)
        assert len(data.shape) == 1
        return data.reshape((-1, 1))

class SklearnModel(object):
    def __init__(self, name, pipe, params_range):
        self.name = name
        self.pipe = pipe
        self.params_range = params_range

def text_pipe(clf):
    return Pipeline([
             ('select', ItemSelector(key="question")),
             ('vect', CountVectorizer(tokenizer=dummy_tokenizer, lowercase=False)),
             ('tfidf', TfidfTransformer()),
             ('clf', clf)
             ])

def text_and_scalar_pipe(scalar, clf):
    return Pipeline([
        ('union', FeatureUnion(
            transformer_list=[
                ('text', Pipeline([
                    ('select', ItemSelector(key="question")),
                    ('vect', CountVectorizer(tokenizer=dummy_tokenizer, lowercase=False)),
                    ('tfidf', TfidfTransformer()),
                    ])),
                ('scalar', Pipeline([
                    ('select', ItemSelector(key=scalar)),
                    ('reshape', Reshape()),
                    ]))
                ]
            )),
        ('clf', clf)
        ])

log_params = {'clf__C': np.logspace(-4, 4, 100), 'clf__penalty': ['l2', 'l1']}
svm_params = {'clf__C': np.logspace(-4,4,100), 'clf__loss': ['hinge', 'squared_hinge']}

Logistic = SklearnModel("logistic", text_pipe(LogisticRegression(class_weight='balanced', random_state=Config.SEED)), log_params)
SVM = SklearnModel("svm", text_pipe(LinearSVC(class_weight='balanced', random_state=Config.SEED)), svm_params)
Dummy = SklearnModel("dummy", text_pipe(DummyClassifier(random_state=Config.SEED)), {})

LogisticWithScalar = lambda s: SklearnModel("logistic", text_and_scalar_pipe(s, LogisticRegression(class_weight='balanced', random_state=Config.SEED)), log_params)
SVMWithScalar = lambda s: SklearnModel("logistic", text_and_scalar_pipe(s, LinearSVC(class_weight='balanced', random_state=Config.SEED)), svm_params)