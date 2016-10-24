import cv2
import os


def _full_path(rel_path):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        return os.path.join(__location__, rel_path)


class FaceBlurCapture(object):
    """
    Blurs any faces in the frame captured by VideoCapture
    cv2.VideoCapture is a C extension, and non-subclass-able, so we encapsulate it instead
    """
    # Load cascade statically
    cascade_file = _full_path("haarcascade_frontalface_alt.xml")
    cascade = cv2.CascadeClassifier(cascade_file)
    if cascade.empty():
        print "Error loading cascade files"
        raise Exception()

    @staticmethod
    def detect(img, cascade):
        rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4,
                                         minSize=(30, 30),
                                         flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
        if len(rects) == 0:
            return []
        rects[:, 2:] += rects[:, :2]
        return rects

    @staticmethod
    def filter_frame(image):
        gray = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = FaceBlurCapture.detect(gray, FaceBlurCapture.cascade)
        for face in faces:
            x0, y0, x1, y1 = face
            sub_face = image[y0:y1, x0:x1]
            sub_face = cv2.blur(sub_face, (73, 73))
            image[y0:y1, x0:x1] = sub_face
        return image

    def __init__(self):
        self.capture = cv2.VideoCapture()

    def read(self):
        retval, frame = self.capture.read()
        if not retval:
            return retval, None
        filtered = FaceBlurCapture.filter_frame(frame)
        return retval, filtered

    def open(self, device_or_file):
        return self.capture.open(device_or_file)

    def isOpened(self):
        return self.capture.isOpened()

    def release(self):
        return self.capture.release()

    def get(self, propId):
        return self.capture.get(propId)

    def set(self, propId, value):
        return self.capture.set(propId, value)