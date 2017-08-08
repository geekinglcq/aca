from sklearn.svm import SVR

class ILearner(object):
	"""description of class"""
	def train(self,X,y):
		pass
	def predict(self,X):
		pass

class Svr(ILearner):

	def __init__(self, kernel='rbf', degree=3, gamma='auto', coef0=0.0, tol=0.001, C=1.0, epsilon=0.1, shrinking=True, cache_size=200, verbose=False, max_iter=-1):
		self.kernel = kernel
		self.C = C
		self.gamma = gamma
		self.coef0 = coef0
		self.tol = tol
		self.epsilon = epsilon
		self.shrinking = shrinking
		self.cache_size = cache_size
		self.verbose = verbose
		self.max_iter = max_iter
		self.model = SVR(kernel=self.kernel, C=self.C, gamma=self.gamma, coef0=self.coef0, tol=self.tol, epsilon=self.epsilon, shrinking=self.shrinking, cache_size=self.cache_size, verbose=self.verbose , max_iter=self.max_iter)

	def train(self, X, y):
		self.model.fit(X,y)
		pass

	def predict(self, X):
		return self.model.predict(X)