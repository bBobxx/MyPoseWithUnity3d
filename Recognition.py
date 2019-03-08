import numpy as np
import cv2
import math
import socket
import time
import os
import tensorflow as tf
import tensorflow.contrib.slim as slim


UDP_IP = "127.0.0.1"
UDP_PORT = 5065

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

last = []


def dataProcess(im):
    shape = im.shape
    w, h = shape[1], shape[0]
    height, width = 256, 192
    img = im
    ratio = float(height) / float(width)
    if h / float(height) > w / float(width):
        pad_w = int((h / ratio - w) / 2.0)
        pad_h = 0
    else:
        pad_w = 0
        pad_h = int((w * ratio - h) / 2.0)

    mean = np.mean(img, axis=(0,1))
    symmetry, nr_skeleton = [(0, 5), (1, 4), (2, 3), (6, 11), (7, 10), (8, 9), (12, 12), (13, 13)], 14
    bimg = cv2.copyMakeBorder(img, pad_h, pad_h, pad_w, pad_w, borderType=cv2.BORDER_CONSTANT,
                              value=mean.reshape(-1))
    details = [pad_w, pad_h, bimg.shape[1], bimg.shape[0]]
    bimg = bimg - mean
    bimg /= 255.
    img2 = cv2.resize(bimg, (192, 256))
    return np.asarray([img2]).astype(np.float32), details,mean



with tf.Session() as sess:
    tf.global_variables_initializer().run()
    output_graph_def = tf.GraphDef()
    with open('./output_graph.pb', "rb") as f:
        output_graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(output_graph_def, name="")

    input_x = sess.graph.get_tensor_by_name("tower_0/Placeholder:0")
    out_pb = sess.graph.get_tensor_by_name("tower_0/concat_35:0")
    cap = cv2.VideoCapture(0)
    while (1):
        st_time = time.time()
        # get a frame
        ret, frame = cap.read()
        # show a frame
        shape_ori = frame.shape
        img, de, pixel_means = dataProcess(frame)
        out = sess.run(out_pb, feed_dict={input_x: img})
        ht = out
        ht = ht.transpose(0, 3, 1, 2)
        c = (np.random.random((1, 3)) * 0.6 + 0.4).tolist()[0]
        x_c = []
        y_c = []
        sym = [(0, 5), (1, 4), (2, 3),(3,2),(4,1),(5,0), (6, 6), (7, 7), (8, 8), (9, 9), (10, 15), (11, 14), (12, 13),(13,12),(14,11),(15,10)]
        for w in range(16):
            lb = ht[0, w].argmax()
            y, x = np.unravel_index(lb, ht[0, w].shape)
            py = y
            px = x
            x *= 4
            y *= 4
            x *= de[2] / 192
            y *= de[3] / 256
            x -= de[0]
            y -= de[1]
            if ht[0, w, py, px] < 0.8:
                x = -1
                y = -1
            x_c.append(int(x))
            y_c.append(int(y))
        print("FPS is {}".format(1.0/(time.time() - st_time)))
        for w in range(16):
            if x_c[w] < 0 and y_c[w] < 0:
                continue
            cv2.circle(frame, (x_c[w], y_c[w]), 5, (188,143,143),-1)
        s = [1, 2, 6, 6, 3, 4, 7, 6, 9, 8, 11, 12, 7, 7, 13, 14]
        t = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        col = [(255,0,0), (0,0,255), (0,255,0), (0,255,0), (0,0,255), (255,0,0), (255,0,0), (255,0,0), (0,0,255), (0,0,255), (255,255,0), (153,51,250), (0,255,0), (0,255,0), (153,51,250), (255,255,0)]
        for w in range(16):
            if x_c[s[w]] > 0 and x_c[t[w]] > 0:
                cv2.line(frame, (x_c[s[w]],y_c[s[w]]), (x_c[t[w]],y_c[t[w]]), col[w], thickness=3)
        string_send = 'st,'
        for w in range(16):
            string_send += str(x_c[w])+','+str(y_c[w])+','
        string_send += 'end'
        sock.sendto( string_send.encode(), (UDP_IP, UDP_PORT) )
        cv2.imshow('out', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
             break
    cap.release()
    cv2.destroyAllWindows()

   
