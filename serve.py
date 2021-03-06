import tensorflow as tf
import os

SAVE_PATH = './save'

MODEL_NAME = 'test'
VERSION = 1
SERVE_PATH = './serve/{}/{}'.format(MODEL_NAME,VERSION)

checkpoint = tf.train.latest_checkpoint(SAVE_PATH)

tf.reset_default_graph()

with tf.Session() as sess:
    saver = tf.train.import_meta_graph(checkpoint+'.meta')
    #get the graph for this session
    graph = tf.get_default_graph()
    sess.run(tf.global_variables_initializer())
    #get the tensors we need
    inputs = graph.get_tensor_by_name('inputs:0')

    # In the tensor variable for prdediction, activation fn is sigmoid, hence the name
    predictions = graph.get_tensor_by_name('prediction/Sigmoid:0')


    #build the tensor info from the above tensor vars
    model_input = tf.saved_model.utils.build_tensor_info(inputs)
    model_output = tf.saved_model.utils.build_tensor_info(predictions)

    #build signature definition (from SavedModelBuilderInstance)

    signature_definition = tf.saved_model.signature_def_utils.build_signature_def(
        inputs = {'inputs':model_input},
        outputs = {'outputs':model_output},
        method_name = tf.saved_model.signature_constants.PREDICT_METHOD_NAME
    )

    #Create SaveModelBuilderInstance using the above info
    builder = tf.saved_model.builder.SavedModelBuilder(SERVE_PATH)

    builder.add_meta_graph_and_variables(
        sess,[tf.saved_model.tag_constants.SERVING],
        signature_def_map = {
            tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:signature_definition
        }
    )

    #Save the model so we can serve it with model server
    builder.save()