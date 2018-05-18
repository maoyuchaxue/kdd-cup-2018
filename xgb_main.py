import xgboost as xgb
from xgb_model import DataSet

# setup parameters for xgboost
param = {}
# scale weight of positive examples
param['eta'] = 0.1
param['max_depth'] = 6
param['silent'] = 1
param['num_class'] = 6

if __name__ == "__main__":
    dataset = DataSet("london", True)
    dataset.trainEntrance()
    num_round = 5
    xg_train = xgb.DMatrix(dataset.model, label=dataset.label)
    bst = xgb.train(param, xg_train, num_round)