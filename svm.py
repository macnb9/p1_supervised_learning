import numpy as np

from sklearn.decomposition import PCA
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC, NuSVC, SVC

from analysis import analyze_clf
from datareader import load_preprocessor, load_study
from trainer import generate_credit_card_study, generate_heart_study, RANDOM_STATE


def objective(trial, x, y, scoring=None):
    params = {
        "clf_type" : "svc"  # trial.suggest_categorical("clf_type", ["svc", "linear"]),
    }

    if params["clf_type"] == "svc":
        params.update({
            "c"        : trial.suggest_float("c", 1e1, 1e2),
            "kernel"   : trial.suggest_categorical("kernel", ["poly", "rbf", "sigmoid"]),
            "gamma"    : trial.suggest_float("gamma", 1e-4, 1e-3),
            "degree"   : trial.suggest_int("degree", 1, 3),
            "coef0"    : trial.suggest_float("coef0", 0, 4),
            "shrinking": trial.suggest_categorical("shrinking", [False, True])
        })

    elif params["clf_type"] == "nu":
        params.update({
            "nu"       : trial.suggest_float("nu", 1e-10, 0.8),
            "kernel"   : trial.suggest_categorical("kernel", ["poly", "rbf", "sigmoid"]),
            "degree"   : trial.suggest_int("degree", 1, 3),
            "coef0"    : trial.suggest_float("coef0", 0, 4),
            "shrinking": trial.suggest_categorical("shrinking", [False, True])
        })

    elif params["clf_type"] == "linear":
        params.update({
            "c": trial.suggest_float("c", 1e-10, 1e2, log=True),
        })

    clf = load_svm_model(params)

    score = cross_val_score(clf,
                            x,
                            y,
                            n_jobs=-1,
                            cv=5,
                            scoring=scoring)
    return score.mean()


def load_svm_model(params):
    # if params["clf_type"] == "svc":
    return load_svc_model(params)
    # elif params["clf_type"] == "nu":
    #     return load_nu_svc_model(params)
    # elif params["clf_type"] == "linear":
    #     return load_linear_svc_model(params)


def load_svc_model(params):
    return SVC(C=params["c"],
               kernel=params["kernel"],
               gamma=params["gamma"],
               degree=params["degree"],
               coef0=params["coef0"],
               shrinking=params["shrinking"],
               probability=True,
               class_weight="balanced",
               random_state=RANDOM_STATE)


def load_nu_svc_model(params):
    return NuSVC(nu=params["nu"],
                 kernel=params["kernel"],
                 degree=params["degree"],
                 coef0=params["coef0"],
                 shrinking=params["shrinking"],
                 probability=True,
                 class_weight="balanced",
                 random_state=RANDOM_STATE)


def load_linear_svc_model(params):
    return LinearSVC(C=params["c"],
                     fit_intercept=False,
                     class_weight="balanced",
                     dual=False,
                     random_state=RANDOM_STATE)


def load_svm_heart_model():
    study = load_study("svm", "heart")
    return load_svm_model(study.best_params)


def load_svm_credit_card_model():
    study = load_study("svm", "credit_card")
    return load_svm_model(study.best_params)


def load_svm_heart_preprocessor():
    return load_preprocessor("svm", "heart")


def load_svm_credit_card_preprocessor():
    return load_preprocessor("svm", "credit_card")


if __name__ == "__main__":
    # Study Heart Failure dataset with SVM
    prep = make_pipeline(StandardScaler(),
                         PCA(n_components="mle", random_state=RANDOM_STATE))
    generate_heart_study(objective, "svm", 300, data_preprocessor=prep)

    analyze_clf(dataset_name="heart",
                name="Heart Failure",
                labels=["Healthy", "Failure"],
                clf=load_svm_heart_model(),
                data_preprocessor=load_svm_heart_preprocessor())

    # Study Credit Card dataset with SVM
    # prep = make_pipeline(StandardScaler(),
    #                      PCA(n_components=14, random_state=RANDOM_STATE))
    # generate_credit_card_study(objective,
    #                            "svm",
    #                            75,
    #                            percent_sample=0.1,
    #                            data_preprocessor=prep)
    #
    # analyze_clf(dataset_name="credit_card",
    #             name="Credit Card Fraud",
    #             labels=["No Fraud", "Fraud"],
    #             clf=load_svm_credit_card_model(),
    #             train_size=0.05,
    #             data_preprocessor=load_svm_credit_card_preprocessor())
