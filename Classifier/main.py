from verifier_distance import Verifier_Distance
from verifier_naive_bayes import Verifier_Bayes
from verifier_knn import Verifier_KNN
import storage
import accuracy


###########################################################
##    VERIFY                                             ##
###########################################################
verDistance = Verifier_Distance()
verBayes	= Verifier_Bayes()
verKNN		= Verifier_KNN(True) # use weights
test_table_to_verification = {}
test_table_to_verification['scores']  = 'verification'
test_table_to_verification['test_scores']  = 'verification'
test_table_to_verification['test_scores2'] = 'verification2'
test_table_to_verification['test_scores3'] = 'verification3'
test_tables = ['test_scores', 'test_scores2', 'test_scores3']
# test_tables = ['scores']
for table in test_tables:
	print('== ===========================')
	print('TEST TABLE: ' + table)
	print('== ===========================')
	for url in storage.Select('SELECT domainName FROM ' + table):
		print('VERIFYING URL: ' + url[0])
		# verDistance.Euclidean_Distance(table, test_table_to_verification[table], url[0])
		# verDistance.Squared_Euclidian_Distance(table, test_table_to_verification[table], url[0])
		# verDistance.Manhattan_Distance(table, test_table_to_verification[table], url[0])
		# verDistance.Cosine_Distance(table, test_table_to_verification[table], url[0])
		# verDistance.Fractional_Distance(table, test_table_to_verification[table], url[0], 0.5)
		# verBayes.Calculate(table, test_table_to_verification[table], url[0])
		verKNN.Calculate(table, test_table_to_verification[table], url[0], 3)


###########################################################
##    ACCURACY ARITHMETIC                                ##
###########################################################
# thresholds = [0.41, 0.66, 0.62, 0.78, 0.82, 0.5, 0.5] # unweighted (euc, sq. euc, manhattan, cosine, fractional)
thresholds = [0.71, 0.89, 0.75, 0.94, 0.83, 0.5, 0.5] # weighted  (euc, sq. euc, manhattan, cosine, fractional)
results = accuracy.CalculateAccuracy(thresholds)
accuracy.PrintResults(results, False, False)


# or calculate optimal threshold values for distance metrics
# results = accuracy.CalculateThresholds(100, 'fractional', 'scores')
# accuracy.PrintThresholds(results, 'gnu/fractional_weighted.dat')

# TODO:
# - then work on KNN. Calculate KNN with best distance metric found from previous results (use weighted metric)
# - calculate accuracy rates for KNN with n ranging from 1 - 15; (get this N from training set!)


# FOR KNN METRIC CALCULATIONS:
# metrics = ['euclidean' , 'squared_euclidean', 'manhattan', 'cosine', 'fractional']
# metric = 'manhattan'
# for k in range(15, 101): # 1 - 15
# 	if k % 5 == 0:
# 		for url in storage.Select('SELECT domainName FROM scores'):
# 			print('VERIFYING URL: ' + url[0])
# 			verKNN.Calculate('scores', 'verification', url[0], k)
# 		results = accuracy.CalculateAccuracy(thresholds)
# 		accuracy.PrintResults(results, False, True, metric, k)


