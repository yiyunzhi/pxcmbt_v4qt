# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : widget_busy_indicator.py
# ------------------------------------------------------------------------------
#
# File          : widget_busy_indicator.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
# inspired from https://github.com/fbjorn/QtWaitingSpinner/blob/master/pyqtspinner/spinner.py
import math
from ..qtimp import QtGui, QtWidgets, QtCore


class QBusyIndicator(QtWidgets.QWidget):
    """
            center_on_parent: bool = True,
            disable_parent_when_spinning: bool = False,
            modality: Qt.WindowModality = Qt.NonModal,
            roundness: float = 100.0,
            fade: float = 80.0,
            lines: int = 20,
            line_length: int = 10,
            line_width: int = 2,
            radius: int = 10,
            speed: float = math.pi / 2,
            color: QColor = QColor(0, 0, 0),
    """

    def __init__(self, parent: QtWidgets.QWidget, **kwargs) -> None:
        super().__init__(parent)
        self._centerOnParent: bool = kwargs.get('center_on_parent', True)
        self._disableParentWhenBusy: bool = kwargs.get('disable_parent_when_spinning', False)

        self._color: QtGui.QColor = kwargs.get('color', QtGui.QColor(128, 128, 128))
        self._roundness: float = kwargs.get('roundness', 10.0)
        self._minimumTrailOpacity: float = math.pi
        self._trailFadePercentage: float = kwargs.get('fade', 80.0)
        self._revolutionsPerSecond: float = kwargs.get('speed', math.pi / 2)
        self._numberOfLines: int = kwargs.get('lines', 20)
        self._lineLength: int = kwargs.get('line_length', 10)
        self._lineWidth: int = kwargs.get('line_width', 2)
        self._innerRadius: int = kwargs.get('radius', 10)
        self._currentCounter: int = 0
        self._isSpinning: bool = False

        self._timer: QtCore.QTimer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._update_size()
        self._update_timer()
        self.hide()

        self.setWindowModality(kwargs.get('modality', QtCore.Qt.WindowModality.NonModal))
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # pylint: disable=invalid-name
        """
        Paint the WaitingSpinner.
        """
        self._update_position()
        _painter = QtGui.QPainter(self)
        _painter.fillRect(self.rect(), QtGui.Qt.GlobalColor.transparent)
        _painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        _painter.setPen(QtCore.Qt.PenStyle.NoPen)
        for i in range(self._numberOfLines):
            _painter.save()
            _painter.translate(
                self._innerRadius + self._lineLength,
                self._innerRadius + self._lineLength,
            )
            rotate_angle = 360 * i / self._numberOfLines
            _painter.rotate(rotate_angle)
            _painter.translate(self._innerRadius, 0)
            distance = self._line_count_distance_from_primary(
                i, self._currentCounter, self._numberOfLines
            )
            color = self._current_line_color(
                distance,
                self._numberOfLines,
                self._trailFadePercentage,
                self._minimumTrailOpacity,
                self._color,
            )
            _painter.setBrush(color)
            _painter.drawRoundedRect(
                QtCore.QRect(
                    0,
                    -self._lineWidth // 2,
                    self._lineLength,
                    self._lineWidth,
                ),
                self._roundness,
                self._roundness,
                QtCore.Qt.SizeMode.RelativeSize,
            )
            _painter.restore()

    def start(self) -> None:
        """
        Show and start spinning the WaitingSpinner.
        """
        self._update_position()
        self._isSpinning = True
        self.show()

        if self.parentWidget and self._disableParentWhenBusy:
            self.parentWidget().setEnabled(False)

        if not self._timer.isActive():
            self._timer.start()
            self._currentCounter = 0

    def stop(self) -> None:
        """
        Hide and stop spinning the WaitingSpinner.
        """
        self._isSpinning = False
        self.hide()

        if self.parentWidget() and self._disableParentWhenBusy:
            self.parentWidget().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._currentCounter = 0

    @property
    def color(self) -> QtGui.QColor:
        """
        Return color of WaitingSpinner.
        """
        return self._color

    @color.setter
    def color(self, color: QtCore.Qt.GlobalColor = QtCore.Qt.GlobalColor.gray) -> None:
        """
        Set color of WaitingSpinner.
        """
        if isinstance(color, QtGui.QColor):
            self._color = color
        else:
            self._color = QtGui.QColor(color)

    @property
    def roundness(self) -> float:
        """
        Return roundness of WaitingSpinner.
        """
        return self._roundness

    @roundness.setter
    def roundness(self, roundness: float) -> None:
        """
        Set color of WaitingSpinner.
        """
        self._roundness = max(0.0, min(100.0, roundness))

    @property
    def minimum_trail_opacity(self) -> float:
        """
        Return minimum trail opacity of WaitingSpinner.
        """
        return self._minimumTrailOpacity

    @minimum_trail_opacity.setter
    def minimum_trail_opacity(self, minimum_trail_opacity: float) -> None:
        """
        Set minimum trail opacity of WaitingSpinner.
        """
        self._minimumTrailOpacity = minimum_trail_opacity

    @property
    def trail_fade_percentage(self) -> float:
        """
        Return trail fade percentage of WaitingSpinner.
        """
        return self._trailFadePercentage

    @trail_fade_percentage.setter
    def trail_fade_percentage(self, trail: float) -> None:
        """
        Set trail fade percentage of WaitingSpinner.
        """
        self._trailFadePercentage = trail

    @property
    def revolutions_per_second(self) -> float:
        """
        Return revolutions per second of WaitingSpinner.
        """
        return self._revolutionsPerSecond

    @revolutions_per_second.setter
    def revolutions_per_second(self, revolutions_per_second: float) -> None:
        """
        Set revolutions per second of WaitingSpinner.
        """
        self._revolutionsPerSecond = revolutions_per_second
        self._update_timer()

    @property
    def number_of_lines(self) -> int:
        """
        Return number of lines of WaitingSpinner.
        """
        return self._numberOfLines

    @number_of_lines.setter
    def number_of_lines(self, lines: int) -> None:
        """
        Set number of lines of WaitingSpinner.
        """
        self._numberOfLines = lines
        self._currentCounter = 0
        self._update_timer()

    @property
    def line_length(self) -> int:
        """
        Return line length of WaitingSpinner.
        """
        return self._lineLength

    @line_length.setter
    def line_length(self, length: int) -> None:
        """
        Set line length of WaitingSpinner.
        """
        self._lineLength = length
        self._update_size()

    @property
    def line_width(self) -> int:
        """
        Return line width of WaitingSpinner.
        """
        return self._lineWidth

    @line_width.setter
    def line_width(self, width: int) -> None:
        """
        Set line width of WaitingSpinner.
        """
        self._lineWidth = width
        self._update_size()

    @property
    def inner_radius(self) -> int:
        """
        Return inner radius size of WaitingSpinner.
        """
        return self._innerRadius

    @inner_radius.setter
    def inner_radius(self, radius: int) -> None:
        """
        Set inner radius size of WaitingSpinner.
        """
        self._innerRadius = radius
        self._update_size()

    @property
    def is_spinning(self) -> bool:
        """
        Return actual spinning status of WaitingSpinner.
        """
        return self._isSpinning

    def _rotate(self) -> None:
        """
        Rotate the WaitingSpinner.
        """
        self._currentCounter += 1
        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0
        self.update()

    def _update_size(self) -> None:
        """
        Update the size of the WaitingSpinner.
        """
        size = (self._innerRadius + self._lineLength) * 2
        self.setFixedSize(size, size)

    def _update_timer(self) -> None:
        """
        Update the spinning speed of the WaitingSpinner.
        """
        self._timer.setInterval(
            int(1000 / (self._numberOfLines * self._revolutionsPerSecond))
        )

    def _update_position(self) -> None:
        """
        Center WaitingSpinner on parent widget.
        """
        if self.parentWidget() and self._centerOnParent:
            self.move(
                (self.parentWidget().width() - self.width()) // 2,
                (self.parentWidget().height() - self.height()) // 2,
            )

    @staticmethod
    def _line_count_distance_from_primary(current: int, primary: int, total_nr_of_lines: int) -> int:
        """
        Return the amount of lines from _current_counter.
        """
        _distance = primary - current
        if _distance < 0:
            _distance += total_nr_of_lines
        return _distance

    @staticmethod
    def _current_line_color(count_distance: int, total_nr_of_lines: int, trail_fade_perc: float, min_opacity: float, color_input: QtGui.QColor) -> QtGui.QColor:
        """
        Returns the current color for the WaitingSpinner.
        """
        _color = QtGui.QColor(color_input)
        if count_distance == 0:
            return _color
        _min_alpha_f = min_opacity / 100.0
        _distance_threshold = int(
            math.ceil((total_nr_of_lines - 1) * trail_fade_perc / 100.0)
        )
        if count_distance > _distance_threshold:
            _color.setAlphaF(_min_alpha_f)
        else:
            _alpha_diff = _color.alphaF() - _min_alpha_f
            _gradient = _alpha_diff / float(_distance_threshold + 1)
            _result_alpha = _color.alphaF() - _gradient * count_distance
            # If alpha is out of bounds, clip it.
            _result_alpha = min(1.0, max(0.0, _result_alpha))
            _color.setAlphaF(_result_alpha)
        return _color
