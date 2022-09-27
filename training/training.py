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

# pickle
import pickle

# models
from selene_models.models import SeleneModel, SeleneNode
from selene_models.serializers import SeleneModelSerializer, SeleneNodeSerializer


def train(data_to_train_model:dict, model_name=str):

    training_sentences:list[str] = []
    training_labels:list[str] = []
    labels:list[str] = []

    nodes:list[SeleneNode] = []
    main_tags:list[str] = []
    previous_node:SeleneNode = None
    head_node:SeleneNode = None

    local_training_sentences:list[str] = []
    
    TOKEN = secrets.token_urlsafe(16)

    for node in data_to_train_model['intents']:
        node:dict
        for pattern in node['patterns']:
            training_sentences.append(pattern)
            local_training_sentences.append(pattern)

            training_labels.append(node['node'])
        
        if node['node'] not in labels:
            labels.append(node['node'])
            main_tags.append(node['node'])

            
        data_to_serialize = {
            'name': f'{TOKEN}-{node["node"]}',
            'patterns': local_training_sentences,
            'responses': node['responses'],
            'random_response': data_to_train_model['random_response'] if 'random_response' in data_to_train_model else True,
            'do_before': node.get('do_before', {}),
            'do_after': node.get('do_after', {}),
        }
        
        if nodes:= node.get('next_node_on_option'):
            data_to_serialize['next_node_on_option'] = [f'{TOKEN}-{nodes[opt]}' for opt in nodes]
        else:
            data_to_serialize['next_node_on_option'] = dict()


        main_node_serializer = SeleneNodeSerializer(data=data_to_serialize)

        if main_node_serializer.is_valid():
            main_node_serializer.save()
            
            # aparently this lines does a shit
            local_training_sentences:list[str] = []
            
            head_node:SeleneNode = main_node_serializer.instance

            nodes.append(main_node_serializer.instance)

            if not node.get('steps'):
                continue

            for step in node['steps']:
                step:dict
                data_to_serialize = {
                    'name': f'{TOKEN}-{step["node"]}',
                    'patterns': step['patterns'],
                    'responses': step['responses'],
                    'head_id': head_node.id,
                    'do_after': step.get('do_after', {}),
                    'do_before': step.get('do_before', {}),
                    'block_step': step.get('block_step', True),
                    'random_response': step.get('random_response', False),
                    'end_steps': step.get('end_steps', False),
                }
                
                if nodes:= node.get('next_node_on_option'):
                    data_to_serialize['next_node_on_option'] = [f'{TOKEN}-{nodes[opt]}' for opt in nodes]
                else:
                    data_to_serialize['next_node_on_option'] = dict()


                for pattern in step['patterns']:
                    training_sentences.append(pattern)
                    training_labels.append(node['node'])

                
                if node['node'] not in labels:
                    labels.append(node['node'])

                # we append the current node to the list to be able to set the model that is attached to the node, 
                # model that is created at the end of this function

                sub_node_serializer = SeleneNodeSerializer(data=data_to_serialize)

                if sub_node_serializer.is_valid():
                    sub_node_serializer.save()
                    node_instance:SeleneNode = sub_node_serializer.instance

                    if not head_node.next_node_on_option:
                        # setting the value by default for the head_node
                        head_node.set_default_next_node(node_instance.name)


                    if previous_node is not None and not previous_node.next_node_on_option and previous_node.end_steps is False:
                        previous_node.set_default_next_node(node_instance.name)
                    
                    previous_node = sub_node_serializer.instance
                    nodes.append(node_instance)

                else:
                    print('-------------------------------')
                    print(sub_node_serializer.errors)
                    print('-------------------------------')
                    return 'error'

        else:
            print('-----------------')
            print(main_node_serializer.errors)
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
    history = model.fit(padded_sequences, np.array(training_labels), epochs=epochs, verbose=0)

    # to save the trained model
    model_path = f"selene_models_saved/model_{secrets.token_hex(16)}/"


    model.save(model_path + 'model')


    # to save the fitted tokenizer
    with open(model_path + 'tokenizer.pickle', 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    # to save the fitted label encoder
    with open(model_path + 'label_encoder.pickle', 'wb') as ecn_file:
        pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)


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
    
