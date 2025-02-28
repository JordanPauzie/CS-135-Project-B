'''
CollabFilterOneVectorPerItem.py

Defines class: `CollabFilterOneVectorPerItem`

Scroll down to __main__ to see a usage example.
'''

# Make sure you use the autograd version of numpy (which we named 'ag_np')
# to do all the loss calculations, since automatic gradients are needed
import autograd.numpy as ag_np

# Use helper packages
from AbstractBaseCollabFilterSGD import AbstractBaseCollabFilterSGD
from train_valid_test_loader import load_train_valid_test_datasets

# Some packages you might need (uncomment as necessary)
## import pandas as pd
## import matplotlib

# No other imports specific to ML (e.g. scikit) needed!

class CollabFilterOneVectorPerItem(AbstractBaseCollabFilterSGD):
    ''' One-vector-per-user, one-vector-per-item recommendation model.

    Assumes each user, each item has learned vector of size `n_factors`.

    Attributes required in param_dict
    ---------------------------------
    mu : 1D array of size (1,)
    b_per_user : 1D array, size n_users
    c_per_item : 1D array, size n_items
    U : 2D array, size n_users x n_factors
    V : 2D array, size n_items x n_factors

    Notes
    -----
    Inherits *__init__** constructor from AbstractBaseCollabFilterSGD.
    Inherits *fit* method from AbstractBaseCollabFilterSGD.
    '''

    def init_parameter_dict(self, n_users, n_items, train_tuple):
        ''' Initialize parameter dictionary attribute for this instance.

        Post Condition
        --------------
        Updates the following attributes of this instance:
        * param_dict : dict
            Keys are string names of parameters
            Values are *numpy arrays* of parameter values
        '''
        random_state = self.random_state # inherited RandomState object

        self.param_dict = dict(
            mu=ag_np.ones(1),
            b_per_user=ag_np.ones(n_users),
            c_per_item=ag_np.ones(n_items), 
            U=0.001 * random_state.randn(n_users, self.n_factors), 
            V=0.001 * random_state.randn(n_items, self.n_factors), 
            )


    def predict(self, user_id_N, item_id_N,
                mu=None, b_per_user=None, c_per_item=None, U=None, V=None):
        ''' Predict ratings at specific user_id, item_id pairs

        Args
        ----
        user_id_N : 1D array, size n_examples
            Specific user_id values to use to make predictions
        item_id_N : 1D array, size n_examples
            Specific item_id values to use to make predictions
            Each entry is paired with the corresponding entry of user_id_N

        Returns
        -------
        yhat_N : 1D array, size n_examples
            Scalar predicted ratings, one per provided example.
            Entry n is for the n-th pair of user_id, item_id values provided.
        '''

        if mu is None: mu = self.param_dict["mu"]
        if b_per_user is None: b_per_user = self.param_dict["b_per_user"]
        if c_per_item is None: c_per_item = self.param_dict["c_per_item"]
        if U is None: U = self.param_dict["U"]
        if V is None: V = self.param_dict["V"]

        return mu + b_per_user[user_id_N] + c_per_item[item_id_N] + ag_np.sum(U[user_id_N] * V[item_id_N], axis = 1)

    def calc_loss_wrt_parameter_dict(self, param_dict, data_tuple):
        ''' Compute loss at given parameters

        Args
        ----
        param_dict : dict
            Keys are string names of parameters
            Values are *numpy arrays* of parameter values

        Returns
        -------
        loss : float scalar
        ''' 
        user_id_N, item_id_N, y_N = data_tuple
        yhat_N = self.predict(user_id_N, item_id_N, **param_dict) 
        loss_total = self.alpha * (ag_np.sum(param_dict["U"] ** 2) + ag_np.sum(param_dict["V"] ** 2)) + ag_np.sum((y_N - yhat_N) ** 2)

        return loss_total    

if __name__ == '__main__':

    # Load the dataset
    train_tuple, valid_tuple, test_tuple, n_users, n_items = \
        load_train_valid_test_datasets()
    # Create the model and initialize its parameters
    # to have right scale as the dataset (right num users and items)
    model = CollabFilterOneVectorPerItem(
        n_epochs=10, batch_size=50, step_size=0.1,
        n_factors=10, alpha=0.001)
    model.init_parameter_dict(n_users, n_items, train_tuple)

    # Fit the model with SGD
    model.fit(train_tuple, valid_tuple)
    test_user_id, test_item_id, true_ratings = test_tuple
    predicted_ratings = model.predict(test_user_id, test_item_id)
    test_mae = ag_np.mean(ag_np.abs(predicted_ratings - true_ratings))
    print("final validation MAE: ", model.trace_mae_valid[-1])
    print("test set MAE: ", test_mae)