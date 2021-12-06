import os
import numpy as np
import cv2
import imutils
import sys

np.set_printoptions(threshold=sys.maxsize)


corner_shapes_map = {
    3: "triangle",
    4: "rectangle",
    5: "pentagon",
    6: "hexagon"
}

model_prediction_map = {
    0: "triangle",
    1: "rectangle",
    2: "circle"
}


def get_corners_in_canvas(canvas):
    detected_contours = cv2.findContours(canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_contours = imutils.grab_contours(detected_contours)

    peri = cv2.arcLength(final_contours[0], True)
    approx = cv2.approxPolyDP(final_contours[0], 0.1 * peri, True)
    return len(approx)


def get_shape_from_model(canvas):
    from keras.models import load_model
    model = load_model(os.path.join(os.getcwd(), "ML", "model.h5"))

    m_input = cv2.resize(canvas, (60, 60))
    m_input = m_input.astype('float32')
    print(m_input.shape)
    # m_input /= 255
    m_input = m_input.reshape(np.prod([60, 60]))

    pred_list = model.predict(m_input.reshape(1, np.prod([60, 60])))[0].tolist()
    print(pred_list)
    max_val = max(pred_list)

    return model_prediction_map[pred_list.index(max_val)]


def get_shape(arr, use_ml=False):
    np_arr = np.array(arr, dtype=np.uint8)

    # Sort by timestamps
    np_arr = np_arr[np.argsort(np_arr[:, 0])]
    contours = np_arr[:, 1:]

    # Hardcoded: Offset x values by 50.
    contours[:, 0] += 50

    # Create a canvas and fill it up for a thresh img
    # canvas = np.full((200, 200), 255, dtype=np.uint8)
    # cv2.fillPoly(canvas, pts=np.int32([contours]), color=0)

    canvas = np.full((200, 200), 0, dtype=np.uint8)
    cv2.fillPoly(canvas, pts=np.int32([contours]), color=255)

    if use_ml:
        return get_shape_from_model(canvas)
    else:
        n_corners = get_corners_in_canvas(canvas)
        if n_corners > 6:
            return "circle"
        if n_corners in corner_shapes_map:
            return corner_shapes_map[n_corners]

    return None

#
# if __name__ == "__main__":
#     inp = [(0, 9.4, 83.4), (1, 10.4, 83.2), (2, 8.8, 83.2), (3, 9, 84), (4, 4.6, 81.6), (5, 1.6, 79.4), (6, -7.8, 75.2),
#      (7, -12.6, 67.6), (8, -14.6, 59), (9, -10.6, 52.4), (10, -3.6, 49.6), (11, 12.4, 51.8), (12, 21.8, 56.4),
#      (13, 28.8, 64.4), (14, 30.4, 73.4), (15, 27.2, 78.6), (16, 19.4, 79.2), (17, 15.4, 82.2), (18, 10.8, 82.4),
#      (19, 10.4, 82), (20, 9.6, 81.6), (21, 10.2, 83.8)]
#
#     print(get_shape(inp, True))
