
# #### Importing Libraries

import os.path
import tensorflow as tf
import helper
import warnings
from distutils.version import LooseVersion
import project_tests as tests

print('All Modules Imported!')


# Check TensorFlow Version
assert LooseVersion(tf.__version__) >= LooseVersion('1.0'), 'Please use TensorFlow version 1.0 or newer.  You are using {}'.format(tf.__version__)
print('TensorFlow Version: {}'.format(tf.__version__))

# Check for a GPU
if not tf.test.gpu_device_name():
    warnings.warn('No GPU found. Please use a GPU to train your neural network.')
else:
    print('Default GPU Device: {}'.format(tf.test.gpu_device_name()))


# #### Test VGG Data

def load_vgg(sess, vgg_path):
    """
    Load Pretrained VGG Model into TensorFlow.
    :param sess: TensorFlow Session
    :param vgg_path: Path to vgg folder, containing "variables/" and "saved_model.pb"
    :return: Tuple of Tensors from VGG model (image_input, keep_prob, layer3_out, layer4_out, layer7_out)
    """
    # TODO: Implement function
    #   Use tf.saved_model.loader.load to load the model and weights
        
    vgg_tag = 'vgg16'
    vgg_input_tensor_name = 'image_input:0'
    vgg_keep_prob_tensor_name = 'keep_prob:0'
    vgg_layer3_out_tensor_name = 'layer3_out:0'
    vgg_layer4_out_tensor_name = 'layer4_out:0'
    vgg_layer7_out_tensor_name = 'layer7_out:0'
    
    tf.saved_model.loader.load(sess,[vgg_tag],vgg_path)
    
    default_graph = tf.get_default_graph()
    
    vgg_input = default_graph.get_tensor_by_name(vgg_input_tensor_name)
    vgg_dropout = default_graph.get_tensor_by_name(vgg_keep_prob_tensor_name)
    vgg_l3 = default_graph.get_tensor_by_name(vgg_layer3_out_tensor_name)
    vgg_l4 = default_graph.get_tensor_by_name(vgg_layer4_out_tensor_name)
    vgg_l7 = default_graph.get_tensor_by_name(vgg_layer7_out_tensor_name)
    
    return vgg_input, vgg_dropout, vgg_l3, vgg_l4, vgg_l7

tests.test_load_vgg(load_vgg, tf)


# #### Test FCN8

def layers(vgg_layer3_out, vgg_layer4_out, vgg_layer7_out, num_classes):
    """
    Create the layers for a fully convolutional network.  
    Build skip-layers using the vgg layers.
    :param vgg_layer7_out: TF Tensor for VGG Layer 3 output
    :param vgg_layer4_out: TF Tensor for VGG Layer 4 output
    :param vgg_layer3_out: TF Tensor for VGG Layer 7 output
    :param num_classes: Number of classes to classify
    :return: The Tensor for the last layer of output
    """
    #print(vgg_layer7_out.shape)
    #print(vgg_layer4_out.shape)
    #print(vgg_layer3_out.shape)      
    #print(num_classes)
    # TODO: Implement function
    Conv_1x1 = tf.layers.conv2d(vgg_layer7_out, 512, 1, 1)
    #print(Conv_1x1.shape)
    T_Conv1 = tf.layers.conv2d_transpose(Conv_1x1, 512, 2, 2, 'SAME')
    Skip_l4 = tf.add(T_Conv1,vgg_layer4_out)
    #print(Skip_l4.shape)
    T_Conv2 = tf.layers.conv2d_transpose(Skip_l4, 256, 2, 2, 'SAME')
    Skip_l3 = tf.add(T_Conv2,vgg_layer3_out)
    #print(Skip_l3.shape)
    T_Conv3 = tf.layers.conv2d_transpose(Skip_l3, num_classes, 8, 8, 'SAME')
    #print(T_Conv3.shape)
    
    
    return T_Conv3
tests.test_layers(layers)


# #### Loss and Optimizer


def optimize(nn_last_layer, correct_label, learning_rate, num_classes):
    """
    Build the TensorFLow loss and optimizer operations.
    :param nn_last_layer: TF Tensor of the last layer in the neural network
    :param correct_label: TF Placeholder for the correct label image
    :param learning_rate: TF Placeholder for the learning rate
    :param num_classes: Number of classes to classify
    :return: Tuple of (logits, train_op, cross_entropy_loss)
    """
    # TODO: Implement function
    #print(nn_last_layer.shape)
    #print(correct_label.shape)
    
    logits = tf.reshape(nn_last_layer, (-1, num_classes))
    labels = tf.reshape(correct_label, (-1, num_classes))
    #print(logits.shape)
    #print(labels.shape)
    
    cost=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=labels))
    optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost)    
    
    
    return logits, optimizer, cost
tests.test_optimize(optimize)


# #### Training the Network

def train_nn(sess, epochs, batch_size, get_batches_fn, train_op, cross_entropy_loss, input_image,
             correct_label, keep_prob, learning_rate):
    
    """
    Train neural network and print out the loss during training.
    :param sess: TF Session
    :param epochs: Number of epochs
    :param batch_size: Batch size
    :param get_batches_fn: Function to get batches of training data.  
     Call using get_batches_fn(batch_size)
    :param train_op: TF Operation to train the neural network
    :param cross_entropy_loss: TF Tensor for the amount of loss
    :param input_image: TF Placeholder for input images
    :param correct_label: TF Placeholder for label images
    :param keep_prob: TF Placeholder for dropout keep probability
    :param learning_rate: TF Placeholder for learning rate
    """
    # TODO: Implement function
    for epoch in range(epochs):
        for image, label in get_batches_fn(batch_size):
            _, loss = sess.run([train_op, cross_entropy_loss],
            feed_dict = {input_image: image, correct_label: label, keep_prob: 0.5, learning_rate: 0.001})
          
            
        print('Epoch {:>2}: Loss: {:>10.4f}'.format(epoch+1, loss))
    
    
tests.test_train_nn(train_nn)


# #### Run


def run():
    num_classes = 2
    image_shape = (160, 576)
    data_dir = './data'
    runs_dir = './runs'
    tests.test_for_kitti_dataset(data_dir)

    # Download pretrained vgg model
    helper.maybe_download_pretrained_vgg(data_dir)
    correct_label = tf.placeholder(tf.float32, shape = [None, image_shape[0], image_shape[1], num_classes])
    learning_rate = tf.placeholder(tf.float32)
    epochs = 40
    batch_size = 16

    # OPTIONAL: Train and Inference on the cityscapes dataset instead of the Kitti dataset.
    # You'll need a GPU with at least 10 teraFLOPS to train on.
    #  https://www.cityscapes-dataset.com/

    with tf.Session() as sess:
        # Path to vgg model
        vgg_path = os.path.join(data_dir, 'vgg')
        # Create function to get batches
        get_batches_fn = helper.gen_batch_function(os.path.join(data_dir, 'data_road/training'), image_shape)
        

        # OPTIONAL: Augment Images for better results
        #  https://datascience.stackexchange.com/questions/5224/how-to-prepare-augment-images-for-neural-network

        # TODO: Build NN using load_vgg, layers, and optimize function
        vgg_input, vgg_dropout, vgg_l3, vgg_l4, vgg_l7 = load_vgg(sess, vgg_path)
        
        out_layer = layers(vgg_l3, vgg_l4, vgg_l7, num_classes)
        
        logits, optimizer, cost = optimize(out_layer, correct_label, learning_rate, num_classes)
        
        
        # TODO: Train NN using the train_nn function
        sess.run(tf.global_variables_initializer())
        train_nn(sess, epochs, batch_size, get_batches_fn, optimizer, cost, vgg_input,
             correct_label, vgg_dropout, learning_rate)
        

        # TODO: Save inference data using helper.save_inference_samples
        helper.save_inference_samples(runs_dir, data_dir, sess, image_shape, logits, vgg_dropout, vgg_input)

        # OPTIONAL: Apply the trained model to a video
        
if __name__ == '__main__':
    run()