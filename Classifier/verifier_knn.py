from verifier import Verifier
import storage
import math


# classification sub-system focussed on the k-NN classification metric
class Verifier_KNN(Verifier):
	def __init__(this, use_weights = True):
		Verifier.__init__(this)
		this.LoadData(use_weights)

	def LoadData(this, use_weights):
		# 1. Get all Booter vectors from the training dataset
		query  = 'SELECT scores.* FROM scores '
		query += 'INNER JOIN urls '
		query += 'ON urls.domainName = scores.domainName '
		query += 'WHERE urls.status = \'on\' '
		this.scores_booter     = {}
		weights = this.GetScaledWeightVector([])
		for score_vector in storage.Select(query + ' AND urls.[booter?] = \'Y\''):
			if use_weights:
				this.scores_booter[score_vector[0]] = [a*b for a,b in zip(weights,list(score_vector[2:]))]
			else:
				this.scores_booter[score_vector[0]] = list(score_vector[2:])
		this.scores_non_booter = {}
		for score_vector in storage.Select(query + ' AND urls.[booter?] = \'N\''):
			if use_weights:
				this.scores_non_booter[score_vector[0]] = [a*b for a,b in zip(weights,list(score_vector[2:]))]
			else:
				this.scores_non_booter[score_vector[0]] = list(score_vector[2:])

	# calculates the distance between a score vector and all other neighbors and chooses
	# the partition with the k-nearest neighbors
	def Calculate(this, score_table, save_table, url, k):
		# 0. get score vector and invalid indices (those with - 1.0 are excluded from calculations)
		score_vector = this.GetScoreVector(score_table, url)
		invalids 	 = this.GetInvalidIndices(score_vector)  
		score_vector = this.GetWeightedScoreVector(score_vector, invalids)
		# 1. calculate distance between all points
		neighbor_distances = []
		for key in this.scores_booter:
			neighbor_score = this.scores_booter[key]
			distance 	   = this.Distance(neighbor_score, score_vector, invalids)
			neighbor_distances.append(('booter', distance))
		for key in this.scores_non_booter:
			neighbor_score = this.scores_non_booter[key]
			distance 	   = this.Distance(neighbor_score, score_vector, invalids)
			neighbor_distances.append(('non-booter', distance))
		# 2. sort list based on distance
		sorted_on_distance = sorted(neighbor_distances, key=lambda pair: pair[1]) 
		sorted_on_distance = sorted_on_distance[1:] # start from 2nd index, 1st is always current vector with distance 0.0
		# 3. take the k-nearest neighbors and calculate the contribution to one category 
		k_nearest         = sorted_on_distance[:k]
		score_booters     = 0.0
		score_non_booters = 0.0
		total_booters     = len(this.scores_booter)
		total_non_booters = len(this.scores_non_booter)
		for neighbor in k_nearest: 
			if neighbor[0] == 'booter':
				score_booters     += 1.0 / total_booters
			else:
				score_non_booters += 1.0 / total_non_booters
		# print('score_booters:' + str(score_booters) + ' | score_non_booters: ' + str(score_non_booters))
		# 4. store result as either booter or non-booter based on which score is higher
		if score_booters >= score_non_booters:
			score = 1.0
		else:
			score = 0.0
		this.SaveScore(save_table, url, 'knn', score)


	# distance metric used to calculate distance between two n-dimensional points
	# this is also the metric where we introduce weights
	# EUCLIDEAN
	# def Distance(this, vecA, vecB, invalids):
	# 	# calculate component-wise difference
	# 	diff = []
	# 	for i in range(0, len(vecA)):
	# 		if i not in invalids:
	# 			diff.append(vecA[i] - vecB[i])
	# 		else:
	# 			diff.append(0.0)
	# 	return this.VectorLength(diff) 

	# SQUARED EUCLIDEAN
	# def Distance(this, vecA, vecB, invalids):
	# 	diff = 0.0
	# 	for i in range(0, len(vecA)):
	# 		if i not in invalids:
	# 			diff += (vecA[i] - vecB[i])**2
	# 	return diff

	# MANHATTAN
	# def Distance(this, vecA, vecB, invalids):
	# 	diff = 0.0
	# 	for i in range(0, len(vecA)):
	# 		if i not in invalids:
	# 			diff += abs(vecA[i] - vecB[i])
	# 	return diff

	# FRACTIONAL (deemed as best distance metric on both unweighted and weighted scenario)
	def Distance(this, vecA, vecB, invalids):
		f    = 0.5
		diff = 0.0
		for i in range(0, len(vecA)):
			if i not in invalids:
				diff += abs(vecA[i] - vecB[i])**f
		diff = diff**(1/f)
		return diff

	# COSINE
	# def Distance(this, vecA, vecB, invalids):
	# 	diff = 0.0
	# 	newA = []
	# 	newB = []
	# 	for i in range(0, len(vecA)):
	# 		if i not in invalids:
	# 			newA.append(vecA[i])
	# 			newB.append(vecB[i])
	# 			diff += vecA[i] * vecB[i]
	# 		else:
	# 			newA.append(0.0) # necessary for VectorLength equation for them all to be of n = 15
	# 			newB.append(0.0)
	# 	diff = diff / (this.VectorLength(newA) * this.VectorLength(newB))
	# 	return diff

