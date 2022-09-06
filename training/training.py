# Python

# Numpy
import numpy as np 

# Tensorflow
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense, Embedding, GlobalAveragePooling1D
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder

# models
from selene_models.models import SeleneModel, SeleneNode
from selene_models.serializers import SeleneModelSerializer, SeleneNodeSerializer

def train(data_to_train_model:dict):

    training_sentences = []
    training_labels = []
    labels = []
    responses = []

    previous_node:SeleneNode = None

    for intent in data_to_train_model['intents']:
        for pattern in intent['patterns']:
            training_sentences.append(pattern)
            training_labels.append(intent['node'])
        
        responses.append(intent['responses'])
        
        if intent['node'] not in labels:
            labels.append(intent['node'])
            
        data_to_serialize = {
            'name': data_to_train_model['name'],
            'patterns_raw_text': ','.join(training_sentences),
            'responses_raw_text': ','.join(responses),
        }
            
        if previous_node is not None:
            data_to_serialize['parent'] = previous_node.id
            
        
        serializer = SeleneNodeSerializer(data=data_to_serialize)
        
        if serializer.is_valid():
            serializer.save()
            
            current_node:SeleneNode = serializer.instance
            
            if previous_node is not None:
                previous_node.next = current_node
            
            previous_node = serializer.instance
        
            
    num_classes = len(labels)

    lbl_encoder = LabelEncoder()
    lbl_encoder.fit(training_labels)
    training_labels = lbl_encoder.transform(training_labels)

    vocab_size = 1000
    embedding_dim = 16
    max_len = 20
    oov_token = "<OOV>"

    tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
    tokenizer.fit_on_texts(training_sentences)
    word_index = tokenizer.word_index
    sequences = tokenizer.texts_to_sequences(training_sentences)
    padded_sequences = pad_sequences(sequences, truncating='post', maxlen=max_len)


    model = Sequential()
    model.add(Embedding(vocab_size, embedding_dim, input_length=max_len))
    model.add(GlobalAveragePooling1D())
    model.add(Dense(16, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy', 
                optimizer=tf.keras.optimizers.Adam(learning_rate=0.01), metrics=['accuracy'])

    epochs = 100
    history = model.fit(padded_sequences, np.array(training_labels), epochs=epochs)

    # to save the trained model
    model.save("chat_model")

    
    #NOTE: Investigate about the tokenizers
    import pickle

    # to save the fitted tokenizer
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    # to save the fitted label encoder
    with open('label_encoder.pickle', 'wb') as ecn_file:
        pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)