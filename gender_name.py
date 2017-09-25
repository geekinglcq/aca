# -*- coding: utf-8 -*-

import re
import json
import nltk
import random
class gender_guesser():
    """
    Guess one's gender for given name
    For two guess methods: simple guess & advanced guess
        return a char: "m"-male "f"-female
    To use advanced guess, you must `train_model` on ahead
    """
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        with open('./data/name_gender.json') as f:
            data = json.load(f)
        self.male_name_set = set(data['male'])
        self.female_name_set = set(data['female'])
    
    def extract_name_features(self, name):
        name = name.lower()          
        return{                      
            'last_two': name[-2:],   
            'last_three': name[-3:], 
            'last_four': name[-4:] if len(name) > 3 else name[-3:] + ' ',
            'last_five': name[-5:] if len(name) > 4 else name[-3:] + '  ',
            'last_six': name[-6:] if len(name) > 5 else name[-3:] + '   ',
            'last_six': name[-7:] if len(name) > 6 else name[-3:] + '    ',
            #'first': name[0],        
            'first2': name[:1],
            'length': len(name)       
        }             

    def train_model(self):
        all_names = [(i, 'm') for i in self.male_name_set] \
            + [(i, 'f') for i in self.female_name_set]
        random.shuffle(all_names)
        train_set = all_names[9000:]
        test_set = all_names[:9000]
        train_features = [(self.extract_name_features(n), g) for n, g in train_set]
        test_features = [(self.extract_name_features(n), g) for n, g in test_set]
        self.classifier = nltk.NaiveBayesClassifier.train(train_features)
        print(nltk.classify.accuracy(self.classifier, test_features))

    def simple_guess(self, name):
        # Acc = 0.833 in training set
        if name in self.female_name_set:
            return 'f'
        else:
            return 'm'

    def predict_gender(self, data):
        """
        data - standrad DataFrame
        """
        for i, r in data.iterrows():
            gender = self.simple_guess(r['name'])
            data.set_value(i, 'gender', gender)

    def advanced_guess(self, name):
        # Acc = 0.778 in training set
        if not(self.classifier):
            self.train_model()
            print("To use advanced guess, call `train_model` first")
        features = self.extract_name_features(name)
        return self.classifier.classify(features)
        