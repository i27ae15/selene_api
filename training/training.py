# Python
import secrets

# django
from django.utils.translation import gettext_lazy as _

# rest_framework
from rest_framework import exceptions

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
from selene_models.models import SeleneModel, SeleneNode, SeleneModelVersion
from selene_models.serializers import SeleneModelSerializer, SeleneNodeSerializer

from print_pp.logging import Print


def train(data_to_train_model:dict, model_name:str, previous_model_version:SeleneModelVersion=None):

    # variables for training

    training_sentences:list[str] = []
    training_labels:list[str] = []
    labels:list[str] = []
    node_patterns:list[str] = []

    # other variables

    next_node:SeleneNode = None

    nodes_created:list[SeleneNode] = []

    main_tags:list[str] = []

    previous_node:SeleneNode = None
    need_to_be_trained:bool = False
    
    model:SeleneModel = None

    TOKEN = secrets.token_urlsafe(16)

    model_path = f"selene_models_saved/model_{secrets.token_hex(16)}/"

    new_model_version:SeleneModelVersion = None

    if previous_model_version:
        TOKEN = previous_model_version.model.token
        model = previous_model_version.model

        new_model_version = SeleneModelVersion.objects.create(
        version = data_to_train_model['version'],
        model = model,
        is_current_version = False)

    else:
        model_serializer = SeleneModelSerializer(data={
            'name': model_name,
            'model_path': model_path,
            'main_tags': main_tags,
            'token': TOKEN,
        })

        if model_serializer.is_valid():
            model_serializer.save()
            model = model_serializer.instance

            new_model_version = SeleneModelVersion.objects.create(
            version = data_to_train_model['version'],
            model = model,
            is_current_version = True)
        else:
            raise exceptions.ValidationError(model_serializer.errors)


    for i in range(len(data_to_train_model['intents']) - 1, -1, -1):
        node:dict = data_to_train_model['intents'][i]


        node_data_to_serialize = {
            'model_version': new_model_version.pk,
            'tokenized_name': f'{TOKEN}s--s{node["node"]}',
            'patterns': node_patterns,
            'responses': node['responses'],
            'random_response': data_to_train_model['random_response'] if 'random_response' in data_to_train_model else True,
            'do_before': node.get('do_before', {}),
            'do_after': node.get('do_after', {}),
            'token': 'initial_token',
        }

        Print(node_data_to_serialize)

        if next_node_name := node.get('next_node'):
            """
                next node is going to be the name of the node that wants to come next
                the name of the node that is saved is tokenized so we need take the tokenized name, and then
                we can use the node
            """

            Print('nodes_created', nodes_created)
            next_node = next(filter(lambda node: node.name == next_node_name and node.model_version == new_model_version, nodes_created), None)
            node_data_to_serialize['next_node'] = next_node.pk
        

        if node.get('token'):
            # if the node has a token this will mean that there is previous version of this node, so we can copy it
            # and edit it on this new version
            previous_node = SeleneNode.objects.get(token=node['token'], model_version=previous_model_version)

            if previous_node.patterns != node['patterns']:
                need_to_be_trained = True
            else:
                node_patterns = previous_node.patterns

            extra_data_for_serializer = {
                'patterns': node_patterns,
                'previous_node_version': previous_node.pk,
                'token': previous_node.token,
            }

            node_data_to_serialize.update(extra_data_for_serializer)
    

        if need_to_be_trained:
            for pattern in node['patterns']:
                training_sentences.append(pattern)
                node_patterns.append(pattern)

                training_labels.append(node['node'])
            
            if node['node'] not in labels:
                labels.append(node['node'])
                main_tags.append(node['node'])

        
        if nodes_opt:= node.get('next_node_on_option'):
            node_data_to_serialize['next_node_on_option'] = [f'{TOKEN}s--s{nodes_opt[opt]}' for opt in nodes_opt]
        else:
            node_data_to_serialize['next_node_on_option'] = dict()

        node_serializer = SeleneNodeSerializer(data=node_data_to_serialize)

        if node_serializer.is_valid():
            node_serializer.save()
            nodes_created.append(node_serializer.instance)
            if next_node:
                next_node.set_previous_node(node_serializer.instance) 
        else:
            Print('there was an error')
            print(node_serializer.errors)
            raise(exceptions.ValidationError(_(node_serializer.errors)))


    if need_to_be_trained:

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


        model.save(model_path + 'model')


        # to save the fitted tokenizer
        with open(model_path + 'tokenizer.pickle', 'wb') as handle:
            pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
        # to save the fitted label encoder
        with open(model_path + 'label_encoder.pickle', 'wb') as ecn_file:
            pickle.dump(lbl_encoder, ecn_file, protocol=pickle.HIGHEST_PROTOCOL)

    
    return nodes_created


