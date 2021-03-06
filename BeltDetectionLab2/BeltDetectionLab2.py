import cv2
import time
import numpy as np


def apply_clahe(frame):
    new_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=12.0, tileGridSize=(12, 12))
    new_frame = clahe.apply(new_frame)
    new_frame = cv2.cvtColor(new_frame, cv2.COLOR_GRAY2RGB)
    return new_frame


def is_correct(beltdetected, frame_id):
    return beltdetected and frame_id <= 125 or \
           not beltdetected and frame_id > 125


def main():
    net = cv2.dnn.readNet("YOLOFI2.weights", "YOLOFI.cfg")
    cap = cv2.VideoCapture("test.mp4")

    with open("obj.names", "r")as f:
        layers_names = net.getLayerNames()
        outputlayers = [
            layers_names[i[0]-1]
            for i in net.getUnconnectedOutLayers()
            ]
        start_time = time.time()
        frame_id = 0

        prediction_results = []
        while True:
            _, frame = cap.read()
            frame_id += 1
            beltcornerdetected = False
            beltdetected = False
            if frame is None:
                break
            height, width, channels = frame.shape

            frame = apply_clahe(frame)
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (480, 480), (0, 0, 0),
                                         True, crop=False)
            net.setInput(blob)
            outs = net.forward(outputlayers)

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    if confidence > 0.2:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        if class_id == 1:
                            beltcornerdetected = True
                        elif class_id == 0:
                            beltdetected = True

            prediction_result = is_correct(beltdetected, frame_id)
            prediction_results.append(prediction_result)
            print('Count: %s; Belt: %s; Correct: %s' % (frame_id, beltdetected,
                                                        prediction_result))
            cv2.imshow("Image", frame)
            key = cv2.waitKey(1)
            if key == 27:
                break

        print("Accuracy: {}".format(sum(prediction_results) /
                                    len(prediction_results)))
        finish_time = time.time()
        print('TIME: %s seconds' % round(finish_time-start_time, 2))
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
