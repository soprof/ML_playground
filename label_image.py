import tensorflow as tf
import sys
import imghdr
from PIL import Image

# change this as you see fit
image_path = sys.argv[1]

# Read in the image_data
image_data = tf.gfile.FastGFile(image_path, 'rb').read()

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line 
                   in tf.gfile.GFile("heroes3data/retrained_labels.txt")]

# Unpersists graph from file
with tf.gfile.FastGFile("heroes3data/retrained_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

with tf.Session() as sess:
    # Feed the image_data as input to the graph and get first prediction
    softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

    print("type: %s",imghdr.what(image_path))

    if imghdr.what(image_path) == "jpeg":
        predictions = sess.run(softmax_tensor, \
             {'DecodeJpeg/contents:0': image_data})

    if imghdr.what(image_path) == "png":
        im = Image.open(image_path).convert('RGB')
        # bg = Image.new("RGB", im.size, (255,255,255))
        # bg.paste(im,im)
        im.save("result2.jpg")
        image_data = tf.gfile.FastGFile("result2.jpg", 'rb').read()
        predictions = sess.run(softmax_tensor, \
             {'DecodeJpeg/contents:0': image_data})

    # Sort to show labels of first prediction in order of confidence
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

    for node_id in top_k:
        human_string = label_lines[node_id]
        score = predictions[0][node_id]
        print('%s (score = %.5f)' % (human_string, score))