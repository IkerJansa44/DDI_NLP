import pickle

with open("common_root_dict.pkl", 'rb') as f:
    loaded_dict = pickle.load(f)

print(loaded_dict['mechanism'])