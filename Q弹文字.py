import sys
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PySide6.QtCore import (QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                            QSequentialAnimationGroup, QPauseAnimation, QByteArray, Qt, QTimer, QRectF)
from PySide6.QtGui import (QColor, QFont, QPainter, QPainterPath, QConicalGradient, QPen, QBrush)

class AnimatedTextItem(QGraphicsTextItem):
    def __init__(self, text):
        super().__init__(text)
        self._scale = 1.0
        self._gradient_rect = None
        self._gradient_angle = 0.0

    def setGradient(self, rect, angle):
        self._gradient_rect = rect
        self._gradient_angle = angle
        self.update()

    def paint(self, painter, option, widget):
        font = self.font()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(font)
        path = QPainterPath()
        path.addText(0, font.pointSizeF()*1.5, font, self.toPlainText())

        # 用全体渐变rect和angle
        if self._gradient_rect is not None:
            center = self._gradient_rect.center()
            gradient = QConicalGradient(center, self._gradient_angle)
        else:
            rect = path.boundingRect()
            center = rect.center()
            gradient = QConicalGradient(center, self._gradient_angle)

        # 彩虹色
        gradient.setColorAt(0, QColor(255, 167, 69, 255))
        gradient.setColorAt(0.125, QColor(254, 134, 159, 255))
        gradient.setColorAt(0.25, QColor(239, 122, 200, 255))
        gradient.setColorAt(0.375, QColor(160, 131, 237, 255))
        gradient.setColorAt(0.5, QColor(67, 174, 255, 255))
        gradient.setColorAt(0.625, QColor(160, 131, 237, 255))
        gradient.setColorAt(0.75, QColor(239, 122, 200, 255))
        gradient.setColorAt(0.875, QColor(254, 134, 159, 255))
        gradient.setColorAt(1, QColor(255, 167, 69, 255))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        painter.restore()

class GraphicsBounceText(QGraphicsView):
    def __init__(self):
        super().__init__()
        self._gradient_rect = None
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setWindowTitle("Q弹统一渐变文字")
        self.setGeometry(100, 100, 1000, 500)

        self.text = "Q弹+颜色渐变文字🚀"
        self.items = []
        self.init_font_size = 80
        self.scene_margin = 40

        self.createTextItems()
        self.anim_group = QParallelAnimationGroup()
        self.createAnimations()
        self.anim_group.setLoopCount(-1)
        self.anim_group.start()
        self._gradient_angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGradients)
        self.timer.start(20)

        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def createTextItems(self):
        for item in self.items:
            self.scene.removeItem(item)
        self.items.clear()

        font = QFont("Arial", self.init_font_size)
        x = 0
        y = self.scene_margin
        for char in self.text:
            item = AnimatedTextItem(char)
            item.setFont(font)
            rect = item.boundingRect()
            item.setTransformOriginPoint(rect.center())
            item.setPos(x, y)
            item.setScale(1.0)
            self.scene.addItem(item)
            self.items.append(item)
            x += item.boundingRect().width()
        total_width = sum(item.boundingRect().width() for item in self.items)
        scene_height = self.init_font_size * 2  + self.scene_margin * 2
        self.setSceneRect(0, 0, total_width, scene_height)
        # 统一渐变boundingRect
        self._gradient_rect = QRectF(0, y, total_width, self.init_font_size)

    def createAnimations(self):
        self.anim_group.clear()
        for i, item in enumerate(self.items):
            char_anim = QSequentialAnimationGroup()
            delay = QPauseAnimation(i * 200)
            char_anim.addAnimation(delay)

            parallel_group = QParallelAnimationGroup()

            # 跳跃动画
            anim_y = QPropertyAnimation(item, QByteArray(b"y"))
            anim_y.setDuration(1000)
            start_y = item.y()
            anim_y.setStartValue(start_y)
            anim_y.setKeyValueAt(0.5, start_y - 1.2 * self.init_font_size)
            anim_y.setEndValue(start_y)
            anim_y.setEasingCurve(QEasingCurve.Type.OutBounce)

            # 缩放动画
            anim_scale = QPropertyAnimation(item, QByteArray(b"scale"))
            anim_scale.setDuration(1000)
            anim_scale.setStartValue(1.0)
            anim_scale.setKeyValueAt(0.3, 0.4)
            anim_scale.setEndValue(1.0)
            anim_scale.setEasingCurve(QEasingCurve.Type.OutBounce)

            parallel_group.addAnimation(anim_y)
            parallel_group.addAnimation(anim_scale)
            char_anim.addAnimation(parallel_group)
            self.anim_group.addAnimation(char_anim)

    def updateGradients(self):
        self._gradient_angle = (self._gradient_angle + 1) % 360
        for item in self.items:
            item.setGradient(self._gradient_rect, self._gradient_angle)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphicsBounceText()
    window.show()
    sys.exit(app.exec())
