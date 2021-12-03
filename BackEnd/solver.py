import numpy as np
import cv2
import imutils


corner_shapes_map = {
    3: "triangle",
    4: "rectangle",
    5: "pentagon",
    6: "hexagon"
}


def get_corners_in_canvas(canvas):
    detected_contours = cv2.findContours(canvas, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_contours = imutils.grab_contours(detected_contours)

    peri = cv2.arcLength(final_contours[0], True)
    approx = cv2.approxPolyDP(final_contours[0], 0.04 * peri, True)
    return len(approx)


def get_shape(arr):
    np_arr = np.array(arr, dtype=np.uint8)

    # Sort by timestamps
    np_arr = np_arr[np.argsort(np_arr[:, 0])]
    contours = np_arr[:, 1:]

    # Hardcoded: Offset x values by 20.
    contours[:, 0] += 20

    # Create a canvas and fill it up for a thresh img
    canvas = np.zeros((200, 200), dtype=np.uint8)
    cv2.fillPoly(canvas, pts=np.int32([contours]), color=255)

    n_corners = get_corners_in_canvas(canvas)

    if n_corners > 6:
        return "circle"

    if n_corners in corner_shapes_map:
        return corner_shapes_map[n_corners]

    return None
