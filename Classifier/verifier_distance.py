from verifier import Verifier
import storage
import math


# verification sub-class for Distance metrics:
# Eucldiean, Squared Euclidean, Manhattan, Fractional and Cosine
class Verifier_Distance(Verifier):
	def __init__(this):
		Verifier.__init__(this)
		# below we add two vectors for comparing between what feature vector is of the ideal Booter
		# and what feature vector is of the ideal non-Booter.
		# currently they are defined as completely 0.0 or 1.0; experimenting wtih different values e.g.
		# averages of Booter training dataset, numbers more often assosicated with Booters and so on did
		# not generate consistently better results (sometimes it did, sometimes it didn't). We thus keep
		# the [1.0,...,1.0] vector as this directly corresponds with the indvidual distance each element
		# has to its maximum value.
		this.vector_booter     = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

	# calculates a similarity score from a distance score
	def Similarity(this, distance_score):
		return 1.0 - distance_score


	# caclulates the Euclidean distance between a feature vector and Booter vector
	# saves the result into the database
	def Euclidean_Distance(this, score_table, save_table, url):
		# 0. get score vector and invalid indices (those with -1.0 are excluded from calculations)
		score_vector = this.GetScoreVector(score_table, url)
		invalids 	 = this.GetInvalidIndices(score_vector)
		valid_nr	 = len(score_vector) - len(invalids)
		score_vector = this.GetWeightedScoreVector(score_vector, invalids)
		score_booter = this.GetWeightedScoreVector(this.vector_booter, invalids) 
		# 1. first obtain difference vector
		max_distance      = 0.0
		vector_difference = []
		for i in range(0, len(score_vector)):
			if i not in invalids:
				vector_difference.append(score_booter[i] - score_vector[i])
				max_distance += score_booter[i] * score_booter[i]
		# 2. then calculate length of difference vector
		sum_squared = 0.0
		for value in vector_difference:
			sum_squared += (value * value)
		# 3. then obtain square root to get the vector's length i.e. its distance to vector_booter
		distance = math.sqrt(sum_squared)
		# 4. normalize results and calculate similarity
		max_distance = math.sqrt(max_distance)
		distance 	 = distance / max_distance
		score        = this.Similarity(distance)
		# 5. finally save result in database
		this.SaveScore(save_table, url, 'euclidean', score)

	# caclulates the squared Euclidean distance between a feature vector and Booter vector
	# saves the result into the database
	def Squared_Euclidian_Distance(this, score_table, save_table, url):
		# 0. get score vector
		score_vector = this.GetScoreVector(score_table, url)
		invalids 	 = this.GetInvalidIndices(score_vector)
		valid_nr	 = len(score_vector) - len(invalids)
		score_vector = this.GetWeightedScoreVector(score_vector, invalids)
		score_booter = this.GetWeightedScoreVector(this.vector_booter, invalids) 
		# 1. first obtain difference vector
		max_distance      = 0.0
		vector_difference = []
		for i in range(0, len(score_vector)):
			if i not in invalids:
				vector_difference.append(score_booter[i] - score_vector[i])
				max_distance += score_booter[i] * score_booter[i]
		# 2. then calculate length of difference vector
		distance = 0.0
		for value in vector_difference:
			distance += (value * value)
		# 3. normalize results
		distance 	 = distance / max_distance
		score        = this.Similarity(distance)
		# 4. and finally store result in database
		this.SaveScore(save_table, url, 'squared_euclidean', score)

	# caclulates the Manhattan distance between a feature vector and Booter vector
	# saves the result into the database
	def Manhattan_Distance(this, score_table, save_table, url):
		# 0. get score vector
		score_vector = this.GetScoreVector(score_table, url)
		invalids 	 = this.GetInvalidIndices(score_vector)
		valid_nr	 = len(score_vector) - len(invalids)
		score_vector = this.GetWeightedScoreVector(score_vector, invalids)
		score_booter = this.GetWeightedScoreVector(this.vector_booter, invalids) 
		# 1. get manhattan distance
		max_distance = 0.0
		distance 	 = 0.0
		for i in range(0, len(score_vector)):
			if i not in invalids:
				distance     += abs(score_booter[i] - score_vector[i])
				max_distance += score_booter[i]
		# 2. normalize results
		distance 	 = distance / max_distance
		score        = this.Similarity(distance)
		# store result in database
		this.SaveScore(save_table, url, 'manhattan', score)

	# caclulates the Cosine distance between a feature vector and Booter vector
	# saves the result into the database
	def Cosine_Distance(this, score_table, save_table, url):
		# 0. get score vector
		score_vector = this.GetScoreVector(score_table, url)
		invalids 	 = this.GetInvalidIndices(score_vector)
		valid_nr	 = len(score_vector) - len(invalids)
		score_vector = this.GetWeightedScoreVector(score_vector, invalids)
		score_booter = this.GetWeightedScoreVector(this.vector_booter, invalids) 
		# 1. calculate cosine distance
		dot_product = 0.0
		for i in range(0, len(score_vector)):
			if i not in invalids:
				dot_product += score_booter[i] * score_vector[i]
		denominator = this.VectorLength(score_booter) * this.VectorLength(score_vector)
		score    = 0.0
		if denominator != 0.0:
			score = dot_product / denominator
			# 2. normalize results
			# distance = distance * 0.5 + 0.5 # transforms from [-1,1] to [0,1] range # no need to convert, angle will never be negative as there are no negative vector values so will always be between [0,1]
			# score    = distance
		# store result in database
		this.SaveScore(save_table, url, 'cosine', score)

	# caclulates the Fractional distance between a feature vector and Booter vector
	# saves the result into the database
	# 
	# the normalization is calculated as follows:
	# to get the maximum distance possible for a given f we assume each individual
	# element difference equals 1.0. This then gives us a maximum distance value
	# that we multiply with the power of (1/f). We take the invalid metrics into
	# account.
	def Fractional_Distance(this, score_table, save_table, url, f = 1.0):
		# 0. get score vector
		score_vector = this.GetScoreVector(score_table, url)
		invalids 	 = this.GetInvalidIndices(score_vector)
		valid_nr	 = len(score_vector) - len(invalids)
		score_vector = this.GetWeightedScoreVector(score_vector, invalids)
		score_booter = this.GetWeightedScoreVector(this.vector_booter, invalids) 
		# calculate fractional distance
		max_distance = 0.0
		distance 	 = 0.0
		for i in range(0, len(score_vector)):
			if i not in invalids:
				distance     += abs(score_booter[i] - score_vector[i])**f
				max_distance += score_booter[i]**f
		distance = distance**(1/f)
		# normalize results
		# - calculate maximum value by assuming input vector is completely 1.0 in equation
		max_distance = max_distance**(1/f) 
		distance = distance / max_distance
		score    = this.Similarity(distance)
		# store result in database
		this.SaveScore(save_table, url, 'fractional', score)

