import xgboost as xgb
from xgb_model import DataSet

# setup parameters for xgboost
param = {}
# scale weight of positive examples
param['eta'] = 0.1
param['max_depth'] = 8
param['silent'] = 1

if __name__ == "__main__":
    dataset = DataSet("london", True)
#    dataset.trainEntrance()
    num_round = 5
#    xg_train = xgb.DMatrix(dataset.model, label=dataset.label)
#    xg_train.save_binary("./train.buffer")
#    xg_train = xgb.DMatrix("./train.buffer")
#    bst = xgb.train(param, xg_train, num_round)
#    bst.save_model("./xgb.model")

    bst = xgb.Booster(param)
    bst.load_model("./xgb.model")