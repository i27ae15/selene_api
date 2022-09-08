# Python
import secrets

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

def train(data_to_train_model:dict, model_name=str):

    training_sentences = []
    training_labels = []
    labels = []
    responses = []

    nodes:list[SeleneNode] = []
    main_tags = []
    previous_node:SeleneNode = None
    head_node:SeleneNode = None

    for node in data_to_train_model['intents']:
        for pattern in node['patterns']:
            training_sentences.append(pattern)
            training_labels.append(node['node'])
        
        responses.append(node['responses'])
        
        if node['node'] not in labels:
            labels.append(node['node'])
            main_tags.append(node['node'])

            
        data_to_serialize = {
            'name': node['node'],
            'patterns_raw_text': ','.join(training_sentences),
            'responses_raw_text': responses,
            'random_response': data_to_train_model['random_response'] if 'random_response' in data_to_train_model else True,
        }

        
        serializer = SeleneNodeSerializer(data=data_to_serialize)

        if serializer.is_valid():
            serializer.save()

            head_node:SeleneNode = serializer.instance

            nodes.append(serializer.instance)

            if not node.get('steps'):
                break

            for step in node['steps']:

                data_to_serialize = {
                    'name': step['name'],
                    'patterns_raw_text': ','.join(step['patterns']),
                    'responses_raw_text': ','.join(step['responses']),
                    'parent_id': previous_node.id if previous_node else head_node.id,
                    'head_id': head_node.id,
                    'do_after': step['do_after'],
                    'do_before': step['do_before'],
                    'block_step': step['block_step'],
                    'random_response': step['random_response'],
                }

                for pattern in step['patterns']:
                    training_sentences.append(pattern)
                    training_labels.append(node['node'])
                
                responses.append(node['responses'])
                
                if node['node'] not in labels:
                    labels.append(node['node'])

                # we append the current node to the list to be able to set the model that is attached to the node, 
                # model that is created at the end of this function

                serializer = SeleneNodeSerializer(data=data_to_serialize)

                if serializer.is_valid():
                    serializer.save()


                    if previous_node is not None:
                        previous_node.next_id = serializer.instance.id
                        previous_node.save()
                    
                    previous_node = serializer.instance
                    nodes.append(serializer.instance)

                else:
                    print('-------------------------------')
                    print(serializer.errors)
                    print('-------------------------------')
                    return 'error'

        else:
            print('-----------------')
            print(serializer.errors)
            print('-----------------')
            return 'error'
                
    line = str()
    for node in nodes:
        line += f'{node.id} <- '

    line += 'None'

    reversed_nodes = nodes[::-1]

    reversed_line = str()
    for node in reversed_nodes:
        reversed_line += f'{node.id} <- '
    
    reversed_line += 'None'
            
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
    model_path = f"selene_models_saved/model_{secrets.token_hex()}/{model_name}"
    model.save(model_path)

    model_serializer = SeleneModelSerializer(data={
        'name': model_name,
        'model_path': model_path,
        'main_tags': main_tags,
    })

    if model_serializer.is_valid():
        model_serializer.save()

        for node in nodes:
            node.model = model_serializer.instance
            node.save()
    else:
        print('-----------------')
        print(model_serializer.errors)
        print('-----------------')
    
    #NOTE: Investigate about the tokenizers
    import pickle

    # to save the fitted tokenizer
    with open('tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    # to save the fitted label encoder
    with open('label_encoder.pickle', 'wb') as ecn_file:
        pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)