from sklearn.svm import SVR

class ILearner(object):
	"""description of class"""
	def train(self,X,y):
		pass
	def predict(self,X):
		pass

class Svr(ILearner):

	def __init__(self, kernel='rbf', degree=3, gamma='auto', coef0=0.0, tol=0.001, C=1.0, epsilon=0.1, shrinking=True, cache_size=200, verbose=False, max_iter=-1):
		self.kernel=kernel
		self.C = C
		self.gamma=gamma
		self.model = SVR(kernel=self.kernel,gamma=self.gamma,C=self.C)

	def train(self, X, y):
		self.model.fit(X,y)
		pass

	def predict(self, X):
		return self.model.predict(X)