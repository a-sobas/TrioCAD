from PyQt5.QtCore import QRectF


class RectF(QRectF):

    def __init__(self, *args):
        super(RectF, self).__init__(*args)

    @classmethod
    def rect_from_center(cls, center, dx, dy):

        p1_x = center.x() - dx/2
        p1_y = center.y() - dy/2

        return cls(p1_x, p1_y, dx, dy)
