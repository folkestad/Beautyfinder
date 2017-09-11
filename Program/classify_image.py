import numpy
import os
import cv2
import tensorflow as tf
from CNN import *
from HAAR import *
from align_face import *
from performance_measures import *

def classify_image_to_beauty_scale(dirname="Test", file_name="test.jpg", dim1=32, dim2=32):

    # img = get_image(file_name=file_name)
    # haar_img = haar_cascade(dir_name="Test", file_name=file_name)
    aligned_face = align_face(dirname=dirname, filename=file_name)
    resized_image = resize_image(aligned_face, dim1, dim2)

    n_classes = 3

    x = tf.placeholder(tf.float32, [None, resized_image.shape[0], resized_image.shape[1], resized_image.shape[2]])
    y_conv, keep_prob = cnn_model(x, resized_image.shape[0], resized_image.shape[1], resized_image.shape[2], n_classes)
    predict_operation = tf.argmax(y_conv, axis=1)

    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, get_model_path())
        result = sess.run(predict_operation, feed_dict={
            x: [resized_image],
            keep_prob: 1.0
        })
        print("The person in the image is a {} on the beauty scale.".format(result+1))
    
    current_dir = os.path.dirname(__file__)
    file_path = '../Data/{}/{}'.format(dirname, file_name)
    file_rel_path = os.path.join(current_dir, file_path)
    img = cv2.imread(file_rel_path)
    print(type(img), img.shape)
    show_image(img)
    show_image(aligned_face)

def test(test_dir="Processed_Validation", test_labels="Validation_ratings.txt"):

    current_dir = os.path.dirname(__file__)
    file_path = '../Data/Ratings/{}'.format(test_labels)
    file_rel_path = os.path.join(current_dir, file_path)
    labels_file = open(file_rel_path, 'r')
    true_labels = [ int(l.replace("\r\n", "").split(";")[1]) for l in labels_file ]
    print true_labels
    true_labels = [
        (lambda r: 2)(r)
        if r > 8 else
        (lambda r: 1)(r)
        if r > 5 else
        (lambda r: 0)(r)
        for r in true_labels
    ]
    print true_labels
    labels_file.close()
    
    src_dir = '../Data/Datasets/{}'.format(test_dir)
    files = os.walk(src_dir).next()[2]

    predicted_labels = []
    
    n_classes = 3

    x = tf.placeholder(tf.float32, [None, 32, 32, 3])
    y_conv, keep_prob = cnn_model(x, 32, 32, 3, n_classes)
    predict_operation = tf.argmax(y_conv, axis=1)

    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, get_model_path())
        for f in files:
            if f != '.DS_Store':
                aligned_image = cv2.imread(os.path.join(src_dir, f))
                resized_image = resize_image(aligned_image, 32, 32)
                result = sess.run(predict_operation, feed_dict={
                    x: [resized_image],
                    keep_prob: 1.0
                })
                result2 = sess.run(y_conv, feed_dict={
                    x: [resized_image],
                    keep_prob: 1.0
                })
                predicted_labels.append(result)
                print("The person in the image is a {} on the beauty scale. --> {}".format(result, result2))
                show_image(aligned_image)
    
    print(get_classification_report(predicted_labels, true_labels))
    print true_labels
    print predicted_labels


def get_model_path(file_name='model.ckpt'):
    saver = tf.train.Saver()

    current_dir = os.path.dirname(__file__)
    file_path = '../Models/{}'.format(file_name)
    file_rel_path = os.path.join(current_dir, file_path)

    return file_rel_path

def show_image(img, name='Picture'):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_image(file_name):
    current_dir = os.path.dirname(__file__)
    file_path = '../Data/Test/{}'.format(file_name)
    file_rel_path = os.path.join(current_dir, file_path)
    img = cv2.imread(file_rel_path)
    return img

def resize_image(img, dim1, dim2):
    resized_img = cv2.resize(img, (dim2, dim1)) 
    return resized_img

if __name__ == '__main__':
    # classify_image_to_beauty_scale(dirname="Presentation", file_name="donald.jpg", dim1=64, dim2=64)
    test()