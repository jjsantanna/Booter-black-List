from verifier import Verifier
import storage
import math

# classification sub-system based on the Naive Bayes classification metric
class Verifier_Bayes(Verifier):
	def __init__(this):
		Verifier.__init__(this)
		
		this.p_booter 	  = 0.1001
		this.p_non_booter = 0.8999

		# calculated: see 'naive_bayes_probabilities.txt'
		this.p_booter_characteristics     = [
    		0.97, 0.93, 0.94, 0.37, 0.89, 0.89, 0.38, 0.72, 0.85, 0.74, 0.92, 0.52, 0.22, 0.44, 0.82
		]
		this.p_non_booter_characteristics = [
			0.23, 0.80, 0.67, 0.06, 0.14, 0.62, 0.28, 0.18, 0.35, 0.16, 0.20, 0.19, 0.19, 0.36, 0.66
		]

	# calculates the probability a score vector is a Booter ranging between [0,1]
	def Calculate(this, score_table, save_table, url):
		# 0. get score vector and invalid indices (those with - 1.0 are excluded from calculations)
		score_vector = this.GetScoreVector(score_table, url)
		invalids 	 = this.GetInvalidIndices(score_vector)  
		valid_nr	 = len(score_vector) - len(invalids)
		# 1. Get all weights between [0,1] to multiply each individual chance with the corresponding weight
		# - basically we're reducing the chance of a characteristic occuring if it's less influental
		weights		 = this.GetScaledWeightVector(invalids)
		score_vector = this.GetWeightedScoreVector(score_vector, invalids)
		# 2. calculate the Naive Bayes probablity for both Outcome=Booter and Outcome=Non-Booter and
		# return that with highest probabiltiy = category
		# 2.1 - P(O=Booter)
		b_chance = this.p_booter # base rate => Prob(Outcome)
		for i in range(0, len(score_vector)):
			if i not in invalids:
				if score_vector[i] >= (0.5  * weights[i]): # is 1.0
					b_chance *= this.p_booter_characteristics[i]
				else:
					b_chance *= (1.0 - this.p_booter_characteristics[i]) # the NOT version of evidence probability
			else:
				b_chance *= 1.0 # if characteristic unknown, take average probability 
		# print('|Prob(Booter)....:' + str(b_chance))
		# 2.2 - P(O=Non-Booter)
		non_b_chance = this.p_non_booter # base rate => Prob(Outcome)
		for i in range(0, len(score_vector)):
			if i not in invalids:
				if score_vector[i] >= (0.5  * weights[i]): # is 1.0
					non_b_chance *= this.p_non_booter_characteristics[i]
				else:
					non_b_chance *= (1.0 - this.p_non_booter_characteristics[i]) 
			else:
				non_b_chance *= 1.0 # as long as average prob. is same as P(O=Non-Booter) case it's fine
		# print('|Prob(Non-Booter):' + str(non_b_chance))

		# 3 compare both probabilities and store 1.0 if Booter >= Non-Booter and 0.0 otherwise
		if b_chance >= non_b_chance:
			score = 1.0
		else:
			score = 0.0
		this.SaveScore(save_table, url, 'naive_bayes', score)	

